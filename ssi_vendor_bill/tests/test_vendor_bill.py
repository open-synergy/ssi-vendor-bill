# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree
from odoo_yaml_test import YamlTransactionCase

from odoo import fields
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestVendorBill(YamlTransactionCase):
    def test_vendor_bill(self):
        self.run_yaml_scenario("test_data_vendor_bill.yaml")

    def test_form_view_has_exactly_one_policies_page(self):
        """Python murni -- pemicu P1 (L-01/L-02: nilai balik fields_view_get()).

        Menghitung kemunculan sebuah node di string `arch` yang dikembalikan
        `fields_view_get()` adalah assert atas nilai balik method, bukan efek
        pada sebuah record -- YAML tidak bisa meng-assert nilai balik `call`
        (L-01/L-02). Sebelum perbaikan open-synergy/ssi-vendor-bill#17, arch
        `vendor_bill_view_form` menduplikasi seluruh isi yang sudah datang
        lewat pewarisan `account.view_move_form` <-
        `ssi_financial_accounting.account_move_view_form`, menghasilkan dua
        tab "Policies".
        """
        arch = etree.fromstring(
            self.env["vendor_bill"].fields_view_get(view_type="form")["arch"]
        )
        self.assertEqual(len(arch.xpath("//page[@name='policy']")), 1)
        self.assertEqual(
            len(
                arch.xpath(
                    "//button[@name='action_post']" "[contains(@attrs, 'confirm_ok')]"
                )
            ),
            1,
        )
        self.assertEqual(
            len(
                arch.xpath(
                    "//button[@name='button_draft']" "[contains(@attrs, 'restart_ok')]"
                )
            ),
            1,
        )
        self.assertEqual(
            len(
                arch.xpath(
                    "//button[@name='button_cancel']" "[contains(@attrs, 'cancel_ok')]"
                )
            ),
            1,
        )

    def test_chatter_recordsets_match_account_move(self):
        """Python murni -- pemicu P3 (L-06: assert isi recordset x2m lintas model).

        L-06: perbandingan o2m/m2m di YAML hanya bisa dilakukan terhadap
        record/xml_id tetap (`expected_records`/`expected_xml_ids`), bukan
        terhadap x2m milik record LAIN yang baru dibuat di skenario yang
        sama -- di sini `vendor_bill.message_ids` harus identik dengan
        `account.move.message_ids` untuk id yang sama, sebelum dan sesudah
        `action_post`. Lihat open-synergy/ssi-vendor-bill#16.
        """
        vendor = self.env["res.partner"].create(
            {"name": "P3 Chatter Vendor", "is_company": True}
        )
        journal = self.env["account.journal"].create(
            {
                "name": "P3 Chatter Purchase Journal",
                "code": "PCJ1",
                "type": "purchase",
            }
        )
        expense_account = self.env["account.account"].create(
            {
                "name": "P3 Chatter Test Expense",
                "code": "P3CHT1",
                "user_type_id": self.env.ref("account.data_account_type_expenses").id,
            }
        )
        bill = self.env["vendor_bill"].create(
            {
                "partner_id": vendor.id,
                "journal_id": journal.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Line",
                            "quantity": 1,
                            "price_unit": 10000.0,
                            "account_id": expense_account.id,
                        },
                    )
                ],
            }
        )
        move = self.env["account.move"].browse(bill.id)

        self.assertEqual(bill.account_move_id, move)
        self.assertEqual(bill.message_ids, move.message_ids)
        self.assertEqual(bill.message_follower_ids, move.message_follower_ids)
        self.assertEqual(bill.message_attachment_count, move.message_attachment_count)

        bill.action_post()
        bill.invalidate_cache()
        move.invalidate_cache()

        self.assertEqual(bill.message_ids, move.message_ids)
        self.assertEqual(bill.message_follower_ids, move.message_follower_ids)
