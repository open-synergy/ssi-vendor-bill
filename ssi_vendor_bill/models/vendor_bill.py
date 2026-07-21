# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class VendorBill(models.Model):
    """
    Represents a vendor bill as a standalone SSI transactional document.

    Tracks the full lifecycle of a purchase invoice received from a
    supplier -- draft, waiting for approval, unpaid (open), and paid
    (done) -- with its own sequence-based document number, multiple
    approval, and policy-controlled actions. This model owns its own
    table; it does not share storage with ``account.move``. Detail lines,
    taxes, and the generation of the accompanying ``account.move`` are
    handled by separate modules/items.
    """

    _name = "vendor_bill"
    _description = "Vendor Bill"
    _inherit = [
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_open",
        "mixin.transaction_confirm",
        "mixin.transaction_date_due",
        "mixin.transaction_partner",
        "mixin.company_currency",
        "mixin.many2one_configurator",
    ]

    # A. Atribut Multiple Approval
    _approval_from_state = "draft"
    _approval_to_state = "open"
    _approval_state = "confirm"
    _after_approved_method = "action_open"

    # B. Atribut Auto-insert View Element
    _automatically_insert_view_element = True
    _automatically_insert_multiple_approval_page = True

    # C. Atribut Form View
    _statusbar_visible_label = "draft,confirm,open,done"
    _policy_field_order = [
        "confirm_ok",
        "open_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "restart_ok",
        "done_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # D. Atribut Search View
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_open",
        "dom_done",
        "dom_reject",
        "dom_cancel",
    ]

    # E. Atribut Sequence
    _create_sequence_state = "open"

    # F. Definisi Field
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("open", "Unpaid"),
            ("done", "Paid"),
            ("cancel", "Cancelled"),
            ("reject", "Rejected"),
        ],
        default="draft",
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="vendor_bill_type",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        ondelete="restrict",
        help="Vendor bill type that determines the default journal, "
        "payable account, and the allowed currencies/pricelists for "
        "this document.",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        ondelete="restrict",
        help="Currency used to express every monetary amount on this " "document.",
    )
    pricelist_id = fields.Many2one(
        string="Pricelist",
        comodel_name="product.pricelist",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        ondelete="restrict",
        help="Pricelist used to determine the vendor price of the "
        "products purchased on this document.",
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        ondelete="restrict",
        help="Accounting journal in which the resulting accounting "
        "entry of this document will be posted.",
    )
    payable_account_id = fields.Many2one(
        string="Payable Account",
        comodel_name="account.account",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        ondelete="restrict",
        help="Payable account credited for the total amount owed to "
        "the vendor when this document is posted.",
    )
    analytic_account_id = fields.Many2one(
        string="Analytic Account",
        comodel_name="account.analytic.account",
        readonly=True,
        states={"draft": [("readonly", False)]},
        ondelete="restrict",
        help="Analytic account used to track the cost of this document "
        "for analytic reporting purposes.",
    )
    partner_document_number = fields.Char(
        string="Vendor Document Number",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=False,
        help="Reference number of the original document issued by the "
        "vendor (e.g. their own invoice number), used to cross-check "
        "against the vendor's own records.",
    )
    allowed_currency_ids = fields.Many2many(
        string="Allowed Currencies",
        comodel_name="res.currency",
        compute="_compute_allowed_currency_ids",
        store=False,
        compute_sudo=True,
        help="Currencies that may be selected on this document, "
        "determined by the currency selection method configured on "
        "the selected Type.",
    )
    allowed_pricelist_ids = fields.Many2many(
        string="Allowed Pricelists",
        comodel_name="product.pricelist",
        compute="_compute_allowed_pricelist_ids",
        store=False,
        compute_sudo=True,
        help="Pricelists that may be selected on this document, "
        "determined by the pricelist selection method configured on "
        "the selected Type.",
    )

    # G. Compute Methods
    @api.depends("type_id")
    def _compute_allowed_currency_ids(self):
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="res.currency",
                    method_selection=record.type_id.currency_selection_method,
                    manual_recordset=record.type_id.currency_ids,
                    domain=record.type_id.currency_domain,
                    python_code=record.type_id.currency_python_code,
                )
            record.allowed_currency_ids = result

    @api.depends("type_id")
    def _compute_allowed_pricelist_ids(self):
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="product.pricelist",
                    method_selection=record.type_id.pricelist_selection_method,
                    manual_recordset=record.type_id.pricelist_ids,
                    domain=record.type_id.pricelist_domain,
                    python_code=record.type_id.pricelist_python_code,
                )
            record.allowed_pricelist_ids = result

    # H. Onchange Methods
    @api.onchange("type_id")
    def onchange_journal_id(self):
        self.journal_id = False
        if self.type_id:
            self.journal_id = self.type_id.journal_id

    @api.onchange("type_id")
    def onchange_payable_account_id(self):
        self.payable_account_id = False
        if self.type_id:
            self.payable_account_id = self.type_id.payable_account_id

    # J. Decorator: Insert Form Element
    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch

    # K. Override _get_policy_field
    @api.model
    def _get_policy_field(self):
        res = super()._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "reject_ok",
            "restart_approval_ok",
            "cancel_ok",
            "restart_ok",
            "open_ok",
            "done_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res
