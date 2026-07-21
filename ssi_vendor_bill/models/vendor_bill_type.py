# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class VendorBillType(models.Model):
    """
    Represents a configuration template for a category of vendor bills.

    Stores the default journal and payable account used when posting a
    vendor bill of this type, plus three independent allow-lists (product,
    currency, pricelist) that a vendor bill document of this type may use.
    Each allow-list supports three selection strategies -- manual (explicit
    recordset), domain (ORM domain string), or code (Python snippet) -- but
    the strategy is only *stored* here; evaluating it is the responsibility
    of the document side via ``mixin.many2one_configurator``. This model has
    no methods of its own.
    """

    _name = "vendor_bill_type"
    _inherit = ["mixin.master_data"]
    _description = "Vendor Bill Type"

    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        required=True,
        ondelete="restrict",
        help="Default journal used when posting a vendor bill of this type.",
    )
    payable_account_id = fields.Many2one(
        string="Payable Account",
        comodel_name="account.account",
        required=True,
        ondelete="restrict",
        help="Default payable account used when posting a vendor bill of " "this type.",
    )

    # --- Product M2O configurator ---

    product_selection_method = fields.Selection(
        string="Product Selection Method",
        selection=[
            ("manual", "Manual"),
            ("domain", "Domain"),
            ("code", "Python Code"),
        ],
        default="domain",
        required=True,
        help="Method used to determine which products can be selected on a "
        "vendor bill of this type.",
    )
    product_ids = fields.Many2many(
        string="Products",
        comodel_name="product.product",
        relation="rel_vendor_bill_type_2_product",
        column1="type_id",
        column2="product_id",
        help="Manually selected list of allowed products. Used when "
        "Product Selection Method = Manual.",
    )
    product_domain = fields.Text(
        default="[]",
        string="Product Domain",
        help="Domain expression evaluated against product.product to "
        "determine the allowed products. Used when Product Selection "
        "Method = Domain.",
    )
    product_python_code = fields.Text(
        default="result = []",
        string="Product Python Code",
        help="Python code that must set the `result` variable to a "
        "recordset of product.product. Used when Product Selection "
        "Method = Python Code.",
    )

    # --- Currency M2O configurator ---

    currency_selection_method = fields.Selection(
        string="Currency Selection Method",
        selection=[
            ("manual", "Manual"),
            ("domain", "Domain"),
            ("code", "Python Code"),
        ],
        default="domain",
        required=True,
        help="Method used to determine which currencies can be selected on "
        "a vendor bill of this type.",
    )
    currency_ids = fields.Many2many(
        string="Currencies",
        comodel_name="res.currency",
        relation="rel_vendor_bill_type_2_currency",
        column1="type_id",
        column2="currency_id",
        help="Manually selected list of allowed currencies. Used when "
        "Currency Selection Method = Manual.",
    )
    currency_domain = fields.Text(
        default="[]",
        string="Currency Domain",
        help="Domain expression evaluated against res.currency to "
        "determine the allowed currencies. Used when Currency Selection "
        "Method = Domain.",
    )
    currency_python_code = fields.Text(
        default="result = []",
        string="Currency Python Code",
        help="Python code that must set the `result` variable to a "
        "recordset of res.currency. Used when Currency Selection Method "
        "= Python Code.",
    )

    # --- Pricelist M2O configurator ---

    pricelist_selection_method = fields.Selection(
        string="Pricelist Selection Method",
        selection=[
            ("manual", "Manual"),
            ("domain", "Domain"),
            ("code", "Python Code"),
        ],
        default="domain",
        required=True,
        help="Method used to determine which pricelists can be selected on "
        "a vendor bill of this type.",
    )
    pricelist_ids = fields.Many2many(
        string="Pricelists",
        comodel_name="product.pricelist",
        relation="rel_vendor_bill_type_2_pricelist",
        column1="type_id",
        column2="pricelist_id",
        help="Manually selected list of allowed pricelists. Used when "
        "Pricelist Selection Method = Manual.",
    )
    pricelist_domain = fields.Text(
        default="[]",
        string="Pricelist Domain",
        help="Domain expression evaluated against product.pricelist to "
        "determine the allowed pricelists. Used when Pricelist Selection "
        "Method = Domain.",
    )
    pricelist_python_code = fields.Text(
        default="result = []",
        string="Pricelist Python Code",
        help="Python code that must set the `result` variable to a "
        "recordset of product.pricelist. Used when Pricelist Selection "
        "Method = Python Code.",
    )
