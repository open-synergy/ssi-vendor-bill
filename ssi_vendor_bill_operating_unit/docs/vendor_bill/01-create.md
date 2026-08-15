# Create Vendor Bill

> **Module:** ssi_vendor_bill_operating_unit\
> **Model:** `vendor_bill`\
> **Menu:** Financial Accounting > Account Payable > Vendor Bill\
> **Actor:** user in group `Vendor Bill / User`\
> **State:** `—` → `draft`\
> **Requires:** `ssi_vendor_bill/vendor_bill/01-create`

This IK only documents what this module **adds** to the base create Flow. For the full
list of required/optional fields, detail lines, and the Save step, see the base IK
`ssi_vendor_bill` `docs/vendor_bill/01-create.md`.

## Pre-Condition

- **Module:** The `operating_unit` module is installed.
- **Data:** At least one active `operating.unit` record exists.
- **Access:** User is assigned to the operating unit(s) they need to select
  (`assigned_operating_unit_ids`). Only a user in group
  `operating_unit.group_multi_operating_unit` sees and can edit the **Operating Unit**
  field described below; a user outside that group creates the bill exactly as
  documented in the base IK, with the field hidden.

## Flow

1. Open the **Financial Accounting > Account Payable > Vendor Bill** menu and click
   **New**, as described in the base Flow.
2. If the current user is in group `operating_unit.group_multi_operating_unit`, an
   **Operating Unit** field is available on the form: select the operating unit issuing
   this bill. Defaults to the user's default operating unit
   (`default_operating_unit_id`); change if needed. Editable only while the document is
   in **Draft** status — it becomes read-only once the document leaves Draft.
3. Continue filling in the remaining fields and detail lines, then click **Save**, as
   described in the base Flow.

## Post-Condition

- The vendor bill is saved with the **Operating Unit** field set to the selected value
  (or left empty, for a user outside the multi-operating-unit group).
- When the bill later leaves Draft and reaches **Open** status (see base IK
  `ssi_vendor_bill` `docs/vendor_bill/05-approve.md`), the `account.move` created for it
  — and every one of its journal items (payable line, detail lines, and tax lines alike)
  — carries the same **Operating Unit** as the bill.

## Modified — Record Visibility

- The Vendor Bill list is now filtered by operating unit (record rule). A user only sees
  bills whose Operating Unit is unset or matches one of the operating units assigned to
  them. This is not a Flow step.
