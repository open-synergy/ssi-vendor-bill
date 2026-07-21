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

    def _as_account_move(self):
        """Re-browse this recordset as a genuine ``account.move``.

        Several methods inherited from ``account.move`` (e.g.
        ``_compute_name``, which assigns the sequence-based document
        number) build an internal accumulator hardcoded to
        ``self.env['account.move']`` and then concatenate it with the
        recordset being processed. That concatenation raises a
        ``TypeError`` when the recordset is a ``vendor_bill`` instead,
        since the two are distinct models even though they share the
        physical table. Running mutating operations through a real
        ``account.move`` recordset (same physical rows, same ids) avoids
        that class mismatch entirely.
        """
        return self.env["account.move"].browse(self.ids)

    @api.model_create_multi
    def create(self, vals_list):  # pylint: disable=method-required-super
        for vals in vals_list:
            vals["move_type"] = "in_invoice"
        # Elevate so a user holding only `vendor_bill` ACL can create it,
        # without needing direct access to account.move/account.move.line.
        # sudo() in Odoo 14 keeps env.uid = triggering user -> create_uid
        # stays correct. Create through account.move itself (see
        # _as_account_move) rather than super(), since create() is where
        # the sequence-name computation above is triggered.
        account_moves = self.env["account.move"].sudo().create(vals_list)
        return self.browse(account_moves.ids).with_env(self.env)

    def write(self, vals):  # pylint: disable=method-required-super
        return self._as_account_move().sudo().write(vals)

    def onchange(  # pylint: disable=method-required-super
        self, values, field_name, field_onchange
    ):
        """Run the whole onchange machinery on ``account.move`` instead.

        ``invoice_line_ids`` and ``line_ids`` are One2many fields whose
        inverse ``account.move.line.move_id`` is a Many2one pointing at
        ``account.move`` -- not at ``vendor_bill``. The ORM onchange
        machinery builds a virtual record with ``self.new(...)``, and on a
        ``vendor_bill`` virtual record the One2many/Many2one pair straddles
        two different models. The inverse bookkeeping then updates the wrong
        model's cache, so a line added by the client
        (``invoice_line_ids: [(0, "virtual_1", {...})]``) is missing from the
        final snapshot and the server answers with a bare ``[(5,)]``. The web
        client crashes on that empty list in ``FieldOne2Many.reset``.

        Running the onchange through a genuine ``account.move`` recordset
        (same physical rows, same ids -- see ``_as_account_move``) keeps the
        One2many and its inverse on one and the same model, so newly added
        lines survive and come back as ``(0, ...)`` commands. The returned
        payload only holds field names and values, which are identical on
        both models, so it can be handed back to the client untouched.

        ``sudo()`` mirrors ``create``/``write``: a user holding only the
        ``vendor_bill`` ACL has no read access to ``account.move`` nor to
        ``account.move.line``, and without it the onchange would raise an
        ``AccessError`` for exactly the users this model exists for.

        ``default_move_type`` has to be forced for the same reason
        ``create`` forces ``move_type``: on its first call (falsy
        ``field_name``) the onchange machinery fills the missing fields
        from ``default_get``, and delegating hands that over to
        ``account.move``, whose own default is ``entry``. That would
        silently override the ``in_invoice`` default this model declares,
        and every later onchange would then recompute the document as a
        plain journal entry -- no tax line, no payable counterpart, hence
        an unbalanced entry on save. Forcing the key keeps the delegated
        defaults in step with ``create``, whatever context the caller had.
        """
        account_move = self._as_account_move()
        account_move = account_move.sudo().with_context(default_move_type="in_invoice")
        return account_move.onchange(values, field_name, field_onchange)

    def action_post(self):
        return self._as_account_move().sudo().action_post()

    def button_draft(self):
        return self._as_account_move().sudo().button_draft()

    def button_cancel(self):
        return self._as_account_move().sudo().button_cancel()
