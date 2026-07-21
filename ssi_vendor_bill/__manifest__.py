# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Vendor Bill",
    "version": "14.0.1.1.1",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "contributors": [
        "Andhitia Rama <andhitia.r@gmail.com>",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": [
        "ssi_financial_accounting",
    ],
    "data": [
        "security/ir_module_category/vendor_bill.xml",
        "security/res_groups/vendor_bill.xml",
        "security/ir.model.access.csv",
        "security/ir_rule/vendor_bill.xml",
        "views/vendor_bill_views.xml",
    ],
    "demo": [],
    "uninstall_hook": "uninstall_hook",
}
