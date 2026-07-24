# Create Vendor Bill

> **Module:** ssi_vendor_bill_operating_unit **Extends:** ssi_vendor_bill — model
> `vendor_bill`, aksi `01-create`

## Additional Fields

When this module is installed, the create form gains one field:

- **Operating Unit**: The operating unit issuing the bill. Only visible to users
  belonging to the multi-operating-unit group
  (`operating_unit.group_multi_operating_unit`). Defaults to the user's default
  operating unit. Editable while the document is in **Draft** status; becomes read-only
  once the document leaves Draft. Propagated to the `account.move` (and its journal
  items) created when the bill is opened.

## Modified — Record Visibility

- The Vendor Bill list is now filtered by operating unit (record rule). A user only sees
  bills whose Operating Unit is unset or matches one of the operating units assigned to
  them. This is not a Flow step.
