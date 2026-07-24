# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiVendorBillOperatingUnit(HttpSavepointCase):
    """UI/UX tour test for the Operating Unit field this module adds to
    ``vendor_bill`` (E1 delta -- Additional Fields).

    Pairs with IK ``docs/vendor_bill/01-create.md`` (delta), backed by the
    base IK ``ssi_vendor_bill/docs/vendor_bill/01-create.md`` for the
    navigation up to the New button -- see open-synergy/ssi-vendor-bill#39.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Pre-Condition: the Operating Unit field is gated by the multi
        # operating unit group (`groups="operating_unit.group_multi_operating_unit"`
        # in the view) -- without it, the field is never rendered and the
        # delta assertion would never find it. The user also needs at
        # least one operating unit assigned so the field has a meaningful
        # (non-empty) allowed set.
        cls.user_admin = cls.env.ref("base.user_admin")
        cls.operating_unit_partner = cls.env["res.partner"].create(
            {"name": "TOUR Vendor Bill OU Partner"}
        )
        cls.operating_unit = cls.env["operating.unit"].create(
            {
                "name": "TOUR Vendor Bill Operating Unit",
                "code": "TVBOU",
                "partner_id": cls.operating_unit_partner.id,
            }
        )
        cls.env.ref("operating_unit.group_multi_operating_unit").sudo().write(
            {"users": [(4, cls.user_admin.id)]}
        )
        cls.user_admin.sudo().write(
            {
                "assigned_operating_unit_ids": [(4, cls.operating_unit.id)],
                "default_operating_unit_id": cls.operating_unit.id,
            }
        )

        # Pre-Condition: supporting data so the Vendor Bill create form can
        # be opened -- Type / Journal / Payable Account, following the same
        # fixture pattern as the base module's own tour test
        # (ssi_vendor_bill/tests/test_ui_vendor_bill.py).
        payable_acc_type = cls.env.ref("account.data_account_type_payable")
        cls.payable_account = cls.env["account.account"].create(
            {
                "code": "TOURVBOUP",
                "name": "TOUR Vendor Bill OU Payable",
                "user_type_id": payable_acc_type.id,
                "reconcile": True,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "TOUR Vendor Bill OU Journal",
                "code": "TVBOU",
                "type": "purchase",
            }
        )
        cls.bill_type = cls.env["vendor_bill_type"].create(
            {
                "name": "TOUR Vendor Bill OU Type",
                "code": "/",
                "journal_id": cls.journal.id,
                "payable_account_id": cls.payable_account.id,
            }
        )

    def test_field_operating_unit(self):
        """IK: docs/vendor_bill/01-create.md (E1 delta -- Additional Fields)"""
        self.start_tour(
            "/web",
            "ssi_vendor_bill_operating_unit_vendor_bill_create",
            login="admin",
        )
