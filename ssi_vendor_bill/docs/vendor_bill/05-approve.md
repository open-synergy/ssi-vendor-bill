# Approve Vendor Bill

## Pre-Condition

- Record is in **Waiting for Approval** status.
- User is registered as an active approver on the record (in
  **Approvers**).
- User has *Can Approve* access right.

## Flow

1. Open the **Financial Accounting > Account Payable > Vendor Bill** menu.
2. Open the record to approve.
3. Click the **Approve** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- If all approval levels are fulfilled, the record automatically moves to
  **Unpaid** status (document number is generated at this point), or
  directly to **Paid** status when it has no detail lines.
- If there are still pending approval levels, status remains **Waiting for
  Approval**.
