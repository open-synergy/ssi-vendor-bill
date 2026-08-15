# Retry Vendor Bill AI Import Job

> **Module:** ssi_vendor_bill_claude_code\
> **Model:** `vendor.bill.claude.code.job`\
> **Menu:** Financial Accounting > Configuration > Account > Vendor Bill AI Import Jobs\
> **Actor:** any internal user\
> **State:** `failed` / `need_review` → `queued`\
> **Requires:** `01-import`

## Pre-Condition

- **Record:** The job's Status is **Failed** or **Need Review**.
- **Access:** User can view the job (all internal users can; the retry action itself
  runs with the job model's own elevated rights, so no additional group is required).

## Flow

1. Open the **Financial Accounting > Configuration > Account > Vendor Bill AI Import
   Jobs** menu, or click the **AI Import Jobs** smart button on the vendor bill.
2. Open a job whose Status is **Failed** or **Need Review**.
3. Click **Retry** in the header. This button is only visible while the job's Status is
   **Failed** or **Need Review**.

## Post-Condition

- The job's Status changes to **Queued** and its Error Message is cleared.
- The job is re-processed in the background exactly like a fresh import (see
  `01-import`), calling the backend again and writing the result onto the same vendor
  bill.
