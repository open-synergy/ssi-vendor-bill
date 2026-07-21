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
        "mixin.account_move_single_line",
    ]
    _order = "vendor_bill_id, sequence, id"

    # Accounting Entry Mixin
    _move_id_field_name = "move_id"
    _account_id_field_name = "account_id"
    _partner_id_field_name = "partner_id"
    _analytic_account_id_field_name = "analytic_account_id"
    _currency_id_field_name = "currency_id"
    _company_currency_id_field_name = "company_currency_id"
    _company_id_field_name = "company_id"
    _amount_currency_field_name = "price_subtotal"
    _date_field_name = "date"
    _label_field_name = "name"
    _product_id_field_name = "product_id"
    _uom_id_field_name = "uom_id"
    _quantity_field_name = "uom_quantity"
    _price_unit_field_name = "price_unit"
    _normal_amount = "debit"

    vendor_bill_id = fields.Many2one(
        string="# Vendor Bill",
        comodel_name="vendor_bill",
        required=True,
        ondelete="cascade",
    )

    # Convenience fields mirrored from the header, following the pattern
    # of employee_business_trip.per_diem / employee_business_trip.tax.
    move_id = fields.Many2one(
        related="vendor_bill_id.move_id",
        compute_sudo=True,
    )
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
