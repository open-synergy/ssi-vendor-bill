# Edit Vendor Bill AI Backend

> **Module:** `ssi_vendor_bill_claude_code`\
> **Model:** `vendor.bill.claude.code.backend`\
> **Menu:** Financial Accounting > Configuration > Account > Vendor Bill AI Backends\
> **Actor:** user in group `Vendor Bill Claude Code Import`\
> **Requires:** `01-create`\
> **Inline Actions:** `action_test_connection` (Test Connection)

## Pre-Condition

- **Access:** User is in group `Vendor Bill Claude Code Import`.

## Flow

1. Open the **Financial Accounting > Configuration > Account > Vendor Bill AI Backends**
   menu.
2. Find and open the record to edit.
3. Change the required fields (Code, Name).
4. On the **Claude Code Settings** tab, change the Base URL, Bearer Token, Extraction
   Model, Timeout, or Verify SSL as needed.
5. Click **Test Connection** in the header to verify the changed Base URL and/or Bearer
   Token are still correct — for example after rotating the Bearer Token or moving the
   service to a new Base URL. Skipping this step does not block saving; it only means
   the next real import is the first thing to surface a misconfiguration.
6. Click **Save**.

## Post-Condition

- The record is updated with the new values.
