# Activate Vendor Bill AI Backend

> **Module:** `ssi_vendor_bill_claude_code`\
> **Model:** `vendor.bill.claude.code.backend`\
> **Menu:** Financial Accounting > Configuration > Account > Vendor Bill AI Backends\
> **Actor:** user in group `Vendor Bill Claude Code Import`\
> **Active:** `false` → `true`\
> **Requires:** `04-deactivate`

## Pre-Condition

- **Record:** The record is currently archived.
- **Access:** User is in group `Vendor Bill Claude Code Import`.

## Flow

1. Open the **Financial Accounting > Configuration > Account > Vendor Bill AI Backends**
   menu.
2. Enable the **Archived** filter in the search bar.
3. Select one or more records to reactivate (check the checkbox).
4. Click **Action** > **Unarchive**.

## Post-Condition

- The records are restored and appear again in the default list view.
- The backends can be selected again on the AI Import wizard and as a purchase journal's
  default backend.
