# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestVendorBillClaudeCodeBackend(YamlTransactionCase):
    """Covers create/edit/delete of ``vendor.bill.claude.code.backend``."""

    def test_vendor_bill_claude_code_backend(self):
        """Run the create/edit/delete scenario for the backend model."""
        self.run_yaml_scenario("test_vendor_bill_claude_code_backend.yaml")
