# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import json
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class VendorBillClaudeCodeJob(models.Model):
    """
    Tracks one asynchronous vendor bill extraction request sent to a
    Vendor Bill Claude Code backend.

    A job is created by the ``vendor.bill.claude.code.import.wizard`` when a
    user clicks "AI Import" on a draft vendor bill, then processed in the
    background via ``queue_job`` (``_run``) since a single extraction can
    take up to the backend's configured timeout. Progress and failures are
    tracked on ``state`` / ``error_message`` so users can monitor and retry
    imports without blocking the web request.
    """

    _name = "vendor.bill.claude.code.job"
    _description = "Vendor Bill Claude Code Import Job"
    _order = "create_date desc"

    name = fields.Char(
        string="Reference",
        required=True,
        readonly=True,
        copy=False,
        default="New",
        help="Sequential reference of this import job.",
    )
    attachment_id = fields.Many2one(
        string="Vendor Bill File",
        comodel_name="ir.attachment",
        required=True,
        readonly=True,
        help="Original vendor bill file uploaded by the user and sent to the "
        "claude-code extraction service.",
    )
    source_filename = fields.Char(
        string="Filename",
        readonly=True,
        help="Original filename of the uploaded vendor bill file.",
    )
    move_id = fields.Many2one(
        string="Vendor Bill",
        comodel_name="account.move",
        required=True,
        readonly=True,
        ondelete="cascade",
        help="Draft vendor bill (account.move, in_invoice) the extracted "
        "data is written back to.",
    )
    backend_id = fields.Many2one(
        string="Backend",
        comodel_name="vendor.bill.claude.code.backend",
        required=True,
        readonly=True,
        help="Backend configuration used to call the claude-code extraction "
        "service.",
    )
    state = fields.Selection(
        string="Status",
        selection=[
            ("draft", "Draft"),
            ("queued", "Queued"),
            ("processing", "Processing"),
            ("done", "Done"),
            ("need_review", "Need Review"),
            ("failed", "Failed"),
        ],
        default="draft",
        required=True,
        readonly=True,
        copy=False,
        help=(
            "Job status: "
            "Draft = not yet queued, "
            "Queued = waiting for a queue_job worker, "
            "Processing = currently calling the extraction service, "
            "Done = vendor bill written successfully, "
            "Need Review = written but low confidence / unresolved data, "
            "Failed = the service call or write raised an error."
        ),
    )
    external_id = fields.Char(
        string="Extraction ID",
        readonly=True,
        copy=False,
        help="ID of the extraction record on the service "
        "(VendorBillExtractionRead.id).",
    )
    external_status = fields.Char(
        string="Extraction Status",
        readonly=True,
        copy=False,
        help="Raw status returned by the service (ok / need_review / failed).",
    )
    error_message = fields.Text(
        string="Error Message",
        readonly=True,
        copy=False,
        help="Error raised while calling the service or writing the "
        "extracted vendor bill.",
    )
    response_json = fields.Text(
        string="Raw Response",
        readonly=True,
        copy=False,
        help="Raw JSON response from the service, kept for troubleshooting.",
    )

    @api.model
    def create(self, vals):
        if vals.get("name", "New") in (False, "New"):
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("vendor.bill.claude.code.job")
                or "New"
            )
        return super().create(vals)

    def action_enqueue(self):
        for record in self.sudo():
            record._enqueue()

    def _enqueue(self):
        self.ensure_one()
        self.write({"state": "queued", "error_message": False})
        self.with_delay(
            description=_("Import vendor bill via claude-code: %s")
            % (self.source_filename or self.name)
        )._run()

    def action_retry(self):
        for record in self.sudo():
            record._retry()

    def _retry(self):
        self.ensure_one()
        if self.state not in ("failed", "need_review"):
            error_message = (
                _(
                    """
Context: Retry vendor bill claude-code import job
Database ID: %s
Problem: Job is in state '%s', only 'Failed' or 'Need Review' jobs can be \
retried
Solution: Wait for the current job to finish, or check its result
"""
                )
                % (self.id, self.state)
            )
            raise UserError(error_message)
        self._enqueue()

    def action_open_move(self):
        for record in self.sudo():
            result = record._open_move()
        return result

    def _open_move(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_move_in_invoice_type"
        )
        form = self.env.ref("account.view_move_form")
        action["views"] = [(form.id, "form")]
        action["view_mode"] = "form"
        action["res_id"] = self.move_id.id
        return action

    def _run(self):
        """Call the claude-code service and write the result onto the move.

        Meant to be invoked via ``with_delay()``. Never re-raises: any
        failure is caught and recorded on ``state`` / ``error_message`` so
        the job can be inspected and retried from the UI.
        """
        self.ensure_one()
        self.write({"state": "processing"})
        try:
            data_file = base64.b64decode(self.attachment_id.datas or b"")
            filename = self.source_filename or self.attachment_id.name or "vendor_bill"

            response_json = self.backend_id._call_service(data_file, filename)
            move_vals, meta = self.backend_id._transform_result(response_json)

            currency_id = self._resolve_currency(meta.get("currency_code"))
            if currency_id:
                move_vals["currency_id"] = currency_id

            if not move_vals.get("partner_id"):
                partner_id = self._resolve_partner(
                    meta.get("partner_vat"), meta.get("partner_name")
                )
                if partner_id:
                    move_vals["partner_id"] = partner_id

            self.move_id.with_context(check_move_validity=False).write(move_vals)
            self._post_import_note(meta, response_json)

            external_status = meta.get("external_status")
            state = "done"
            if (
                external_status == "need_review"
                or meta.get("warnings")
                or not move_vals.get("partner_id")
            ):
                state = "need_review"

            self.write(
                {
                    "state": state,
                    "external_id": meta.get("external_id"),
                    "external_status": external_status,
                    "response_json": json.dumps(response_json),
                    "error_message": False,
                }
            )
        except Exception as exc:  # noqa: BLE001 - job must never propagate
            _logger.exception(
                "vendor bill claude-code import job %s failed",
                self.id,
            )
            self.write(
                {
                    "state": "failed",
                    "error_message": str(exc),
                }
            )

    def _resolve_currency(self, currency_code):
        """Resolve a currency code (e.g. 'IDR') to a ``res.currency`` id, or
        ``False`` when unknown so the move keeps the company default."""
        self.ensure_one()
        if not currency_code:
            return False
        currency = self.env["res.currency"].search(
            [("name", "=", currency_code)], limit=1
        )
        return currency.id if currency else False

    def _resolve_partner(self, partner_vat, partner_name):
        """Best-effort resolve a vendor to a ``res.partner`` id by VAT first,
        then by name, only when the match is unique."""
        self.ensure_one()
        partner_model = self.env["res.partner"]
        if partner_vat:
            partner = partner_model.search([("vat", "=", partner_vat)])
            if len(partner) == 1:
                return partner.id
        if partner_name:
            partner = partner_model.search([("name", "=", partner_name)])
            if len(partner) == 1:
                return partner.id
        return False

    def _post_import_note(self, meta, response_json):
        """Post extraction warnings and unresolved-line hints to the move
        chatter so a user can complete the import manually."""
        self.ensure_one()
        lines = []
        matched = meta.get("matched")
        lines.append(
            _("Vendor bill imported via claude-code (job %s, matching: %s).")
            % (self.name, _("on") if matched else _("off"))
        )
        for warning in meta.get("warnings") or []:
            lines.append(_("Warning: %s") % warning)

        result = response_json.get("result") or {}
        bill = result.get("bill") or {}
        for index, line in enumerate(bill.get("lines") or [], start=1):
            hints = []
            if line.get("product_id") is None and line.get("product_hint"):
                hints.append(_("product: %s") % line["product_hint"])
            if line.get("account_id") is None and line.get("account_hint"):
                hints.append(_("account: %s") % line["account_hint"])
            if not line.get("tax_ids") and line.get("tax_hint"):
                hints.append(_("tax: %s") % line["tax_hint"])
            if hints:
                lines.append(
                    _("Line %d (%s) needs review — %s")
                    % (index, line.get("name") or "N/A", "; ".join(hints))
                )
        if meta.get("partner_vat") and not self.move_id.partner_id:
            lines.append(_("Vendor VAT hint: %s") % meta["partner_vat"])
        if meta.get("partner_name") and not self.move_id.partner_id:
            lines.append(_("Vendor name hint: %s") % meta["partner_name"])

        self.move_id.message_post(body="<br/>".join(lines))
