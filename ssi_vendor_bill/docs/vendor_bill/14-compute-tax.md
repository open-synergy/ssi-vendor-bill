# Compute Tax — Vendor Bill

> **Module:** ssi_vendor_bill\
> **Model:** `vendor_bill`\
> **Menu:** Financial Accounting > Account Payable > Vendor Bill\
> **Actor:** user in group `Vendor Bill / User`\
> **Requires:** `01-create`

## Pre-Condition

- Record is in **Draft** status.
- The **Detail** tab has one or more lines filled in.

## Flow

1. Open the **Financial Accounting > Account Payable > Vendor Bill** menu.
2. Open the record.
3. On the **Detail** tab, click the **Compute Tax** button below the detail lines.

## Post-Condition

- The **Taxes** table on the **Detail** tab is recomputed from the detail lines:
  existing tax lines are replaced by the tax(es) configured on each detail line.
- **Untaxed Amount**, **Tax**, and **Total** are updated accordingly.
