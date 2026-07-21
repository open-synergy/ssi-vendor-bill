# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class VendorBillTax(models.Model):
    """
    Tax line of a vendor bill.

    Stores a single computed (or manually entered) tax entry associated
    with the detail lines of a vendor bill. Standard fields (``tax_id``,
    ``name``, ``account_id``, ``manual``, ``base_amount``, ``tax_amount``)
    are provided by ``mixin.tax_line``; this model only adds the link
    back to its parent ``vendor_bill`` and a handful of convenience
    fields mirrored from the header, following the pattern of
    ``employee_business_trip.tax``.
    """

    _name = "vendor_bill.tax"
    _description = "Vendor Bill - Tax"
    _inherit = [
        "mixin.tax_line",
    ]
    _order = "vendor_bill_id, id"

    vendor_bill_id = fields.Many2one(
        string="# Vendor Bill",
        comodel_name="vendor_bill",
        required=True,
        ondelete="cascade",
    )

    # Convenience fields mirrored from the header.
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
    date = fields.Date(
        related="vendor_bill_id.date",
        compute_sudo=True,
    )
