# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Pre-migration for ssi_vendor_bill 14.0.2.0.0.

    Up to 14.0.1.x, ``vendor_bill`` was a dedicated model bolted onto the
    accounting module's own shared journal-entry table (its ``_table``
    pointed straight at that table, with ``_auto = False``): it had no
    table of its own and no real columns, only borrowed ir.model /
    ir.model.fields metadata. Starting with this version ``vendor_bill``
    becomes a genuine standalone transactional model with its own table.

    Before the new model is reflected, the leftover metadata of the old
    delegated model must be purged: its ir.model.fields rows (borrowed
    field definitions that were never really its own columns), the
    ir.model.relation / ir.model.constraint rows this module registered
    for that model as if it owned relation tables and constraints that in
    fact belong to the journal-entry model, and finally its own ir.model
    row. Left in place, that stale metadata would collide with -- or
    wrongly claim ownership of -- structures belonging to a table this
    migration must never touch, drop, or alter in any way.

    Two rules shape every statement below:

    * ``ir.model.relation.module`` and ``ir.model.constraint.module`` are
      Many2one columns to ir.module.module, i.e. plain integers -- they
      are matched through a subquery on ``ir_module_module.name``, the
      same idiom core Odoo uses in ``ir.model.relation._reflect_relation``.
      Both deletions are further narrowed to the old ``vendor_bill``
      model, so this module's legitimate claims over the relations and
      constraints of its *other* models stay untouched. Both run before
      the ir.model row goes away, since that narrowing depends on it.
    * Every ir.model.* row that disappears -- whether deleted here
      explicitly or silently through a database-level FK cascade when the
      ir.model row is removed -- first has the ir.model.data rows pointing
      at it removed. A dangling xmlid would be picked up at the end of the
      update by ``ir.model.data._process_end()``, whose ``unlink()`` on
      ir.model triggers ``_drop_table()`` and on ir.model.fields triggers
      ``_drop_column()``: unrequested DDL on a table that must be left
      exactly as it was.

    Nothing here does DDL: the whole script is DELETE statements against
    ir_* metadata tables only.

    Idempotent: every statement is a plain DELETE guarded by a WHERE
    clause, so re-running this script on a database where the cleanup
    already happened is a no-op.
    """
    _logger.info("14.0.2.0.0 (ssi_vendor_bill) pre-migrate: start")

    # 1. Drop ir.model.data entries pointing at the old model's borrowed
    #    field metadata (ir.model.fields rows for model = 'vendor_bill').
    openupgrade.logged_query(
        cr,
        """
        DELETE FROM ir_model_data
        WHERE model = 'ir.model.fields'
          AND res_id IN (
              SELECT id FROM ir_model_fields WHERE model = 'vendor_bill'
          )
        """,
    )

    # 2. Drop the old model's borrowed field metadata itself.
    openupgrade.logged_query(
        cr,
        "DELETE FROM ir_model_fields WHERE model = 'vendor_bill'",
    )

    # 3. Drop ir.model.data entries pointing at the relation metadata of
    #    the old model. Scoped by model only -- not by module -- so the
    #    rows that step 7 takes down through the ir.model FK cascade are
    #    covered too: a database-level cascade never cleans ir_model_data.
    openupgrade.logged_query(
        cr,
        """
        DELETE FROM ir_model_data
        WHERE model = 'ir.model.relation'
          AND res_id IN (
              SELECT id
              FROM ir_model_relation
              WHERE model IN (
                  SELECT id FROM ir_model WHERE model = 'vendor_bill'
              )
          )
        """,
    )

    # 4. Drop this module's claim on the relation tables of the old model.
    #    'module' is a Many2one to ir.module.module (an integer column),
    #    hence the subquery on the module name instead of a string
    #    literal. Narrowed to the old model so claims over the relations
    #    of this module's other models survive.
    openupgrade.logged_query(
        cr,
        """
        DELETE FROM ir_model_relation
        WHERE module IN (
                  SELECT id FROM ir_module_module WHERE name = 'ssi_vendor_bill'
              )
          AND model IN (
                  SELECT id FROM ir_model WHERE model = 'vendor_bill'
              )
        """,
    )

    # 5. Same treatment for constraint metadata: xmlids first, scoped by
    #    model only so the FK-cascaded rows of step 7 are covered as well.
    openupgrade.logged_query(
        cr,
        """
        DELETE FROM ir_model_data
        WHERE model = 'ir.model.constraint'
          AND res_id IN (
              SELECT id
              FROM ir_model_constraint
              WHERE model IN (
                  SELECT id FROM ir_model WHERE model = 'vendor_bill'
              )
          )
        """,
    )

    # 6. Drop this module's claim on the constraints of the old model --
    #    'module' is a Many2one here as well, and the same narrowing
    #    applies.
    openupgrade.logged_query(
        cr,
        """
        DELETE FROM ir_model_constraint
        WHERE module IN (
                  SELECT id FROM ir_module_module WHERE name = 'ssi_vendor_bill'
              )
          AND model IN (
                  SELECT id FROM ir_model WHERE model = 'vendor_bill'
              )
        """,
    )

    # 7. Drop ir.model.data entries pointing at the old ir.model row, then
    #    the row itself, so the new model reflects cleanly with its own
    #    table.
    openupgrade.logged_query(
        cr,
        """
        DELETE FROM ir_model_data
        WHERE model = 'ir.model'
          AND res_id IN (
              SELECT id FROM ir_model WHERE model = 'vendor_bill'
          )
        """,
    )
    openupgrade.logged_query(
        cr,
        "DELETE FROM ir_model WHERE model = 'vendor_bill'",
    )

    _logger.info("14.0.2.0.0 (ssi_vendor_bill) pre-migrate: done")
