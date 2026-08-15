# Reject Vendor Bill

> **Module:** ssi_vendor_bill\
> **Model:** `vendor_bill`\
> **Menu:** Financial Accounting > Account Payable > Vendor Bill\
> **Actor:** user in group `Vendor Bill / Validator`, registered as active approver\
> **State:** `confirm` → `reject`\
> **Requires:** `04-confirm`

## Pre-Condition

- Record is in **Waiting for Approval** status.
- User is registered as an active approver on the record (in **Approvers**).
- User has _Can Reject_ access right.

## Flow

1. Open the **Financial Accounting > Account Payable > Vendor Bill** menu.
2. Open the record to reject.
3. Click the **Reject** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- Status changes to **Rejected**.
