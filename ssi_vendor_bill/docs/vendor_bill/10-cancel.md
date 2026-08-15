# Cancel Vendor Bill

> **Module:** ssi_vendor_bill\
> **Model:** `vendor_bill`\
> **Menu:** Financial Accounting > Account Payable > Vendor Bill\
> **Actor:** user in group `Vendor Bill / Validator`\
> **State:** `draft`/`confirm`/`open` → `cancel`\
> **Requires:** `01-create`

## Pre-Condition

- Record is in **Draft**, **Waiting for Approval**, or **Unpaid** status.
- User has _Can Cancel_ access right (**Validator** access group).

## Flow

1. Open the **Financial Accounting > Account Payable > Vendor Bill** menu.
2. Open the record to cancel.
3. Click the **Cancel** button.
4. In the wizard that appears, select the **Cancellation Reason**.
5. Click **Confirm**.

## Post-Condition

- Status changes to **Cancelled**.
- The accounting entry generated for this document (if any) is deleted.
