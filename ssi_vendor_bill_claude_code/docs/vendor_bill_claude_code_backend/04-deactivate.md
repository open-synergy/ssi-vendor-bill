# Deactivate Vendor Bill AI Backend

> **Module:** ssi_vendor_bill_claude_code
> **Model:** `vendor.bill.claude.code.backend`
> **Menu:** Financial Accounting > Configuration > Account > Vendor Bill AI Backends
> **Actor:** user in group *Vendor Bill Claude Code Import*
> **Active:** `true` → `false`
> **Requires:** `01-create`

## Pre-Condition

- **Record:** The record is currently active.
- **Access:** User is in group *Vendor Bill Claude Code Import*.

## Flow

1. Open the **Financial Accounting > Configuration > Account > Vendor Bill AI Backends**
   menu.
2. Select one or more records to deactivate (check the checkbox).
3. Click **Action** > **Archive**.
4. Click **OK** to confirm.

## Post-Condition

- The records are archived and no longer appear in the default list view.
- Deactivated backends cannot be selected on the AI Import wizard or as a purchase
  journal's default backend.
- Jobs that already used this backend can still be viewed.
