# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestVendorBillClaudeCodeImportWizard(YamlTransactionCase):
    """Covers the ``import_vendor_bill_claude_code`` attachment wiring."""

    def test_vendor_bill_claude_code_import_wizard(self):
        """Run the attachment/main-attachment scenario for the wizard."""
        self.run_yaml_scenario("test_vendor_bill_claude_code_import_wizard.yaml")
