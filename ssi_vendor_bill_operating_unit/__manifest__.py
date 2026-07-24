# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Vendor Bill + Operating Unit",
    "version": "14.0.1.1.0",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "contributors": [
        "Andhitia Rama <andhitia.r@gmail.com>",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": [
        "ssi_vendor_bill",
        "ssi_financial_accounting_operating_unit",
        "ssi_operating_unit_mixin",
        "web_tour",
    ],
    "data": [
        "security/res_group/vendor_bill.xml",
        "security/ir_rule/vendor_bill.xml",
        "views/vendor_bill_views.xml",
        "views/assets.xml",
    ],
    "demo": [],
}
