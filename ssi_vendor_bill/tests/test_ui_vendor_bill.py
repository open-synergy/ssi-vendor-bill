# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestUiVendorBill(HttpCase):
    """UI/UX tour tests for ``vendor_bill``.

    Every ``test_*`` method below runs the tour pairing with the IK file
    named in its docstring (``docs/vendor_bill/NN-*.md``). Pre-Condition
    data required by each IK is prepared here in Python -- never through UI
    steps -- following the tour authoring doctrine: prerequisite/background
    data belongs to ``setUpClass``, the tour itself only exercises the
    click-flow documented in the IK.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        payable_acc_type = cls.env.ref("account.data_account_type_payable")
        expense_acc_type = cls.env.ref("account.data_account_type_expenses")

        cls.payable_account = cls.env["account.account"].create(
            {
                "code": "TOURVBP",
                "name": "TOUR Vendor Bill Payable",
                "user_type_id": payable_acc_type.id,
                "reconcile": True,
            }
        )
        cls.expense_account = cls.env["account.account"].create(
            {
                "code": "TOURVBE",
                "name": "TOUR Vendor Bill Expense",
                "user_type_id": expense_acc_type.id,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "TOUR Vendor Bill Journal",
                "code": "TOURVBJ",
                "type": "purchase",
            }
        )
        # Selection methods are left at their "domain" default with an
        # empty domain ("[]"), which resolves to "every record allowed" --
        # simplest configuration so the tour can freely pick any
        # currency/pricelist/product without fighting an allow-list.
        cls.bill_type = cls.env["vendor_bill_type"].create(
            {
                "name": "TOUR Vendor Bill Type",
                "code": "TOURVBT",
                "journal_id": cls.journal.id,
                "payable_account_id": cls.payable_account.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "TOUR Vendor Bill Product"}
        )
        cls.currency = cls.env.ref("base.USD")
        cls.pricelist = cls.env.ref("product.list0")
        cls.cancel_reason = cls.env["base.cancel_reason"].create(
            {
                "name": "TOUR Vendor Bill Cancel Reason",
                "code": "TOURVBCR",
                "global_use": True,
            }
        )

        cls.partner_create = cls.env["res.partner"].create(
            {"name": "TOUR Create Vendor", "is_company": True}
        )
        cls.partner_edit = cls.env["res.partner"].create(
            {"name": "TOUR Edit Vendor", "is_company": True}
        )
        cls.partner_delete = cls.env["res.partner"].create(
            {"name": "TOUR Delete Vendor", "is_company": True}
        )
        cls.partner_confirm = cls.env["res.partner"].create(
            {"name": "TOUR Confirm Vendor", "is_company": True}
        )
        cls.partner_approve = cls.env["res.partner"].create(
            {"name": "TOUR Approve Vendor", "is_company": True}
        )
        cls.partner_reject = cls.env["res.partner"].create(
            {"name": "TOUR Reject Vendor", "is_company": True}
        )
        cls.partner_cancel = cls.env["res.partner"].create(
            {"name": "TOUR Cancel Vendor", "is_company": True}
        )
        cls.partner_restart = cls.env["res.partner"].create(
            {"name": "TOUR Restart Vendor", "is_company": True}
        )
        cls.partner_compute_tax = cls.env["res.partner"].create(
            {"name": "TOUR Compute Tax Vendor", "is_company": True}
        )

        cls.bill_edit = cls._create_bill(cls.partner_edit)
        cls.bill_delete = cls._create_bill(cls.partner_delete)
        cls.bill_confirm = cls._create_bill(cls.partner_confirm)

        cls.bill_approve = cls._create_bill(cls.partner_approve, with_line=True)
        cls.bill_approve.with_context(bypass_policy_check=True).action_confirm()

        cls.bill_reject = cls._create_bill(cls.partner_reject)
        cls.bill_reject.with_context(bypass_policy_check=True).action_confirm()

        cls.bill_cancel = cls._create_bill(cls.partner_cancel)

        cls.bill_restart = cls._create_bill(cls.partner_restart)
        cls.bill_restart.with_context(bypass_policy_check=True).action_cancel(
            cls.cancel_reason
        )

        cls.bill_compute_tax = cls._create_bill(cls.partner_compute_tax, with_line=True)

    @classmethod
    def _create_bill(cls, partner, with_line=False):
        """Pre-Condition helper: create a draft ``vendor_bill`` for ``partner``.

        Header fields normally auto-filled by onchange in the UI (journal,
        payable account) are set explicitly here since Python ``create()``
        does not trigger onchange.
        """
        bill = cls.env["vendor_bill"].create(
            {
                "type_id": cls.bill_type.id,
                "partner_id": partner.id,
                "date": "2026-01-15",
                "date_due": "2026-02-15",
                "currency_id": cls.currency.id,
                "pricelist_id": cls.pricelist.id,
                "journal_id": cls.journal.id,
                "payable_account_id": cls.payable_account.id,
            }
        )
        if with_line:
            cls.env["vendor_bill.line"].create(
                {
                    "vendor_bill_id": bill.id,
                    "product_id": cls.product.id,
                    "name": cls.product.name,
                    "account_id": cls.expense_account.id,
                    "uom_quantity": 1,
                    "price_unit": 100000.0,
                }
            )
        return bill

    def test_create(self):
        """IK: docs/vendor_bill/01-create.md"""
        self.start_tour("/web", "ssi_vendor_bill_vendor_bill_create", login="admin")

    def test_edit(self):
        """IK: docs/vendor_bill/02-edit.md"""
        self.start_tour("/web", "ssi_vendor_bill_vendor_bill_edit", login="admin")

    def test_delete(self):
        """IK: docs/vendor_bill/03-delete.md"""
        self.start_tour("/web", "ssi_vendor_bill_vendor_bill_delete", login="admin")

    def test_confirm(self):
        """IK: docs/vendor_bill/04-confirm.md"""
        self.start_tour("/web", "ssi_vendor_bill_vendor_bill_confirm", login="admin")

    def test_approve(self):
        """IK: docs/vendor_bill/05-approve.md"""
        self.start_tour("/web", "ssi_vendor_bill_vendor_bill_approve", login="admin")

    def test_reject(self):
        """IK: docs/vendor_bill/06-reject.md"""
        self.start_tour("/web", "ssi_vendor_bill_vendor_bill_reject", login="admin")

    def test_cancel(self):
        """IK: docs/vendor_bill/10-cancel.md"""
        self.start_tour("/web", "ssi_vendor_bill_vendor_bill_cancel", login="admin")

    def test_restart(self):
        """IK: docs/vendor_bill/12-restart.md"""
        self.start_tour("/web", "ssi_vendor_bill_vendor_bill_restart", login="admin")

    def test_compute_tax(self):
        """IK: docs/vendor_bill/14-compute-tax.md"""
        self.start_tour(
            "/web", "ssi_vendor_bill_vendor_bill_compute_tax", login="admin"
        )
