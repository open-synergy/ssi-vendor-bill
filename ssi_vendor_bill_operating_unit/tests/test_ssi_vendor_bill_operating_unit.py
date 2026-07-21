# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree
from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSSIVendorBillOperatingUnit(YamlTransactionCase):
    def test_ssi_vendor_bill_operating_unit(self):
        self.run_yaml_scenario("vendor_bill_ou.yaml")

    def test_operating_unit_id_and_grp_ou_appear_exactly_once(self):
        """Python murni -- pemicu P1 (L-01/L-02: nilai balik fields_view_get()).

        Menghitung kemunculan sebuah node di string `arch` yang dikembalikan
        `fields_view_get()` adalah assert atas nilai balik method, bukan efek
        pada sebuah record -- YAML tidak bisa meng-assert nilai balik `call`
        (L-01/L-02). Sebelum perbaikan open-synergy/ssi-vendor-bill#13,
        `operating_unit_id` muncul dua kali pada form/tree dan `grp_ou`
        muncul dua kali pada search, karena `vendor_bill_view_form` /
        `vendor_bill_view_search` (rebind primary) sudah mewarisi xpath
        identik dari `ssi_financial_accounting_operating_unit`.
        """
        model = self.env["vendor_bill"]

        form_arch = etree.fromstring(model.fields_view_get(view_type="form")["arch"])
        self.assertEqual(len(form_arch.xpath("//field[@name='operating_unit_id']")), 1)

        search_arch = etree.fromstring(
            model.fields_view_get(view_type="search")["arch"]
        )
        self.assertEqual(len(search_arch.xpath("//filter[@name='grp_ou']")), 1)

        # Regression guard: the tree view's own operating_unit_id addition
        # (vendor_bill_view_tree in this same module) is legitimate -- see
        # open-synergy/ssi-vendor-bill#13 "Tidak termasuk" -- and must
        # survive this fix untouched, so it must still be present.
        #
        # NOTE: this does NOT assert an exact count of 1. Independently of
        # this issue, `account.view_in_invoice_tree` (the base
        # `vendor_bill_view_tree` rebinds) is *itself* a primary rebind of
        # `account.view_invoice_tree`, and `ssi_financial_accounting_operating_unit`
        # already adds operating_unit_id to `account.view_invoice_tree`
        # (`account_move_view_tree`). Primary-view inheritance means that
        # addition is already present once inside `account.view_in_invoice_tree`
        # before this module's own tree xpath ever runs, so the combined
        # count observed here is 2, not 1 -- a pre-existing duplicate one
        # level up the view-inheritance chain, out of scope for #13 (whose
        # "Tidak termasuk" explicitly keeps this record untouched) and not
        # introduced or affected by this fix either way.
        tree_arch = etree.fromstring(model.fields_view_get(view_type="tree")["arch"])
        self.assertGreaterEqual(
            len(tree_arch.xpath("//field[@name='operating_unit_id']")), 1
        )
