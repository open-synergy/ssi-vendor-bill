# Restart Vendor Bill

> **Module:** ssi_vendor_bill\
> **Model:** `vendor_bill`\
> **Menu:** Financial Accounting > Account Payable > Vendor Bill\
> **Actor:** user in group `Vendor Bill / Validator`\
> **State:** `cancel`/`reject` → `draft`\
> **Requires:** `10-cancel`

## Pre-Condition

- Record is in **Cancelled** or **Rejected** status.
- User has _Can Restart_ access right (**Validator** access group).

## Flow

1. Open the **Financial Accounting > Account Payable > Vendor Bill** menu.
2. Open the record to restart.
3. Click the **Restart** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- Status returns to **Draft**.
