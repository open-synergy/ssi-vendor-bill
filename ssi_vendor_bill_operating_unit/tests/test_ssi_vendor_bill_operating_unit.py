# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSSIVendorBillOperatingUnit(YamlTransactionCase):
    """Cover the Operating Unit field added to ``vendor_bill`` by this
    module: default value, propagation to the accounting entry, record
    rule visibility, and the local-group-implies-OU-group relation.
    """

    def test_ssi_vendor_bill_operating_unit(self):
        """Run the Operating Unit YAML scenarios for ``vendor_bill``."""
        self.run_yaml_scenario("vendor_bill_ou.yaml")

    def _create_bill(self, operating_unit=False, prefix="P3"):
        """Shared fixture for the python-pure tests below. Built fresh here
        (not taken from the YAML registry, which only lives during
        ``run_yaml_scenario``).
        """
        payable_acc_type = self.env.ref("account.data_account_type_payable")
        expense_acc_type = self.env.ref("account.data_account_type_expenses")
        payable_account = self.env["account.account"].create(
            {
                "code": "%sP%d"
                % (prefix, self.env["account.account"].search_count([])),
                "name": "%s Vendor Bill OU Payable" % prefix,
                "user_type_id": payable_acc_type.id,
                "reconcile": True,
            }
        )
        expense_account = self.env["account.account"].create(
            {
                "code": "%sE%d"
                % (prefix, self.env["account.account"].search_count([])),
                "name": "%s Vendor Bill OU Expense" % prefix,
                "user_type_id": expense_acc_type.id,
            }
        )
        journal = self.env["account.journal"].create(
            {
                "name": "%s Vendor Bill OU Journal" % prefix,
                "code": "%sJ%d"
                % (prefix, self.env["account.journal"].search_count([])),
                "type": "purchase",
            }
        )
        bill_type = self.env["vendor_bill_type"].create(
            {
                "name": "%s Vendor Bill OU Type" % prefix,
                "code": "/",
                "journal_id": journal.id,
                "payable_account_id": payable_account.id,
            }
        )
        vendor = self.env["res.partner"].create(
            {"name": "%s Vendor Bill OU Vendor" % prefix, "is_company": True}
        )
        bill = self.env["vendor_bill"].create(
            {
                "type_id": bill_type.id,
                "partner_id": vendor.id,
                "operating_unit_id": operating_unit.id if operating_unit else False,
                "date": "2024-01-15",
                "date_due": "2024-02-15",
                "currency_id": self.env.ref("base.USD").id,
                "pricelist_id": self.env.ref("product.list0").id,
                "journal_id": journal.id,
                "payable_account_id": payable_account.id,
            }
        )
        line_1 = self.env["vendor_bill.line"].create(
            {
                "vendor_bill_id": bill.id,
                "name": "%s Line 1" % prefix,
                "account_id": expense_account.id,
                "uom_quantity": 1,
                "price_unit": 100000.0,
            }
        )
        return bill, line_1

    def test_every_move_line_shares_the_bills_operating_unit(self):
        """Python murni -- pemicu P3 (L-06: perbandingan o2m berbasis
        `set`, tidak ada assert per-baris; membaca isi SETIAP baris
        `move_id.line_ids` butuh iterasi Python, tidak bisa diungkapkan
        sebagai satu assert YAML).

        Setelah `action_open`, baris hutang (dari `vendor_bill`) maupun
        baris beban (dari `vendor_bill.line`) pada `move_id.line_ids` harus
        seluruhnya membawa `operating_unit_id` yang sama dengan dokumen
        induknya -- bukan hanya salah satu baris.
        """
        ou_partner = self.env["res.partner"].create(
            {"name": "P3 Vendor Bill OU Partner"}
        )
        ou = self.env["operating.unit"].create(
            {
                "name": "P3 Vendor Bill Operating Unit",
                "code": "VBOUP3",
                "partner_id": ou_partner.id,
            }
        )
        bill, _line_1 = self._create_bill(operating_unit=ou, prefix="P3")
        bill.with_context(bypass_policy_check=True).action_open()

        self.assertEqual(bill.state, "open")
        self.assertTrue(bill.move_id)
        self.assertTrue(bill.move_id.line_ids)

        for move_line in bill.move_id.line_ids:
            self.assertEqual(
                move_line.operating_unit_id,
                ou,
                "Move line %s does not carry the bill's operating unit"
                % move_line.name,
            )

    def test_tax_line_prepare_standard_ml_carries_operating_unit(self):
        """Python murni -- pemicu P1 (L-01: `action: call` YAML membuang
        nilai balik method -- `_prepare_standard_ml()` adalah method
        internal mixin yang tidak pernah dipanggil lewat tombol UI/tombol
        aksi, hanya lewat method Python lain, sehingga nilai balik dict-nya
        hanya bisa di-assert dengan memanggilnya langsung).

        Memverifikasi bahwa override `vendor_bill.tax._prepare_standard_ml()`
        (open-synergy/ssi-vendor-bill#25) menyalin `operating_unit_id` dari
        `vendor_bill_id` ke dict yang dipakai untuk membuat journal item
        pajak -- tanpa perlu menjalankan seluruh pipeline compute-tax +
        posting.
        """
        ou_partner = self.env["res.partner"].create(
            {"name": "P1 Vendor Bill Tax OU Partner"}
        )
        ou = self.env["operating.unit"].create(
            {
                "name": "P1 Vendor Bill Tax Operating Unit",
                "code": "VBOUP1T",
                "partner_id": ou_partner.id,
            }
        )
        bill, _line_1 = self._create_bill(operating_unit=ou, prefix="P1T")

        tax_account = self.env["account.account"].create(
            {
                "code": "P1TX%d" % self.env["account.account"].search_count([]),
                "name": "P1 Vendor Bill Tax Account",
                "user_type_id": self.env.ref(
                    "account.data_account_type_current_liabilities"
                ).id,
            }
        )
        tax = self.env["account.tax"].create(
            {
                "name": "P1 Vendor Bill Tax 10%",
                "amount": 10.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
            }
        )
        tax_line = self.env["vendor_bill.tax"].create(
            {
                "vendor_bill_id": bill.id,
                "name": "P1 Vendor Bill Tax Line",
                "tax_id": tax.id,
                "account_id": tax_account.id,
                "base_amount": 100000.0,
                "tax_amount": 10000.0,
            }
        )

        vals = tax_line._prepare_standard_ml()

        self.assertEqual(vals["operating_unit_id"], ou.id)
