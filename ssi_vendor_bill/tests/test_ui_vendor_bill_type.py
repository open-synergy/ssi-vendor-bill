# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestUiVendorBillType(HttpCase):
    """UI/UX tour tests for ``vendor_bill_type``.

    Every ``test_*`` method below runs the tour pairing with the IK file
    named in its docstring (``docs/vendor_bill_type/NN-*.md``). Pre-Condition
    data required by each IK is prepared here in Python -- never through UI
    steps -- following the tour authoring doctrine: prerequisite/background
    data belongs to ``setUpClass``, the tour itself only exercises the
    click-flow documented in the IK.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        payable_acc_type = cls.env.ref("account.data_account_type_payable")

        cls.journal = cls.env["account.journal"].create(
            {
                "name": "TOUR Vendor Bill Type Journal",
                "code": "TOURVBTJ",
                "type": "purchase",
            }
        )
        cls.payable_account = cls.env["account.account"].create(
            {
                "code": "TOURVBTP",
                "name": "TOUR Vendor Bill Type Payable",
                "user_type_id": payable_acc_type.id,
                "reconcile": True,
            }
        )

        cls.type_edit = cls._create_type("TOUR VBT Edit")
        cls.type_delete = cls._create_type("TOUR VBT Delete")
        cls.type_deactivate = cls._create_type("TOUR VBT Deactivate")
        cls.type_activate = cls._create_type("TOUR VBT Activate", active=False)

    @classmethod
    def _create_type(cls, name, active=True):
        """Pre-Condition helper: create a draft ``vendor_bill_type`` record.

        Journal and Payable Account are set explicitly since Python
        ``create()`` does not trigger onchange. ``code`` is left as ``"/"``
        (per Flow step 3 of ``docs/vendor_bill_type/01-create.md``, the
        allow-list-of-values later than a unique code is not needed here)
        so several records can share it without violating the unique-code
        constraint (``mixin.master_data._check_duplicate_code`` explicitly
        excludes ``code == "/"`` from the duplicate check).
        """
        return cls.env["vendor_bill_type"].create(
            {
                "name": name,
                "code": "/",
                "journal_id": cls.journal.id,
                "payable_account_id": cls.payable_account.id,
                "active": active,
            }
        )

    def test_create(self):
        """IK: docs/vendor_bill_type/01-create.md"""
        self.start_tour(
            "/web", "ssi_vendor_bill_vendor_bill_type_create", login="admin"
        )

    def test_edit(self):
        """IK: docs/vendor_bill_type/02-edit.md"""
        self.start_tour("/web", "ssi_vendor_bill_vendor_bill_type_edit", login="admin")

    def test_delete(self):
        """IK: docs/vendor_bill_type/03-delete.md"""
        self.start_tour(
            "/web", "ssi_vendor_bill_vendor_bill_type_delete", login="admin"
        )

    def test_deactivate(self):
        """IK: docs/vendor_bill_type/04-deactivate.md"""
        self.start_tour(
            "/web", "ssi_vendor_bill_vendor_bill_type_deactivate", login="admin"
        )

    def test_activate(self):
        """IK: docs/vendor_bill_type/05-activate.md"""
        self.start_tour(
            "/web", "ssi_vendor_bill_vendor_bill_type_activate", login="admin"
        )
