# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class ImportVendorBillClaudeCode(models.TransientModel):
    """
    Wizard opened from the "AI Import" button on a draft vendor bill.

    Lets the user upload a PDF/PNG and pick a backend, then creates a
    ``vendor.bill.claude.code.job`` and enqueues it via ``queue_job`` so the
    extraction runs in the background instead of blocking the web request.
    """

    _name = "import_vendor_bill_claude_code"
    _description = "Import Vendor Bill Claude Code"

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
        """Preselect the journal's default backend when opened from a bill.

        :param fields_list: field names requested by the client
        :return: dict of default values
        """
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
        """Create the attachment and job, then queue the AI extraction.

        :return: an ``ir.actions.client`` display_notification dict
        """
        for record in self.sudo():
            result = record._import()
        return result

    def _import(self):
        """Attach the uploaded file, create the job, and enqueue it.

        Side effect: creates an ``ir.attachment`` linked to ``move_id``,
        creates a ``vendor.bill.claude.code.job``, sets it as the vendor
        bill's main attachment, and calls ``action_enqueue`` on the job.

        :return: an ``ir.actions.client`` display_notification dict
        """
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
        """Show the uploaded file in the vendor bill's preview panel.

        Only sets it when the vendor bill has no main attachment yet, so
        the extracted data can be checked against the source document
        without overwriting an existing one.

        :param attachment: the ``ir.attachment`` just created for the
            uploaded vendor bill file
        """
        self.ensure_one()
        if self.move_id.message_main_attachment_id:
            return
        self.move_id.sudo().with_context(tracking_disable=True).write(
            {"message_main_attachment_id": attachment.id}
        )

    def _prepare_attachment(self):
        """Build the ``ir.attachment`` values for the uploaded file.

        Extension point: override to change how the uploaded vendor bill
        file is stored.

        :return: dict of ``ir.attachment`` values
        """
        self.ensure_one()
        return {
            "name": self.filename or "vendor_bill",
            "datas": self.data_file,
            "type": "binary",
            "res_model": "account.move",
            "res_id": self.move_id.id,
        }

    def _prepare_job(self, attachment):
        """Build the ``vendor.bill.claude.code.job`` values to create.

        Extension point: override to add fields to the job created for
        each import.

        :param attachment: the ``ir.attachment`` holding the uploaded file
        :return: dict of ``vendor.bill.claude.code.job`` values
        """
        self.ensure_one()
        return {
            "attachment_id": attachment.id,
            "source_filename": self.filename,
            "move_id": self.move_id.id,
            "backend_id": self.backend_id.id,
        }
