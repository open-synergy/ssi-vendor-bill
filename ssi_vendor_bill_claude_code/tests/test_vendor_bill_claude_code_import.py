# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
from unittest.mock import Mock, patch

from odoo.exceptions import AccessError, UserError
from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase

_BACKEND_MODEL = "vendor.bill.claude.code.backend"
_JOB_MODEL = "vendor.bill.claude.code.job"
_WIZARD_MODEL = "vendor.bill.claude.code.import.wizard"
_CALL_SERVICE_PATH = (
    "odoo.addons.ssi_vendor_bill_claude_code.models."
    "vendor_bill_claude_code_backend."
    "VendorBillClaudeCodeBackend._call_service"
)
_REQUESTS_GET_PATH = (
    "odoo.addons.ssi_vendor_bill_claude_code.models."
    "vendor_bill_claude_code_backend.requests.get"
)


def _sample_response(
    status="ok",
    unique_suffix="a",
    currency_code="IDR",
    product_id=None,
    account_id=None,
    tax_ids=None,
    warnings=None,
    partner_vat=None,
    partner_name="PT Sample Vendor",
):
    """Build a VendorBillExtractionRead-shaped dict for the given options."""
    resolved_line = {
        "name": "Service A",
        "quantity": 2.0,
        "price_unit": 100000.0,
        "product_id": product_id,
        "account_id": account_id,
        "tax_ids": list(tax_ids or []),
        "product_hint": None,
        "account_hint": None,
        "tax_hint": None,
        "price_subtotal": 200000.0,
    }
    hint_line = {
        "name": "Misc Charge",
        "quantity": 1.0,
        "price_unit": 50000.0,
        "product_id": None,
        "account_id": None,
        "tax_ids": [],
        "product_hint": "Unknown item",
        "account_hint": "Expense account",
        "tax_hint": "PPN 11%",
        "price_subtotal": 50000.0,
    }
    return {
        "id": "vb_test_%s" % unique_suffix,
        "status": status,
        "source_filename": "bill.pdf",
        "content_type": "application/pdf",
        "model": None,
        "matched": True,
        "created_at": "2026-01-05T00:00:00",
        "updated_at": "2026-01-05T00:00:00",
        "error": None,
        "result": {
            "bill": {
                "partner_id": None,
                "partner_name": partner_name,
                "partner_vat": partner_vat,
                "ref": "INV/2026/%s" % unique_suffix,
                "invoice_date": "2026-01-05",
                "invoice_date_due": "2026-02-05",
                "currency_code": currency_code,
                "lines": [resolved_line, hint_line],
                "amount_untaxed": 250000.0,
                "amount_tax": 0.0,
                "amount_total": 250000.0,
                "narration": "Imported by AI",
            },
            "matched": True,
            "warnings": list(warnings or []),
        },
    }


@tagged("post_install", "-at_install")
class TestVendorBillClaudeCodeImport(TransactionCase):
    def setUp(self):
        super().setUp()
        self.backend = self.env[_BACKEND_MODEL].create(
            {
                "name": "Test Backend",
                "code": "TEST-BACKEND",
                "base_url": "https://vendor-bill.example.com",
                "bearer_token": "test-token",
            }
        )
        self.purchase_journal = self.env["account.journal"].search(
            [("type", "=", "purchase")], limit=1
        )
        self.product = self.env["product.product"].search([], limit=1)

    def _make_move(self):
        return self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "journal_id": self.purchase_journal.id,
            }
        )

    def _make_attachment(self, filename="bill.pdf"):
        return self.env["ir.attachment"].create(
            {
                "name": filename,
                "datas": base64.b64encode(b"dummy pdf content"),
                "type": "binary",
            }
        )

    def _make_job(self, move, unique_suffix="a", filename="bill.pdf"):
        attachment = self._make_attachment(filename)
        return self.env[_JOB_MODEL].create(
            {
                "attachment_id": attachment.id,
                "source_filename": filename,
                "move_id": move.id,
                "backend_id": self.backend.id,
            }
        )

    # ------------------------------------------------------------------
    # _transform_result — pure seam, no HTTP
    # ------------------------------------------------------------------

    def test_transform_result_returns_move_vals_and_meta(self):
        response = _sample_response(
            product_id=42,
            account_id=7,
            tax_ids=[3],
            partner_vat="01.234.567.8-901.000",
        )
        move_vals, meta = self.backend._transform_result(response)

        self.assertEqual(move_vals["ref"], "INV/2026/a")
        self.assertEqual(move_vals["invoice_date"], "2026-01-05")
        self.assertEqual(move_vals["invoice_date_due"], "2026-02-05")
        self.assertEqual(move_vals["narration"], "Imported by AI")
        # partner_id is None on the bill -> key omitted
        self.assertNotIn("partner_id", move_vals)

        commands = move_vals["invoice_line_ids"]
        self.assertEqual(len(commands), 2)

        resolved = commands[0][2]
        self.assertEqual(resolved["name"], "Service A")
        self.assertEqual(resolved["quantity"], 2.0)
        self.assertEqual(resolved["price_unit"], 100000.0)
        self.assertEqual(resolved["product_id"], 42)
        self.assertEqual(resolved["account_id"], 7)
        self.assertEqual(resolved["tax_ids"], [(6, 0, [3])])

        hint = commands[1][2]
        self.assertEqual(hint["name"], "Misc Charge")
        self.assertNotIn("product_id", hint)
        self.assertNotIn("account_id", hint)
        self.assertNotIn("tax_ids", hint)

        self.assertEqual(meta["currency_code"], "IDR")
        self.assertEqual(meta["partner_name"], "PT Sample Vendor")
        self.assertEqual(meta["partner_vat"], "01.234.567.8-901.000")
        self.assertEqual(meta["warnings"], [])
        self.assertTrue(meta["matched"])
        self.assertEqual(meta["external_id"], "vb_test_a")
        self.assertEqual(meta["external_status"], "ok")

    def test_transform_result_empty_line_name_defaults_na(self):
        response = _sample_response()
        response["result"]["bill"]["lines"][0]["name"] = None
        move_vals, _meta = self.backend._transform_result(response)
        self.assertEqual(move_vals["invoice_line_ids"][0][2]["name"], "N/A")

    def test_transform_result_failed_status_raises(self):
        response = _sample_response(status="failed")
        response["error"] = "Could not read the file"
        with self.assertRaises(UserError):
            self.backend._transform_result(response)

    # ------------------------------------------------------------------
    # Job _run — mocked HTTP call
    # ------------------------------------------------------------------

    def test_run_success_writes_move(self):
        if not self.purchase_journal:
            self.skipTest("No purchase journal found in test environment")
        move = self._make_move()
        job = self._make_job(move, unique_suffix="success")
        with patch(
            _CALL_SERVICE_PATH,
            return_value=_sample_response(
                unique_suffix="success",
                product_id=self.product.id if self.product else None,
            ),
        ):
            job._run()
        self.assertEqual(job.state, "done")
        self.assertEqual(job.external_id, "vb_test_success")
        self.assertEqual(len(move.invoice_line_ids), 2)
        self.assertEqual(move.ref, "INV/2026/success")

    def test_run_resolves_partner_by_vat(self):
        if not self.purchase_journal:
            self.skipTest("No purchase journal found in test environment")
        vendor = self.env["res.partner"].create(
            {"name": "Unique VAT Vendor", "vat": "VBCLAUDE-VAT-1"}
        )
        move = self._make_move()
        job = self._make_job(move, unique_suffix="vat")
        with patch(
            _CALL_SERVICE_PATH,
            return_value=_sample_response(
                unique_suffix="vat", partner_vat="VBCLAUDE-VAT-1"
            ),
        ):
            job._run()
        self.assertEqual(move.partner_id, vendor)

    def test_run_need_review_on_warnings(self):
        if not self.purchase_journal:
            self.skipTest("No purchase journal found in test environment")
        move = self._make_move()
        job = self._make_job(move, unique_suffix="review")
        with patch(
            _CALL_SERVICE_PATH,
            return_value=_sample_response(
                unique_suffix="review",
                warnings=["Vendor not found"],
            ),
        ):
            job._run()
        self.assertEqual(job.state, "need_review")
        # move still written despite need_review
        self.assertEqual(len(move.invoice_line_ids), 2)

    def test_run_error_path_sets_failed(self):
        move = self._make_move()
        job = self._make_job(move, unique_suffix="error")
        with patch(_CALL_SERVICE_PATH, side_effect=UserError("boom")):
            job._run()
        self.assertEqual(job.state, "failed")
        self.assertIn("boom", job.error_message)
        self.assertFalse(move.invoice_line_ids)

    def test_retry_only_allowed_from_failed_or_need_review(self):
        move = self._make_move()
        job = self._make_job(move, unique_suffix="retryguard")
        with self.assertRaises(UserError):
            job.action_retry()

    # ------------------------------------------------------------------
    # Wizard enqueue path — does NOT call the service synchronously
    # ------------------------------------------------------------------

    def test_wizard_import_enqueues_job_not_sync_call(self):
        move = self._make_move()
        wizard = self.env[_WIZARD_MODEL].create(
            {
                "move_id": move.id,
                "backend_id": self.backend.id,
                "data_file": base64.b64encode(b"dummy pdf content"),
                "filename": "enqueue_test.pdf",
            }
        )
        with patch(_CALL_SERVICE_PATH) as mocked_call:
            action = wizard.action_import()
            mocked_call.assert_not_called()

        jobs = self.env[_JOB_MODEL].search([("move_id", "=", move.id)])
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs.state, "queued")
        self.assertEqual(jobs.backend_id, self.backend)
        self.assertEqual(jobs.attachment_id.res_model, _JOB_MODEL)
        self.assertEqual(jobs.attachment_id.res_id, jobs.id)
        self.assertEqual(action["tag"], "display_notification")
        self.assertEqual(
            action["params"]["next"]["type"], "ir.actions.act_window_close"
        )

    def test_wizard_preselect_backend_from_journal_default(self):
        if not self.purchase_journal:
            self.skipTest("No purchase journal found in test environment")
        self.purchase_journal.write(
            {"default_claude_code_backend_id": self.backend.id}
        )
        move = self._make_move()
        form = Form(
            self.env[_WIZARD_MODEL].with_context(default_move_id=move.id)
        )
        self.assertEqual(form.backend_id, self.backend)

    # ------------------------------------------------------------------
    # Test Connection — mocked HTTP
    # ------------------------------------------------------------------

    def test_test_connection_success(self):
        health_response = Mock(status_code=200)
        health_response.json.return_value = {"status": "ok", "version": "0.2.0"}
        me_response = Mock(status_code=200)
        me_response.json.return_value = {"sub": "svc-account"}
        with patch(_REQUESTS_GET_PATH, side_effect=[health_response, me_response]):
            result = self.backend.action_test_connection()
        self.assertEqual(result["params"]["type"], "success")

    def test_test_connection_unauthorized_raises(self):
        health_response = Mock(status_code=200)
        health_response.json.return_value = {"status": "ok", "version": "0.2.0"}
        me_response = Mock(status_code=401)
        with patch(_REQUESTS_GET_PATH, side_effect=[health_response, me_response]):
            with self.assertRaises(UserError):
                self.backend.action_test_connection()

    # ------------------------------------------------------------------
    # Security
    # ------------------------------------------------------------------

    def test_non_configurator_cannot_create_backend(self):
        demo_user = self.env.ref("base.user_demo")
        with self.assertRaises(AccessError):
            self.env[_BACKEND_MODEL].with_user(demo_user).create(
                {
                    "name": "Unauthorized Backend",
                    "code": "UNAUTH-TEST",
                    "base_url": "https://vendor-bill.example.com",
                    "bearer_token": "test-token",
                }
            )
