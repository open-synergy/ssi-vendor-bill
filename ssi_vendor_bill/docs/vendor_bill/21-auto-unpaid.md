# Auto Transition to Unpaid — Vendor Bill

> **Module:** ssi_vendor_bill\
> **Model:** `vendor_bill`\
> **Menu:** Financial Accounting > Account Payable > Vendor Bill\
> **Actor:** system (`base.automation`), when the payable move line becomes unreconciled\
> **State:** `done` → `open`\
> **Requires:** `20-auto-paid`

## Pre-Condition

- Record is in **Paid** status.
- The document has a payable journal item (**Payable Move Line**) linked to its
  accounting entry.

## Flow

This transition is not triggered by a user action. It runs automatically
(`base.automation`) whenever the payable journal item of the document becomes no longer
fully reconciled — for example, after the reconciled vendor payment is
undone/unreconciled, so that the **Realized** field changes from checked to unchecked.

## Post-Condition

- Status changes to **Unpaid**.
