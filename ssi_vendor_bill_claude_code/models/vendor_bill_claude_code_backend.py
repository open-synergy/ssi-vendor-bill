# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import hashlib
import mimetypes

import requests

from odoo import _, fields, models
from odoo.exceptions import UserError

# odoo-vendor-bill-claude-code-extract default MAX_UPLOAD_BYTES (~15 MiB).
# The service itself enforces this limit; checking it client-side avoids
# uploading a file that the service will reject anyway.
_MAX_UPLOAD_BYTES = 15 * 1024 * 1024


class VendorBillClaudeCodeBackend(models.Model):
    """
    Represents a connection profile to an
    ``odoo-vendor-bill-claude-code-extract`` service (FastAPI, Bearer token
    resource server) that extracts vendor bills from PDF/PNG files.

    Holds the base URL and static bearer token used to call the
    ``POST /api/v1/vendor-bills`` endpoint, and provides the seams used by
    the async import job: ``_call_service`` (HTTP) and ``_transform_result``
    (pure, no HTTP) to convert the service response into the
    ``(move_vals, meta)`` pair written onto an ``account.move`` vendor bill.
    """

    _name = "vendor.bill.claude.code.backend"
    _inherit = ["mixin.master_data"]
    _description = "Vendor Bill Claude Code Import Backend"

    base_url = fields.Char(
        string="Base URL",
        required=True,
        help="Base URL of the odoo-vendor-bill-claude-code-extract service, "
        "without trailing slash (e.g. https://vendor-bill.example.com). The "
        "wizard calls POST {base_url}/api/v1/vendor-bills to upload the "
        "vendor bill file.",
    )
    bearer_token = fields.Char(
        string="Bearer Token",
        required=True,
        help="Static bearer token sent as 'Authorization: Bearer <token>' on "
        "every call to the service (e.g. an Authentik long-lived token). The "
        "token carries the 'odoo_instance' claim the service uses to resolve "
        "master data back to this Odoo.",
    )
    model = fields.Char(
        string="Extraction Model",
        help="Optional Claude model override sent as the 'model' form field. "
        "Leave empty to use the service's default model.",
    )
    timeout_seconds = fields.Integer(
        string="Timeout (seconds)",
        default=600,
        required=True,
        help="Maximum time to wait for the extraction response. The service "
        "itself may take up to CLAUDE_EXTRACTION_TIMEOUT_SECONDS (default "
        "600s) to analyze a single file.",
    )
    verify_ssl = fields.Boolean(
        string="Verify SSL",
        default=True,
        help="Verify the service's TLS certificate. Disable only for "
        "self-signed certificates in a development environment.",
    )

    def _get_headers(self, idempotency_key=None):
        """Build the HTTP headers used to call the extraction service."""
        self.ensure_one()
        headers = {"Authorization": "Bearer %s" % self.bearer_token}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    def _call_service(self, data_file, filename):
        """Upload a vendor bill file and return the raw JSON response.

        :param data_file: raw file bytes (already base64-decoded)
        :param filename: original filename, used for content-type guessing
            and the multipart filename
        :return: parsed JSON body of the ``VendorBillExtractionRead`` response
        :rtype: dict
        """
        self.ensure_one()
        if len(data_file) > _MAX_UPLOAD_BYTES:
            error_message = (
                _(
                    """
Context: Upload vendor bill file to claude-code extraction service
Database ID: %s
Problem: File '%s' is %d bytes, larger than the service limit of %d bytes
Solution: Split the file or use a smaller export of the vendor bill
"""
                )
                % (self.id, filename, len(data_file), _MAX_UPLOAD_BYTES)
            )
            raise UserError(error_message)

        content_type = mimetypes.guess_type(filename or "")[0] or (
            "application/octet-stream"
        )
        idempotency_key = hashlib.sha256(data_file).hexdigest()

        try:
            response = requests.post(
                "%s/api/v1/vendor-bills" % self.base_url.rstrip("/"),
                files={"file": (filename or "vendor_bill", data_file, content_type)},
                data={"model": self.model} if self.model else None,
                headers=self._get_headers(idempotency_key=idempotency_key),
                timeout=self.timeout_seconds,
                verify=self.verify_ssl,
            )
        except requests.exceptions.RequestException as exc:
            error_message = (
                _(
                    """
Context: Upload vendor bill file to claude-code extraction service
Database ID: %s
Problem: Could not reach the backend '%s': %s
Solution: Check the Base URL, network connectivity, and that the service \
is running, then retry
"""
                )
                % (self.id, self.base_url, str(exc))
            )
            raise UserError(error_message) from exc

        if response.status_code not in (200, 201):
            error_message = (
                _(
                    """
Context: Upload vendor bill file to claude-code extraction service
Database ID: %s
Problem: The backend '%s' returned HTTP %d: %s
Solution: Verify the Bearer Token and Base URL configuration, or check the \
service logs
"""
                )
                % (self.id, self.base_url, response.status_code, response.text[:500])
            )
            raise UserError(error_message)

        try:
            return response.json()
        except ValueError as exc:
            error_message = (
                _(
                    """
Context: Upload vendor bill file to claude-code extraction service
Database ID: %s
Problem: The backend '%s' returned a non-JSON response
Solution: Check the service logs for the actual error
"""
                )
                % (self.id, self.base_url)
            )
            raise UserError(error_message) from exc

    def _transform_result(self, response_json):
        """Convert a ``VendorBillExtractionRead`` JSON body into the pair
        ``(move_vals, meta)`` written onto an ``account.move`` vendor bill.

        This is the pure seam for testing: no HTTP call, just a dict-in
        dict-out transformation mirroring the library's
        ``core/exporters.py::to_odoo_values``. Resolved ``*_id`` values are
        included; ``None`` ids are omitted so Odoo onchange fills defaults or
        the user completes them manually.

        :param response_json: parsed JSON body returned by ``_call_service``
        :return: ``(move_vals, meta)`` where ``move_vals`` is ready for
            ``account.move.write`` and ``meta`` carries currency/partner
            hints and the external extraction status
        :rtype: tuple
        """
        self.ensure_one()
        if response_json.get("status") == "failed":
            error_message = (
                _(
                    """
Context: Extract vendor bill via claude-code extraction service
Database ID: %s
Problem: extraction failed: %s
Solution: Check the source file quality (scan/photo legibility) and retry
"""
                )
                % (self.id, response_json.get("error") or _("unknown error"))
            )
            raise UserError(error_message)

        result = response_json.get("result") or {}
        bill = result.get("bill") or {}

        move_vals = {
            "invoice_line_ids": [
                self._prepare_line_command(line) for line in (bill.get("lines") or [])
            ],
        }
        if bill.get("partner_id") is not None:
            move_vals["partner_id"] = bill["partner_id"]
        if bill.get("ref"):
            move_vals["ref"] = bill["ref"]
        if bill.get("invoice_date"):
            move_vals["invoice_date"] = bill["invoice_date"]
        if bill.get("invoice_date_due"):
            move_vals["invoice_date_due"] = bill["invoice_date_due"]
        if bill.get("narration"):
            move_vals["narration"] = bill["narration"]

        meta = {
            "currency_code": bill.get("currency_code"),
            "partner_name": bill.get("partner_name"),
            "partner_vat": bill.get("partner_vat"),
            "warnings": result.get("warnings") or [],
            "matched": result.get("matched", False),
            "external_id": response_json.get("id"),
            "external_status": response_json.get("status"),
        }
        return (move_vals, meta)

    def _prepare_line_command(self, line):
        """Build one One2many ``(0, 0, vals)`` command for
        ``invoice_line_ids`` from an extracted line, mirroring the library's
        ``_line_command``. Unresolved ids are omitted."""
        self.ensure_one()
        vals = {
            "name": line.get("name") or "N/A",
            "quantity": line.get("quantity", 1.0),
            "price_unit": line.get("price_unit", 0.0),
        }
        if line.get("product_id") is not None:
            vals["product_id"] = line["product_id"]
        if line.get("account_id") is not None:
            vals["account_id"] = line["account_id"]
        if line.get("tax_ids"):
            vals["tax_ids"] = [(6, 0, list(line["tax_ids"]))]
        return (0, 0, vals)

    def action_test_connection(self):
        for record in self.sudo():
            result = record._test_connection()
        return result

    def _test_connection(self):
        """Call GET /api/v1/health then GET /api/v1/me to verify the Base
        URL and Bearer Token, and report the outcome to the user."""
        self.ensure_one()
        base_url = self.base_url.rstrip("/")

        try:
            health_response = requests.get(
                "%s/api/v1/health" % base_url,
                timeout=10,
                verify=self.verify_ssl,
            )
        except requests.exceptions.RequestException as exc:
            error_message = (
                _(
                    """
Context: Test connection to claude-code extraction service
Database ID: %s
Problem: Could not reach '%s/api/v1/health': %s
Solution: Check the Base URL and network connectivity
"""
                )
                % (self.id, base_url, str(exc))
            )
            raise UserError(error_message) from exc

        if health_response.status_code != 200:
            error_message = (
                _(
                    """
Context: Test connection to claude-code extraction service
Database ID: %s
Problem: '%s/api/v1/health' returned HTTP %d
Solution: Check that the service is running and the Base URL is correct
"""
                )
                % (self.id, base_url, health_response.status_code)
            )
            raise UserError(error_message)

        try:
            me_response = requests.get(
                "%s/api/v1/me" % base_url,
                headers=self._get_headers(),
                timeout=10,
                verify=self.verify_ssl,
            )
        except requests.exceptions.RequestException as exc:
            error_message = (
                _(
                    """
Context: Test connection to claude-code extraction service
Database ID: %s
Problem: Could not reach '%s/api/v1/me': %s
Solution: Check the Base URL and network connectivity
"""
                )
                % (self.id, base_url, str(exc))
            )
            raise UserError(error_message) from exc

        if me_response.status_code != 200:
            error_message = (
                _(
                    """
Context: Test connection to claude-code extraction service
Database ID: %s
Problem: '%s/api/v1/me' returned HTTP %d — the Bearer Token was rejected
Solution: Verify the Bearer Token configured on this backend
"""
                )
                % (self.id, base_url, me_response.status_code)
            )
            raise UserError(error_message)

        health_data = health_response.json()
        me_data = me_response.json()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Connection Successful"),
                "message": _("claude-code extraction service %s — authenticated as %s")
                % (
                    health_data.get("version") or "?",
                    me_data.get("sub") or me_data.get("name") or "?",
                ),
                "type": "success",
                "sticky": False,
            },
        }
