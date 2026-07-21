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

    account_move_id = fields.Many2one(
        comodel_name="account.move",
        compute="_compute_account_move_id",
        string="Account Move",
        help="Same physical row, addressed through the generic "
        "account.move model. Used to make the mail thread (messages, "
        "followers, activities) point at account.move so it has a single "
        "owner model instead of being split between vendor_bill and "
        "account.move.",
    )
    # mail.thread/mail.activity.mixin fields are plain One2many relying on
    # an implicit ORM filter that matches the *model name of this
    # recordset* (`vendor_bill`) against `mail.message.model` /
    # `mail.followers.res_model` / `mail.activity.res_model`. Since
    # create()/write()/action_post() delegate to a genuine account.move
    # recordset (see _as_account_move), messages/followers/activities
    # produced by those calls are owned by account.move and would never
    # show up through that implicit filter.
    #
    # These are redeclared as plain computed fields (NOT `related=`) that
    # fetch account.move's value directly. A `related="account_move_id...`
    # field would look correct, but Odoo also registers it in the global
    # field-dependency graph: creating a mail.message/mail.followers
    # ANYWHERE in the database then makes the ORM try to search
    # vendor_bill by account_move_id to find affected records to
    # recompute -- and account_move_id, a non-stored field, cannot be
    # searched, logging "Non-stored field ... cannot be searched" (an
    # ERROR-level log line that fails the `oca_checklog_odoo` CI job) on
    # every such create in the whole system, not just on vendor_bill.
    # `@api.depends()` (no dependencies) keeps these out of that graph
    # entirely; the value is simply recomputed each time it is read.
    message_follower_ids = fields.One2many(
        compute="_compute_message_follower_ids",
    )
    message_ids = fields.One2many(
        compute="_compute_message_ids",
    )
    activity_ids = fields.One2many(
        compute="_compute_activity_ids",
    )

    @api.depends()
    def _compute_account_move_id(self):
        for record in self:
            record.account_move_id = record._as_account_move()

    @api.depends()
    def _compute_message_follower_ids(self):
        for record in self:
            record.message_follower_ids = record._as_account_move().message_follower_ids

    @api.depends()
    def _compute_message_ids(self):
        for record in self:
            record.message_ids = record._as_account_move().message_ids

    @api.depends()
    def _compute_activity_ids(self):
        for record in self:
            record.activity_ids = record._as_account_move().activity_ids

    def _compute_message_attachment_count(self):
        """Override account.move's own count with the delegated value.

        ``message_attachment_count`` already carries
        ``compute="_compute_message_attachment_count"`` from mail.thread, so
        redefining the method (without redeclaring the field) is enough --
        unlike message_ids/message_follower_ids/activity_ids above, the
        original implementation has no ``@api.depends`` and was never part
        of the field-trigger graph, so there is nothing to avoid here.
        """
        for record in self:
            record.message_attachment_count = (
                record._as_account_move().message_attachment_count
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

    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, **kwargs):  # pylint: disable=method-required-super
        """Post the message on the account.move side of this record.

        Mirrors create()/write(): mail.thread's message_post() stamps the
        new mail.message with ``model = self._name``, so calling it
        directly on a vendor_bill recordset would (re)create the very
        split this module exists to remove. Posting through
        _as_account_move() keeps every message under account.move,
        consistent with message_ids/message_follower_ids/activity_ids
        above.

        The ``@api.returns`` decorator is required here, not just cosmetic:
        mail.thread.message_post() carries the same decorator so that
        RPC callers (the web client's chatter widget) receive a plain
        ``mail.message`` id instead of a recordset. Overriding the method
        without repeating the decorator drops that conversion -- the raw
        ``mail.message`` recordset then leaks into the JSON-RPC response,
        which the client cannot serialize and the longpolling bus
        notification cannot use as a record id, breaking "Log note"/"Send
        message" from the vendor_bill form with an
        ``UndefinedFunction: operator does not exist: integer = text``
        error at the database layer.
        """
        return self._as_account_move().sudo().message_post(**kwargs)

    def message_subscribe(
        self, partner_ids=None, channel_ids=None, subtype_ids=None
    ):  # pylint: disable=method-required-super
        return (
            self._as_account_move()
            .sudo()
            .message_subscribe(
                partner_ids=partner_ids,
                channel_ids=channel_ids,
                subtype_ids=subtype_ids,
            )
        )

    def message_unsubscribe(
        self, partner_ids=None, channel_ids=None
    ):  # pylint: disable=method-required-super
        return (
            self._as_account_move()
            .sudo()
            .message_unsubscribe(partner_ids=partner_ids, channel_ids=channel_ids)
        )

    def activity_schedule(
        self, *args, **kwargs
    ):  # pylint: disable=method-required-super
        return self._as_account_move().sudo().activity_schedule(*args, **kwargs)
