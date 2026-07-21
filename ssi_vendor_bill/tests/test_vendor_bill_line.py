# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase
from psycopg2.errors import NotNullViolation

from odoo.tests import tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestVendorBillLine(YamlTransactionCase):
    def test_vendor_bill_line(self):
        self.run_yaml_scenario("test_data_vendor_bill_line.yaml")

    def _create_bill(self):
        payable_acc_type = self.env.ref("account.data_account_type_payable")
        expense_acc_type = self.env.ref("account.data_account_type_expenses")
        account = self.env["account.account"].create(
            {
                "code": "VBLP%d" % self.env["account.account"].search_count([]),
                "name": "P2 Vendor Bill Line Payable",
                "user_type_id": payable_acc_type.id,
                "reconcile": True,
            }
        )
        line_account = self.env["account.account"].create(
            {
                "code": "VBLE%d" % self.env["account.account"].search_count([]),
                "name": "P2 Vendor Bill Line Expense",
                "user_type_id": expense_acc_type.id,
            }
        )
        journal = self.env["account.journal"].create(
            {
                "name": "P2 Vendor Bill Line Journal",
                "code": "VBLJ%d" % self.env["account.journal"].search_count([]),
                "type": "purchase",
            }
        )
        bill_type = self.env["vendor_bill_type"].create(
            {
                "name": "P2 Vendor Bill Line Type",
                "code": "/",
                "journal_id": journal.id,
                "payable_account_id": account.id,
            }
        )
        vendor = self.env["res.partner"].create(
            {"name": "P2 Vendor Bill Line Partner", "is_company": True}
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
        return bill, line_account

    def test_compute_amount_with_and_without_tax(self):
        """Python murni -- pemicu P2 (L-04: tidak ada toleransi float di YAML
        untuk nilai moneter).

        Menguji dua skenario sekaligus dari issue #23 -- keduanya sama-sama
        soal presisi nilai moneter:
        1. ``amount_untaxed``/``amount_tax``/``amount_total`` dari 2 baris
           tanpa pajak (350.000 = 100.000 + 250.000, tax 0).
        2. Menambah 1 baris berpajak 11% lalu memanggil ``action_compute_tax``
           -- ``amount_tax`` harus sama persis dengan hasil
           ``account.tax.compute_all`` (bisa mengandung pembulatan mata uang)
           dan ``amount_total`` = untaxed + tax.
        """
        bill, line_account = self._create_bill()
        Line = self.env["vendor_bill.line"]
        line_1 = Line.create(
            {
                "vendor_bill_id": bill.id,
                "name": "Line 1",
                "account_id": line_account.id,
                "uom_quantity": 1,
                "price_unit": 100000.0,
            }
        )
        line_2 = Line.create(
            {
                "vendor_bill_id": bill.id,
                "name": "Line 2",
                "account_id": line_account.id,
                "uom_quantity": 1,
                "price_unit": 250000.0,
            }
        )
        self.assertEqual(bill.amount_untaxed, 350000.0)
        self.assertEqual(bill.amount_tax, 0.0)
        self.assertEqual(bill.amount_total, 350000.0)

        # `account_id` on the "tax" repartition line is what ends up on
        # `vendor_bill.tax.account_id` (required=True) once
        # `action_compute_tax` recomputes the tax lines automatically --
        # without it, `compute_all()` returns no account for the tax
        # portion and the auto-created line violates NOT NULL.
        tax = self.env["account.tax"].create(
            {
                "name": "P2 VAT 11%",
                "amount_type": "percent",
                "amount": 11.0,
                "type_tax_use": "purchase",
                "invoice_repartition_line_ids": [
                    (0, 0, {"factor_percent": 100, "repartition_type": "base"}),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "tax",
                            "account_id": line_account.id,
                        },
                    ),
                ],
                "refund_repartition_line_ids": [
                    (0, 0, {"factor_percent": 100, "repartition_type": "base"}),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "tax",
                            "account_id": line_account.id,
                        },
                    ),
                ],
            }
        )
        line_3 = Line.create(
            {
                "vendor_bill_id": bill.id,
                "name": "Line 3 (taxed)",
                "account_id": line_account.id,
                "uom_quantity": 1,
                "price_unit": 100000.0,
                "tax_ids": [(6, 0, [tax.id])],
            }
        )
        bill.action_compute_tax()

        expected_untaxed = (
            line_1.price_subtotal + line_2.price_subtotal + line_3.price_subtotal
        )
        taxes = tax.compute_all(
            line_3.price_unit,
            bill.currency_id,
            line_3.uom_quantity,
            product=line_3.product_id,
            partner=False,
        )
        expected_tax = sum(t.get("amount", 0.0) for t in taxes.get("taxes", []))

        self.assertEqual(bill.amount_untaxed, expected_untaxed)
        self.assertEqual(bill.amount_tax, expected_tax)
        self.assertEqual(bill.amount_total, expected_untaxed + expected_tax)

    @mute_logger("odoo.sql_db")
    def test_create_line_without_vendor_bill_id_violates_not_null_constraint(self):
        """Python murni -- pemicu P5 (L-22: `NotNullViolation` di luar 12
        tipe `expect_error`).

        ``vendor_bill_id`` wajib (`required=True`) tapi -- seperti sudah
        dibuktikan untuk `type_id` pada header `vendor_bill` di
        `test_vendor_bill.py` -- Odoo tidak menegakkan field wajib di layer
        Python saat `create()`; constraint NOT NULL di kolom database yang
        menolaknya sebagai `psycopg2.errors.NotNullViolation`.
        `mute_logger` membungkam baris ERROR NORMAL dari PostgreSQL di sini
        agar `oca_checklog_odoo` tidak menggagalkan CI walau test-nya lulus.
        """
        line_account = self.env["account.account"].create(
            {
                "code": "VBLE5%d" % self.env["account.account"].search_count([]),
                "name": "P5 Vendor Bill Line Expense",
                "user_type_id": self.env.ref("account.data_account_type_expenses").id,
            }
        )
        with self.assertRaises(NotNullViolation):
            self.env["vendor_bill.line"].create(
                {
                    "name": "Orphan Line",
                    "account_id": line_account.id,
                    "uom_quantity": 1,
                    "price_unit": 100000.0,
                }
            )
