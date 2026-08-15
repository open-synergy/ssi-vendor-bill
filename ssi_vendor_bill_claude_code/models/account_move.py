# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class AccountMove(models.Model):
    """
    Adds the "AI Import" entry point and claude-code job tracking to
    vendor bills (``move_type = 'in_invoice'``).

    Opens the ``import_vendor_bill_claude_code`` wizard from a draft
    vendor bill and exposes the AI extraction jobs linked to it via a
    smart button.
    """

    _inherit = "account.move"

    claude_code_job_ids = fields.One2many(
        string="Claude Code Import Jobs",
        comodel_name="vendor.bill.claude.code.job",
        inverse_name="move_id",
        readonly=True,
        help="AI extraction job(s) that wrote data onto this vendor bill. "
        "Read-only; jobs are created and processed from the AI Import wizard.",
    )
    claude_code_job_count = fields.Integer(
        string="Claude Code Import Job Count",
        compute="_compute_claude_code_job_count",
        help="Number of claude-code AI import jobs linked to this vendor bill.",
    )

    @api.depends("claude_code_job_ids")
    def _compute_claude_code_job_count(self):
        """Count the claude-code import jobs linked to this vendor bill."""
        for record in self:
            record.claude_code_job_count = len(record.claude_code_job_ids)

    def action_open_vendor_bill_claude_code_wizard(self):
        """Open the AI Import wizard for this draft vendor bill.

        :return: an ``ir.actions.act_window`` dict opening
            ``import_vendor_bill_claude_code`` with this bill preset
        """
        for record in self.sudo():
            result = record._open_vendor_bill_claude_code_wizard()
        return result

    def _open_vendor_bill_claude_code_wizard(self):
        """Build the act_window dict for the AI Import wizard.

        :return: an ``ir.actions.act_window`` dict targeting
            ``import_vendor_bill_claude_code``
        """
        self.ensure_one()
        return {
            "name": _("AI Import Vendor Bill"),
            "type": "ir.actions.act_window",
            "res_model": "import_vendor_bill_claude_code",
            "view_mode": "form",
            "target": "new",
            "context": {"default_move_id": self.id},
        }

    def action_open_claude_code_jobs(self):
        """Open the AI import jobs linked to this vendor bill.

        :return: an ``ir.actions.act_window`` dict listing
            ``vendor.bill.claude.code.job`` filtered on this bill
        """
        for record in self.sudo():
            result = record._open_claude_code_jobs()
        return result

    def _open_claude_code_jobs(self):
        """Build the act_window dict for this bill's claude-code jobs.

        :return: an ``ir.actions.act_window`` dict, domain-restricted to
            jobs whose ``move_id`` is this record
        """
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "ssi_vendor_bill_claude_code.vendor_bill_claude_code_job_action"
        )
        action["domain"] = [("move_id", "=", self.id)]
        action["context"] = {}
        return action
