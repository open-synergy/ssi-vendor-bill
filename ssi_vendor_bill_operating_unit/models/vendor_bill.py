# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class VendorBill(models.Model):
    """
    Adds Operating Unit support to ``vendor_bill``.

    ``operating_unit_id`` itself comes from ``mixin.single_operating_unit``
    (default: the creating user's default operating unit); this override
    only locks its editability to the draft state and propagates it to the
    accounting entry created on ``action_open`` (``mixin.account_move`` /
    ``mixin.account_move_single_line`` from ``ssi_accounting_entry_mixin``).
    """

    _name = "vendor_bill"
    _inherit = [
        "vendor_bill",
        "mixin.single_operating_unit",
    ]

    operating_unit_id = fields.Many2one(
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    def _prepare_standard_move(self):
        self.ensure_one()
        res = super()._prepare_standard_move()
        res.update(
            {
                "operating_unit_id": self.operating_unit_id.id,
            }
        )
        return res

    def _prepare_standard_ml(self):
        self.ensure_one()
        res = super()._prepare_standard_ml()
        res.update(
            {
                "operating_unit_id": self.operating_unit_id.id,
            }
        )
        return res
