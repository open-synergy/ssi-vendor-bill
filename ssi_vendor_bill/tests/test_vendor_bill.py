# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase
from psycopg2.errors import NotNullViolation

from odoo.tests import tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestVendorBill(YamlTransactionCase):
    def test_vendor_bill(self):
        self.run_yaml_scenario("test_data_vendor_bill.yaml")

    def _create_bill_with_lines(self):
        """Shared fixture for the P2/P3 python-pure tests below. Built fresh
        here (not taken from the YAML registry, which only lives during
        ``run_yaml_scenario``).
        """
        payable_acc_type = self.env.ref("account.data_account_type_payable")
        expense_acc_type = self.env.ref("account.data_account_type_expenses")
        account = self.env["account.account"].create(
            {
                "code": "VBP2%d" % self.env["account.account"].search_count([]),
                "name": "P2/P3 Vendor Bill Payable",
                "user_type_id": payable_acc_type.id,
                "reconcile": True,
            }
        )
        expense_account_1 = self.env["account.account"].create(
            {
                "code": "VBE2%d" % self.env["account.account"].search_count([]),
                "name": "P2/P3 Vendor Bill Expense 1",
                "user_type_id": expense_acc_type.id,
            }
        )
        expense_account_2 = self.env["account.account"].create(
            {
                "code": "VBE3%d" % self.env["account.account"].search_count([]),
                "name": "P2/P3 Vendor Bill Expense 2",
                "user_type_id": expense_acc_type.id,
            }
        )
        journal = self.env["account.journal"].create(
            {
                "name": "P2/P3 Vendor Bill Journal",
                "code": "VBJ2%d" % self.env["account.journal"].search_count([]),
                "type": "purchase",
            }
        )
        bill_type = self.env["vendor_bill_type"].create(
            {
                "name": "P2/P3 Vendor Bill Type",
                "code": "/",
                "journal_id": journal.id,
                "payable_account_id": account.id,
            }
        )
        vendor = self.env["res.partner"].create(
            {"name": "P2/P3 Vendor Bill Partner", "is_company": True}
        )
        bill = self.env["vendor_bill"].create(
            {
                "type_id": bill_type.id,
                "partner_id": vendor.id,
                "date": "2024-01-15",
                "date_due": "2024-02-15",
                "currency_id": self.env.ref("base.USD").id,
                "pricelist_id": self.env.ref("product.list0").id,
                "journal_id": journal.id,
                "payable_account_id": account.id,
            }
        )
        Line = self.env["vendor_bill.line"]
        line_1 = Line.create(
            {
                "vendor_bill_id": bill.id,
                "name": "Line 1",
                "account_id": expense_account_1.id,
                "uom_quantity": 1,
                "price_unit": 100000.0,
            }
        )
        line_2 = Line.create(
            {
                "vendor_bill_id": bill.id,
                "name": "Line 2",
                "account_id": expense_account_2.id,
                "uom_quantity": 2,
                "price_unit": 75000.0,
            }
        )
        return bill, line_1, line_2

    def test_journal_entry_has_one_payable_line_and_matching_debit_lines(self):
        """Python murni -- pemicu P3 (L-06: isi/urutan baris x2m tak bisa
        di-assert dari YAML -- `type: o2m`/`m2m` hanya mendukung
        count/contains/exact terhadap satu field relasional secara
        keseluruhan, bukan filter per akun atau per debit/kredit).

        Setelah ``action_open``, ``move_id.line_ids`` harus berisi tepat
        satu baris pada ``payable_account_id`` (kredit > 0, debit == 0) dan
        satu baris debit > 0 pada masing-masing ``account_id`` milik setiap
        ``vendor_bill.line``.
        """
        bill, line_1, line_2 = self._create_bill_with_lines()
        bill.with_context(bypass_policy_check=True).action_open()

        self.assertEqual(bill.state, "open")
        self.assertTrue(bill.move_id)
        self.assertEqual(bill.move_id.state, "posted")

        payable_lines = bill.move_id.line_ids.filtered(
            lambda ml: ml.account_id == bill.payable_account_id
        )
        self.assertEqual(len(payable_lines), 1)
        self.assertEqual(payable_lines.debit, 0.0)
        self.assertGreater(payable_lines.credit, 0.0)

        for line in (line_1, line_2):
            expense_lines = bill.move_id.line_ids.filtered(
                lambda ml: ml.account_id == line.account_id
            )
            self.assertEqual(len(expense_lines), 1)
            self.assertGreater(expense_lines.debit, 0.0)
            self.assertEqual(expense_lines.credit, 0.0)

    def test_payable_line_credit_equals_amount_total(self):
        """Python murni -- pemicu P2 (L-04: tidak ada toleransi float di
        YAML untuk nilai moneter; ``equals`` adalah ``!=`` mentah).

        ``credit`` baris hutang pada ``move_id`` harus tepat sama dengan
        ``amount_total`` dokumen.
        """
        bill, _line_1, _line_2 = self._create_bill_with_lines()
        bill.with_context(bypass_policy_check=True).action_open()

        payable_line = bill.move_id.line_ids.filtered(
            lambda ml: ml.account_id == bill.payable_account_id
        )
        self.assertEqual(payable_line.credit, bill.amount_total)

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
            {"name": "P5 Vendor Bill Journal", "code": "VBP5J", "type": "purchase"}
        )
        account = self.env["account.account"].create(
            {
                "name": "P5 Vendor Bill Payable",
                "code": "VBP5001",
                "user_type_id": self.env.ref("account.data_account_type_payable").id,
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
