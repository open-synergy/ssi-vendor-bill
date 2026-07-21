# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class VendorBillLine(models.Model):
    """
    Detail line of a vendor bill.

    Represents one product/service being billed together with its
    accounting distribution (account, analytic account, usage) and
    applicable taxes. Quantity, price, and subtotal computation are
    provided by ``mixin.product_line_account``; this model only adds
    the link back to its parent ``vendor_bill`` and a handful of
    convenience fields mirrored from the header.
    """

    _name = "vendor_bill.line"
    _description = "Vendor Bill - Line"
    _inherit = [
        "mixin.product_line_account",
    ]
    _order = "vendor_bill_id, sequence, id"

    vendor_bill_id = fields.Many2one(
        string="# Vendor Bill",
        comodel_name="vendor_bill",
        required=True,
        ondelete="cascade",
    )

    # Convenience fields mirrored from the header, following the pattern
    # of employee_business_trip.per_diem / employee_business_trip.tax.
    currency_id = fields.Many2one(
        related="vendor_bill_id.currency_id",
        compute_sudo=True,
    )
    company_id = fields.Many2one(
        related="vendor_bill_id.company_id",
        compute_sudo=True,
    )
    company_currency_id = fields.Many2one(
        related="vendor_bill_id.company_currency_id",
        compute_sudo=True,
    )
    partner_id = fields.Many2one(
        related="vendor_bill_id.partner_id",
        compute_sudo=True,
    )
    pricelist_id = fields.Many2one(
        related="vendor_bill_id.pricelist_id",
        compute_sudo=True,
    )
    date = fields.Date(
        related="vendor_bill_id.date",
        compute_sudo=True,
    )
