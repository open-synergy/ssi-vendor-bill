# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class VendorBillLine(models.Model):
    """
    Propagates the parent ``vendor_bill``'s Operating Unit to the journal
    item created for this detail line (``mixin.account_move_single_line``
    from ``ssi_accounting_entry_mixin``).
    """

    _name = "vendor_bill.line"
    _inherit = [
        "vendor_bill.line",
    ]

    def _prepare_standard_ml(self):
        self.ensure_one()
        res = super()._prepare_standard_ml()
        res.update(
            {
                "operating_unit_id": self.vendor_bill_id.operating_unit_id.id,
            }
        )
        return res
