# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Vendor Bill + Operating Unit",
    "version": "14.0.1.0.2",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "contributors": [
        "Andhitia Rama <andhitia.r@gmail.com>",
    ],
    "license": "AGPL-3",
    # Temporarily disabled: open-synergy/ssi-vendor-bill#22 rebuilt
    # `vendor_bill` as a standalone transactional model, so it no longer
    # carries `operating_unit_id` (previously inherited for free from
    # `account.move` via `ssi_financial_accounting_operating_unit`), and
    # `views/vendor_bill_views.xml` in this module now points at a field
    # that does not exist. Re-enable once open-synergy/ssi-vendor-bill#25
    # reworks this module's model/view for the new `vendor_bill`.
    "installable": False,
    "application": False,
    "depends": [
        "ssi_vendor_bill",
        "ssi_financial_accounting_operating_unit",
    ],
    "data": [
        "security/res_group/vendor_bill.xml",
        "security/ir_rule/vendor_bill.xml",
        "views/vendor_bill_views.xml",
    ],
    "demo": [],
}
