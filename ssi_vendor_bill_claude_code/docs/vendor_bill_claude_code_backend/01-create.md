# Create Vendor Bill AI Backend

> **Module:** `ssi_vendor_bill_claude_code`\
> **Model:** `vendor.bill.claude.code.backend`\
> **Menu:** Financial Accounting > Configuration > Account > Vendor Bill AI Backends\
> **Actor:** user in group `Vendor Bill Claude Code Import`\
> **Inline Actions:** `action_test_connection` (Test Connection)

## Pre-Condition

- **Access:** User is in group `Vendor Bill Claude Code Import`.

## Flow

1. Open the **Financial Accounting > Configuration > Account > Vendor Bill AI Backends**
   menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Code** _(required)_: unique identifier for this backend.
   - **Name** _(required)_: descriptive name for this backend, shown wherever a backend
     is selected (e.g. on the AI Import wizard).
4. On the **Claude Code Settings** tab, fill in:
   - **Base URL** _(required)_: base URL of the `odoo-vendor-bill-claude-code-extract`
     service, without a trailing slash.
   - **Bearer Token** _(required)_: static bearer token sent as
     `Authorization: Bearer <token>` on every call to the service.
   - **Extraction Model**: optional Claude model override. Leave empty to use the
     service's default model.
   - **Timeout (seconds)**: maximum time to wait for the extraction response.
     Automatically defaulted to **600**.
   - **Verify SSL**: verifies the service's TLS certificate. Automatically checked;
     uncheck only for a self-signed certificate in a development environment.
5. Click **Test Connection** in the header to verify the Base URL and Bearer Token are
   correct before saving. A success notification shows the service version and the
   authenticated identity; a failure raises an error explaining what to check (Base URL,
   network connectivity, or the Bearer Token). This step is optional — you may also save
   first and test later from the same button.
6. Click **Save**.

## Post-Condition

- A new Vendor Bill AI Backend record is created and active.
- The backend becomes selectable on the AI Import wizard and as a purchase journal's
  default backend.
