# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class VendorBillClaudeCodeImportWizard(models.TransientModel):
    """
    Wizard opened from the "AI Import" button on a draft vendor bill.

    Lets the user upload a PDF/PNG and pick a backend, then creates a
    ``vendor.bill.claude.code.job`` and enqueues it via ``queue_job`` so the
    extraction runs in the background instead of blocking the web request.
    """

    _name = "vendor.bill.claude.code.import.wizard"
    _description = "Vendor Bill Claude Code Import Wizard"

    move_id = fields.Many2one(
        string="Vendor Bill",
        comodel_name="account.move",
        required=True,
        readonly=True,
        help="Draft vendor bill the extracted data will be written back to.",
    )
    backend_id = fields.Many2one(
        string="Backend",
        comodel_name="vendor.bill.claude.code.backend",
        required=True,
        help="Backend configuration used to call the claude-code extraction "
        "service.",
    )
    data_file = fields.Binary(
        string="Vendor Bill File",
        required=True,
        help="PDF or image (PNG/JPEG/WEBP/HEIC) of the vendor bill to " "extract.",
    )
    filename = fields.Char(
        string="Filename",
        help="Original filename of the uploaded vendor bill file.",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if "backend_id" in fields_list and not res.get("backend_id"):
            move_id = res.get("move_id") or self.env.context.get("default_move_id")
            if move_id:
                move = self.env["account.move"].browse(move_id)
                backend = move.journal_id.default_claude_code_backend_id
                if backend:
                    res["backend_id"] = backend.id
        return res

    def action_import(self):
        for record in self.sudo():
            result = record._import()
        return result

    def _import(self):
        self.ensure_one()
        attachment = self.env["ir.attachment"].sudo().create(self._prepare_attachment())
        job = (
            self.env["vendor.bill.claude.code.job"]
            .sudo()
            .create(self._prepare_job(attachment))
        )
        self._set_main_attachment(attachment)
        job.action_enqueue()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("AI Import"),
                "message": _(
                    "Vendor bill file '%s' queued for AI extraction. It is "
                    "processed in the background; you can follow its progress "
                    "from the vendor bill."
                )
                % (self.filename or ""),
                "type": "success",
                "sticky": False,
                "next": {"type": "ir.actions.act_window_close"},
            },
        }

    def _set_main_attachment(self, attachment):
        """Show the uploaded file in the vendor bill's document preview panel so
        the extracted data can be checked against the source document."""
        self.ensure_one()
        if self.move_id.message_main_attachment_id:
            return
        self.move_id.sudo().with_context(tracking_disable=True).write(
            {"message_main_attachment_id": attachment.id}
        )

    def _prepare_attachment(self):
        self.ensure_one()
        return {
            "name": self.filename or "vendor_bill",
            "datas": self.data_file,
            "type": "binary",
            "res_model": "account.move",
            "res_id": self.move_id.id,
        }

    def _prepare_job(self, attachment):
        self.ensure_one()
        return {
            "attachment_id": attachment.id,
            "source_filename": self.filename,
            "move_id": self.move_id.id,
            "backend_id": self.backend_id.id,
        }
