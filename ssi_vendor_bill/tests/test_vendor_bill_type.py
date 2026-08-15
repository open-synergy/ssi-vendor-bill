# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase
from psycopg2 import IntegrityError

from odoo import tools
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestVendorBillType(YamlTransactionCase):
    """YAML-scenario and Python-pure tests for ``vendor_bill_type``.

    ``test_vendor_bill_type`` runs the YAML scenario covering CRUD and
    the master-data (de)activation flow. ``test_create_without_journal
    _id_is_rejected`` below is a Python-pure escape hatch for an
    assertion the YAML DSL cannot express (see its own docstring for
    the ``P#``/``L-xx`` trigger code).
    """

    def test_vendor_bill_type(self):
        """Run the ``test_data_vendor_bill_type.yaml`` scenario."""
        self.run_yaml_scenario("test_data_vendor_bill_type.yaml")

    def test_create_without_journal_id_is_rejected(self):
        """Python murni -- pemicu P5 (L-22: exception di luar 12 tipe
        `expect_error`).

        `journal_id` is a required Many2one without a Python-level
        `@api.constrains`, so a missing value only fails at the database
        NOT NULL constraint (``psycopg2.errors.NotNullViolation``, a
        subclass of ``psycopg2.IntegrityError``). That exception type is
        not among the 12 supported by YAML's `expect_error`, so this
        negative path cannot be expressed in
        test_data_vendor_bill_type.yaml.
        """
        account_type = self.env.ref("account.data_account_type_payable")
        payable_account = self.env["account.account"].create(
            {
                "code": "VBTPY%d" % self.env["account.account"].search_count([]),
                "name": "Vendor Bill Type Python Test Payable",
                "user_type_id": account_type.id,
                "reconcile": True,
            }
        )
        with self.assertRaises(IntegrityError), tools.mute_logger("odoo.sql_db"):
            self.env["vendor_bill_type"].create(
                {
                    "name": "No Journal Type",
                    "code": "VBTPY001",
                    "payable_account_id": payable_account.id,
                }
            )
