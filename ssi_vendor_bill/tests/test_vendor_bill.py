# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2.errors import NotNullViolation

from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo_yaml_test import YamlTransactionCase


@tagged("post_install", "-at_install")
class TestVendorBill(YamlTransactionCase):
    def test_vendor_bill(self):
        self.run_yaml_scenario("test_data_vendor_bill.yaml")

    @mute_logger("odoo.sql_db")
    def test_create_without_type_id_violates_not_null_constraint(self):
        """Python murni -- pemicu P5 (L-22: NotNullViolation di luar 12 tipe
        `expect_error`).

        ``type_id`` wajib (`required=True`) tapi Odoo tidak menegakkan field
        wajib di layer Python saat `create()` -- baris INSERT dikirim apa
        adanya dan constraint NOT NULL di kolom database yang menolaknya,
        sehingga exception yang muncul adalah
        `psycopg2.errors.NotNullViolation` (turunan `psycopg2.IntegrityError`),
        bukan salah satu dari 12 tipe yang didukung `expect_error` YAML.
        `mute_logger` membungkam baris ERROR yang NORMAL dituliskan
        PostgreSQL di sini agar `oca_checklog_odoo` tidak menggagalkan CI
        walau test-nya sendiri lulus.
        """
        vendor = self.env["res.partner"].create(
            {"name": "P5 Vendor Bill Partner", "is_company": True}
        )
        journal = self.env["account.journal"].create(
            {"name": "P5 Vendor Bill Journal", "type": "purchase"}
        )
        account = self.env["account.account"].create(
            {
                "name": "P5 Vendor Bill Payable",
                "code": "VBP5001",
                "user_type_id": self.env.ref(
                    "account.data_account_type_payable"
                ).id,
                "reconcile": True,
            }
        )
        with self.assertRaises(NotNullViolation):
            self.env["vendor_bill"].create(
                {
                    "partner_id": vendor.id,
                    "date": "2024-01-15",
                    "date_due": "2024-02-15",
                    "currency_id": self.env.ref("base.USD").id,
                    "pricelist_id": self.env.ref("product.list0").id,
                    "journal_id": journal.id,
                    "payable_account_id": account.id,
                }
            )
