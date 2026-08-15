# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase — NOT HttpCase. In 14.0, HttpCase does not set up
# cls.env in setUpClass, so fixtures written there would fail before the
# browser ever starts.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiVendorBillClaudeCodeBackend(HttpSavepointCase):
    """Tour tests for the ``vendor.bill.claude.code.backend`` work
    instructions."""

    @classmethod
    def setUpClass(cls):
        """Create the backends the edit/delete/deactivate/activate tours
        open. ``admin`` is already a member of the *Vendor Bill Claude
        Code Import* group via module data, so no extra group grant is
        needed here.
        """
        super().setUpClass()
        cls.admin = cls.env.ref("base.user_admin")
        cls.backend_edit = cls.env["vendor.bill.claude.code.backend"].create(
            {
                "name": "Tour Backend Edit",
                "code": "TOUR-BACKEND-EDIT",
                "base_url": "https://vendor-bill-tour.example.com",
                "bearer_token": "tour-token",
            }
        )
        cls.backend_delete = cls.env["vendor.bill.claude.code.backend"].create(
            {
                "name": "Tour Backend Delete",
                "code": "TOUR-BACKEND-DELETE",
                "base_url": "https://vendor-bill-tour.example.com",
                "bearer_token": "tour-token",
            }
        )
        cls.backend_deactivate = cls.env["vendor.bill.claude.code.backend"].create(
            {
                "name": "Tour Backend Deactivate",
                "code": "TOUR-BACKEND-DEACTIVATE",
                "base_url": "https://vendor-bill-tour.example.com",
                "bearer_token": "tour-token",
            }
        )
        cls.backend_activate = cls.env["vendor.bill.claude.code.backend"].create(
            {
                "name": "Tour Backend Activate",
                "code": "TOUR-BACKEND-ACTIVATE",
                "base_url": "https://vendor-bill-tour.example.com",
                "bearer_token": "tour-token",
                "active": False,
            }
        )

    def test_create(self):
        """Run the create tour for ``vendor.bill.claude.code.backend``.

        IK: docs/vendor_bill_claude_code_backend/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_vendor_bill_claude_code_vendor_bill_claude_code_backend_create",
            login="admin",
        )

    def test_edit(self):
        """Run the edit tour for ``vendor.bill.claude.code.backend``.

        IK: docs/vendor_bill_claude_code_backend/02-edit.md
        """
        self.start_tour(
            "/web",
            "ssi_vendor_bill_claude_code_vendor_bill_claude_code_backend_edit",
            login="admin",
        )

    def test_delete(self):
        """Run the delete tour for ``vendor.bill.claude.code.backend``.

        IK: docs/vendor_bill_claude_code_backend/03-delete.md
        """
        self.start_tour(
            "/web",
            "ssi_vendor_bill_claude_code_vendor_bill_claude_code_backend_delete",
            login="admin",
        )

    def test_deactivate(self):
        """Run the deactivate tour for ``vendor.bill.claude.code.backend``.

        IK: docs/vendor_bill_claude_code_backend/04-deactivate.md
        """
        self.start_tour(
            "/web",
            "ssi_vendor_bill_claude_code_vendor_bill_claude_code_backend_deactivate",
            login="admin",
        )

    def test_activate(self):
        """Run the activate tour for ``vendor.bill.claude.code.backend``.

        IK: docs/vendor_bill_claude_code_backend/05-activate.md
        """
        self.start_tour(
            "/web",
            "ssi_vendor_bill_claude_code_vendor_bill_claude_code_backend_activate",
            login="admin",
        )
