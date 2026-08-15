# Auto Transition to Paid — Vendor Bill

> **Module:** ssi_vendor_bill\
> **Model:** `vendor_bill`\
> **Menu:** Financial Accounting > Account Payable > Vendor Bill\
> **Actor:** system (`base.automation`), when the payable move line becomes reconciled\
> **State:** `open` → `done`\
> **Requires:** `05-approve`

## Pre-Condition

- Record is in **Unpaid** status.
- The document has a payable journal item (**Payable Move Line**) linked to its
  accounting entry.

## Flow

This transition is not triggered by a user action. It runs automatically
(`base.automation`) whenever the payable journal item of the document is fully
reconciled — for example, after a vendor payment is matched/ reconciled against this
bill's payable move line, so that the **Realized** field changes from unchecked to
checked.

## Post-Condition

- Status changes to **Paid**.
