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
        "mixin.transaction_pricelist",
        "mixin.account_move",
        "mixin.account_move_single_line",
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

    # E2. Atribut Perhitungan Pajak (mixin.account_move)
    _tax_lines_field_name = "tax_ids"
    _tax_on_self = False
    _tax_source_recordset_field_name = "line_ids"
    _price_unit_field_name = "price_unit"
    _quantity_field_name = "uom_quantity"

    # E3. Atribut Accounting Entry (mixin.account_move_single_line -- payable
    # journal item created on the header itself)
    _journal_id_field_name = "journal_id"
    _move_id_field_name = "move_id"
    _accounting_date_field_name = "date"
    _currency_id_field_name = "currency_id"
    _company_currency_id_field_name = "company_currency_id"
    _account_id_field_name = "payable_account_id"
    _partner_id_field_name = "partner_id"
    _analytic_account_id_field_name = "analytic_account_id"
    _amount_currency_field_name = "amount_total"
    _date_field_name = "date"
    _label_field_name = "name"
    _date_due_field_name = "date_due"
    _need_date_due = True
    _normal_amount = "credit"

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
    allowed_product_ids = fields.Many2many(
        string="Allowed Products",
        comodel_name="product.product",
        compute="_compute_allowed_product_ids",
        store=False,
        compute_sudo=True,
        help="Products that may be selected on the detail lines of this "
        "document, determined by the product selection method "
        "configured on the selected Type.",
    )
    line_ids = fields.One2many(
        string="Lines",
        comodel_name="vendor_bill.line",
        inverse_name="vendor_bill_id",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Product/service detail lines being billed on this "
        "document. Used to compute the untaxed amount and, together "
        "with the applicable taxes, the tax lines.",
    )
    tax_ids = fields.One2many(
        string="Taxes",
        comodel_name="vendor_bill.tax",
        inverse_name="vendor_bill_id",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Tax lines computed automatically from the detail lines "
        "(or entered manually).",
    )
    amount_untaxed = fields.Monetary(
        string="Untaxed Amount",
        compute="_compute_amount",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="Sum of the price subtotal of every detail line.",
    )
    amount_tax = fields.Monetary(
        string="Tax",
        compute="_compute_amount",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="Sum of the tax amount of every tax line.",
    )
    amount_total = fields.Monetary(
        string="Total",
        compute="_compute_amount",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="Untaxed amount plus tax amount.",
    )
    move_id = fields.Many2one(
        string="Move",
        comodel_name="account.move",
        readonly=True,
        copy=False,
        help="Journal entry generated when this document is opened. Left "
        "empty for documents without detail lines, which move directly "
        "to Paid without waiting for reconciliation.",
    )
    payable_move_line_id = fields.Many2one(
        string="Payable Move Line",
        comodel_name="account.move.line",
        readonly=True,
        copy=False,
        help="Journal item on the payable account created together with "
        "``move_id``. Its reconciliation status drives the automatic "
        "Unpaid/Paid transition.",
    )
    realized = fields.Boolean(
        string="Realized",
        related="payable_move_line_id.reconciled",
        store=True,
        compute_sudo=True,
        help="Technical flag mirroring whether the payable journal item "
        "has been fully reconciled. Drives the automatic done/open state "
        "transition through base.automation.",
    )
    amount_realized = fields.Monetary(
        string="Realized Amount",
        compute="_compute_realized",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="Portion of the total amount already settled, derived from "
        "the payable journal item's residual amount.",
    )
    amount_residual = fields.Monetary(
        string="Residual Amount",
        compute="_compute_realized",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="Portion of the total amount still outstanding on the "
        "payable journal item.",
    )

    # G. Compute Methods
    @api.depends("type_id")
    def _compute_allowed_currency_ids(self):
        """Compute the currencies selectable on this document.

        Delegates to ``mixin.many2one_configurator`` using the
        currency selection method (manual/domain/code) configured on
        ``type_id``. Empty when no ``type_id`` is set yet.
        """
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
        """Compute the pricelists selectable on this document.

        Delegates to ``mixin.many2one_configurator`` using the
        pricelist selection method (manual/domain/code) configured on
        ``type_id``. Empty when no ``type_id`` is set yet.
        """
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

    @api.depends("type_id")
    def _compute_allowed_product_ids(self):
        """Compute the products selectable on the detail lines.

        Delegates to ``mixin.many2one_configurator`` using the
        product selection method (manual/domain/code) configured on
        ``type_id``. Empty when no ``type_id`` is set yet.
        """
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="product.product",
                    method_selection=record.type_id.product_selection_method,
                    manual_recordset=record.type_id.product_ids,
                    domain=record.type_id.product_domain,
                    python_code=record.type_id.product_python_code,
                )
            record.allowed_product_ids = result

    @api.depends(
        "line_ids.price_subtotal",
        "tax_ids.tax_amount",
    )
    def _compute_amount(self):
        """Compute the header monetary totals from lines and taxes.

        ``amount_untaxed`` is the sum of ``line_ids.price_subtotal``,
        ``amount_tax`` is the sum of ``tax_ids.tax_amount``, and
        ``amount_total`` is their sum.
        """
        for record in self:
            amount_untaxed = sum(record.line_ids.mapped("price_subtotal"))
            amount_tax = sum(record.tax_ids.mapped("tax_amount"))
            record.amount_untaxed = amount_untaxed
            record.amount_tax = amount_tax
            record.amount_total = amount_untaxed + amount_tax

    @api.depends(
        "payable_move_line_id.amount_residual_currency",
        "payable_move_line_id.reconciled",
        "amount_total",
    )
    def _compute_realized(self):
        """Compute the realized/residual portion of the total amount.

        Derives both values from ``payable_move_line_id``'s residual
        amount (sign-flipped, since it is a credit line); both are
        zero when the document has no payable move line yet.
        """
        for record in self:
            amount_realized = 0.0
            amount_residual = 0.0

            if record.payable_move_line_id:
                amount_residual = (
                    -1.0 * record.payable_move_line_id.amount_residual_currency
                )
                amount_realized = record.amount_total - amount_residual

            record.amount_realized = amount_realized
            record.amount_residual = amount_residual

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

    # I. Action Methods
    def action_compute_tax(self):
        """Recompute the tax lines from the current detail lines.

        Called from the **Compute Tax** button on the Detail tab.
        Runs with ``sudo()`` so users without direct write access to
        ``vendor_bill.tax`` can still trigger the recomputation.
        """
        for record in self.sudo():
            record._compute_tax()

    def _compute_tax(self):
        """Replace the tax lines with the recomputed standard tax lines.

        Thin wrapper around ``mixin.account_move``'s
        ``_recompute_standard_tax`` -- kept as a separate method so it
        can be called both from ``action_compute_tax`` and from the
        pre-confirm hook below without duplicating ``ensure_one()``.
        """
        self.ensure_one()
        self._recompute_standard_tax()

    # I2. Pre-confirm Hook: Recompute Tax
    @ssi_decorator.pre_confirm_action()
    def _01_compute_tax(self):
        """Recompute the tax lines just before the record is confirmed.

        Runs as a pre-``action_confirm`` hook so the tax lines saved
        on the record always reflect the detail lines at confirmation
        time, even if the user forgot to click **Compute Tax**
        manually.
        """
        self.ensure_one()
        self._recompute_standard_tax()

    # I3. Post-open Hooks: Create Accounting Entry / Skip Straight to Done
    @ssi_decorator.post_open_action()
    def _10_create_accounting_entry(self):
        """Create the accounting entry when the document is opened.

        Skipped when there are no detail lines (nothing to post) or
        when ``move_id`` is already set (idempotent on repeated
        calls). Creates the journal entry and its payable journal
        item via ``mixin.account_move_single_line``/
        ``mixin.account_move``, links ``payable_move_line_id`` to the
        newly created line, generates a journal item for every
        detail/tax line, and posts the move.
        """
        self.ensure_one()

        if not self.line_ids or self.move_id:
            return True

        self._create_standard_move()  # Mixin
        ml = self._create_standard_ml()  # Mixin
        self.write(
            {
                "payable_move_line_id": ml.id,
            }
        )

        for line in self.line_ids:
            line._create_standard_ml()  # Mixin

        for tax in self.tax_ids:
            tax._create_standard_ml()  # Mixin

        self._post_standard_move()  # Mixin

    @ssi_decorator.post_open_action()
    def _20_skip_open(self):
        """Move a document without detail lines straight to Paid.

        When ``_10_create_accounting_entry`` above did not create a
        ``move_id`` (no detail lines), there is nothing left to
        reconcile, so the document transitions directly to **Paid**
        instead of waiting in **Unpaid**.
        """
        self.ensure_one()
        if not self.move_id:
            self.action_done()

    # I4. Post-cancel Hook: Delete Accounting Entry
    @ssi_decorator.post_cancel_action()
    def _30_delete_accounting_entry(self):
        """Delete the accounting entry when the document is cancelled.

        Runs as a post-``action_cancel`` hook so the journal entry
        (and its journal items) created by
        ``_10_create_accounting_entry`` does not linger once the
        document is cancelled.
        """
        self.ensure_one()
        self._delete_standard_move()  # Mixin

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
