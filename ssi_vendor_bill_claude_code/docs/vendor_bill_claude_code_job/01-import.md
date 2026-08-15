# Import Vendor Bill via AI

> **Module:** ssi_vendor_bill_claude_code
> **Model:** `vendor.bill.claude.code.job`
> **Menu:** Financial Accounting > Account Payable > Bills
> **Actor:** user in group *Billing* (`account.group_account_invoice`)
> **State:** `—` → `queued`

## Pre-Condition

- **Data:** A draft vendor bill (`account.move`, Type = Vendor Bill) exists, or is
  created as part of this flow.
- **Data:** At least one active Vendor Bill AI Backend exists to select in the wizard.
- **Access:** User is in group *Billing*.

## Flow

1. Open the **Financial Accounting > Account Payable > Bills** menu.
2. Open an existing draft vendor bill, or create a new one and save it in **Draft**
   status.
3. Click **AI Import** in the header. This button is only visible while the bill's
   Type is **Vendor Bill** and its status is **Draft**.
4. In the wizard that appears, select the **Backend** to use. It is automatically
   preselected from the bill's journal default backend, if one is configured; change
   it if needed.
5. Upload the vendor bill file in **Vendor Bill File** (PDF or image — PNG, JPEG,
   WEBP, or HEIC).
6. Click **Import**.

## Post-Condition

- A new Vendor Bill AI Import Job is created, linked to this vendor bill and the
  selected backend, and immediately moves to **Queued** status for background
  processing via `queue_job` — no separate action is needed to start it.
- The uploaded file is attached to the vendor bill and, if the vendor bill did not
  already have a document preview, shown there.
- A notification confirms the file was queued for AI extraction.
- The vendor bill itself remains in **Draft** status; its fields (partner, dates,
  reference, lines) are written by the job once processing completes.
- The job's progress can be tracked from the **AI Import Jobs** smart button on the
  vendor bill, or from the **Vendor Bill AI Import Jobs** menu.

## Related Views

- **AI Import Jobs** (`action_open_claude_code_jobs`) — a stat button in the vendor
  bill's button box, visible once at least one job exists. It only navigates to the
  list of jobs for that bill (filtered on `move_id`); it does not write any field, so
  it has no IK of its own.
- **Open Vendor Bill** (`action_open_move`) — a header button on the job form. It only
  navigates back to the vendor bill the job belongs to; it does not write any field,
  so it has no IK of its own. See `02-retry.md`.
