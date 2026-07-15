# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    default_claude_code_backend_id = fields.Many2one(
        string="Default Vendor Bill AI Backend",
        comodel_name="vendor.bill.claude.code.backend",
        help=(
            "Default claude-code backend pre-selected when importing vendor "
            "bills via this journal. Users can still override it per-import "
            "in the AI Import wizard."
        ),
    )
