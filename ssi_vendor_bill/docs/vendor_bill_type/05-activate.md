# Activate Vendor Bill Type

> **Module:** ssi_vendor_bill\
> **Model:** `vendor_bill_type`\
> **Menu:** Financial Accounting > Configuration > Vendor Bill Types\
> **Actor:** user in group `Vendor Bill Type`\
> **Active:** `false` → `true`\
> **Requires:** `04-deactivate`

## Pre-Condition

- None.

## Flow

1. Open the **Financial Accounting > Configuration > Vendor Bill Types** menu.
2. Enable the **Archived** filter in the search bar.
3. Select one or more records to reactivate (check the checkbox).
4. Click **Action** > **Unarchive**.

## Post-Condition

- The records are restored and appear again in the default list view.
- The types can be selected as **Type** on new vendor bills.
