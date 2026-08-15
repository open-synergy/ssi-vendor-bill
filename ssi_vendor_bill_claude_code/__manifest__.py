# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "SSI Vendor Bill Claude Code Import",
    "version": "14.0.1.1.1",
    "summary": "Import vendor bills from PDF/PNG using the "
    "odoo-vendor-bill-claude-code-extract AI service, processed "
    "asynchronously via queue_job",
    "category": "Accounting",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "contributors": [
        "Andhitia Rama <andhitia.r@gmail.com>",
    ],
    "website": "https://simetri-sinergi.id",
    "license": "AGPL-3",
    "depends": [
        "ssi_financial_accounting",
        "queue_job",
        "web_tour",
    ],
    "external_dependencies": {
        "python": ["requests"],
    },
    "data": [
        "security/res_groups/vendor_bill_claude_code_backend.xml",
        "security/ir_model_access/vendor_bill_claude_code_backend.xml",
        "security/ir_model_access/vendor_bill_claude_code_job.xml",
        "security/ir_model_access/import_vendor_bill_claude_code.xml",
        "data/ir_sequence.xml",
        "views/vendor_bill_claude_code_backend_views.xml",
        "views/vendor_bill_claude_code_job_views.xml",
        "wizards/import_vendor_bill_claude_code_views.xml",
        "views/account_move_views.xml",
        "views/account_journal_views.xml",
        "views/assets.xml",
    ],
    "installable": True,
    "application": False,
}
