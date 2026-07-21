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
    ir.model.relation / ir.model.constraint rows it registered as if it
    owned relation tables and constraints that in fact belong to the
    journal-entry model, and finally its own ir.model row. Left in place,
    that stale metadata would collide with -- or wrongly claim ownership
    of -- structures belonging to a table this migration must never
    touch, drop, or alter in any way.

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

    # 3. Drop this module's claim on relation tables and constraints that
    #    actually belong to the table it used to piggyback on --
    #    otherwise reflection would treat those structures as orphaned
    #    and drop them along with the stale metadata.
    openupgrade.logged_query(
        cr,
        "DELETE FROM ir_model_relation WHERE module = 'ssi_vendor_bill'",
    )
    openupgrade.logged_query(
        cr,
        "DELETE FROM ir_model_constraint WHERE module = 'ssi_vendor_bill'",
    )

    # 4. Drop ir.model.data entries pointing at the old ir.model row, then
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
