# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64

# HttpSavepointCase — NOT HttpCase. In 14.0, HttpCase does not set up
# cls.env in setUpClass, so fixtures written there would fail before the
# browser ever starts.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiVendorBillClaudeCodeJob(HttpSavepointCase):
    """Tour tests for the ``vendor.bill.claude.code.job`` work
    instructions: opening the AI Import wizard, and retrying a job."""

    @classmethod
    def setUpClass(cls):
        """Create the draft vendor bill and the failed job the tours use."""
        super().setUpClass()
        cls.admin = cls.env.ref("base.user_admin")
        journal = cls.env["account.journal"].search(
            [("type", "=", "purchase")], limit=1
        )
        partner = cls.env["res.partner"].create({"name": "Tour AI Import Vendor"})
        cls.move = cls.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "journal_id": journal.id,
                "partner_id": partner.id,
            }
        )
        attachment = cls.env["ir.attachment"].create(
            {
                "name": "TOUR-RETRY-FILE.pdf",
                "datas": base64.b64encode(b"tour dummy pdf content"),
                "type": "binary",
            }
        )
        backend = cls.env["vendor.bill.claude.code.backend"].create(
            {
                "name": "Tour Job Backend",
                "code": "TOUR-JOB-BACKEND",
                "base_url": "https://vendor-bill-tour.example.com",
                "bearer_token": "tour-token",
            }
        )
        cls.failed_job = cls.env["vendor.bill.claude.code.job"].create(
            {
                "attachment_id": attachment.id,
                "source_filename": "TOUR-RETRY-FILE.pdf",
                "move_id": cls.move.id,
                "backend_id": backend.id,
            }
        )
        cls.failed_job.write(
            {"state": "failed", "error_message": "Simulated tour failure"}
        )

    def test_import(self):
        """Run the AI Import tour for ``vendor.bill.claude.code.job``.

        IK: docs/vendor_bill_claude_code_job/01-import.md

        Boundary (patterns.md §Q): stops at "the wizard is open" and
        discards it instead of uploading a file and clicking Import — a
        real file cannot be attached to a hidden ``<input type="file">``
        reliably across browsers. See the tour's own comment for detail.
        """
        self.start_tour(
            "/web",
            "ssi_vendor_bill_claude_code_vendor_bill_claude_code_job_import",
            login="admin",
        )

    def test_retry(self):
        """Run the retry tour for ``vendor.bill.claude.code.job``.

        IK: docs/vendor_bill_claude_code_job/02-retry.md
        """
        self.start_tour(
            "/web",
            "ssi_vendor_bill_claude_code_vendor_bill_claude_code_job_retry",
            login="admin",
        )
