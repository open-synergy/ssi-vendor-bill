# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class VendorBill(models.Model):
    """Dedicated model for Vendor Bill on the shared account_move table.

    ``account.move`` is used for every journal entry, customer invoice,
    vendor bill, refund, etc., distinguished only by ``move_type``. Because
    access rights and record rules are per-model, it is not possible to
    grant a user access to vendor bills only without also exposing every
    other move type.

    This model exposes **only** vendor bills. It inherits every field and
    method of ``account.move`` and reuses the very same physical table
    (``_table = "account_move"``), so no new table nor column is created.
    A dedicated model lets ACL and record rules target vendor bills
    independently from other move types.

    Do NOT add stored fields here: a stored field would add a column to
    the real ``account_move`` table. Only override existing field
    attributes, add methods, or add non-stored/related fields. Extra data
    belongs on ``account.move`` in ``ssi_financial_accounting``.
    """

    _name = "vendor_bill"
    _inherit = "account.move"
    _table = "account_move"
    _description = "Vendor Bill"
    # account.move carries Many2many fields with an explicit relation table
    # (e.g. `transaction_ids` from the `payment` module). Odoo's field setup
    # rejects two _auto=True models sharing the same m2m relation table.
    # vendor_bill does not own the table's schema -- account.move does --
    # so mark it _auto=False to skip that ownership check (no table/column
    # management runs for this model, which is correct: the table is
    # created and migrated by account.move alone).
    _auto = False
    # _auto=False defaults _log_access to False too, which would silently
    # stop create()/write() from stamping create_uid/write_uid/*_date on the
    # shared columns. Force it back on so the audit trail keeps working.
    _log_access = True

    move_type = fields.Selection(
        default="in_invoice",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["move_type"] = "in_invoice"
        # Elevate so a user holding only `vendor_bill` ACL can create it,
        # without needing direct access to account.move/account.move.line.
        # sudo() in Odoo 14 keeps env.uid = triggering user -> create_uid
        # stays correct.
        records = super(VendorBill, self.sudo()).create(vals_list)
        return records.with_env(self.env)

    def write(self, vals):
        return super(VendorBill, self.sudo()).write(vals)

    def action_post(self):
        return super(VendorBill, self.sudo()).action_post()

    def button_draft(self):
        return super(VendorBill, self.sudo()).button_draft()

    def button_cancel(self):
        return super(VendorBill, self.sudo()).button_cancel()
