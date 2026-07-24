.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========
Vendor Bill
===========

This module provides ``vendor_bill``, a standalone SSI transactional
document with its own table -- it does not reuse or extend the
``account.move`` table. The document follows the standard SSI workflow
(``draft`` -> ``confirm`` -> ``open``/``reject`` -> ``done``, plus
``cancel``) with multiple approval. When the document is confirmed and
approved into the ``open`` state, it generates its own ``account.move``
record (linked through the ``move_id`` field). The document then
transitions automatically to ``done`` once the payable journal item on
that ``account.move`` is fully reconciled, and back to ``open`` if the
reconciliation is undone.


Work Instruction
=================

Vendor Bill
-----------

* `Create Vendor Bill <docs/vendor_bill/01-create.html>`_
* `Edit Vendor Bill <docs/vendor_bill/02-edit.html>`_
* `Delete Vendor Bill <docs/vendor_bill/03-delete.html>`_
* `Confirm Vendor Bill <docs/vendor_bill/04-confirm.html>`_
* `Approve Vendor Bill <docs/vendor_bill/05-approve.html>`_
* `Reject Vendor Bill <docs/vendor_bill/06-reject.html>`_
* `Cancel Vendor Bill <docs/vendor_bill/10-cancel.html>`_
* `Restart Vendor Bill <docs/vendor_bill/12-restart.html>`_
* `Compute Tax - Vendor Bill <docs/vendor_bill/14-compute-tax.html>`_
* `Auto Transition to Paid - Vendor Bill <docs/vendor_bill/20-auto-paid.html>`_
* `Auto Transition to Unpaid - Vendor Bill <docs/vendor_bill/21-auto-unpaid.html>`_

Vendor Bill Type
----------------

* `Create Vendor Bill Type <docs/vendor_bill_type/01-create.html>`_
* `Edit Vendor Bill Type <docs/vendor_bill_type/02-edit.html>`_
* `Delete Vendor Bill Type <docs/vendor_bill_type/03-delete.html>`_
* `Deactivate Vendor Bill Type <docs/vendor_bill_type/04-deactivate.html>`_
* `Activate Vendor Bill Type <docs/vendor_bill_type/05-activate.html>`_


Installation
============

To install this module, you need to:

1.  Clone the branch 14.0 of the repository https://github.com/open-synergy/ssi-vendor-bill
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list (Must be on developer mode)
4.  Go to menu *Apps -> Apps -> Main Apps*
5.  Search For *Vendor Bill*
6.  Install the module


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/open-synergy/ssi-vendor-bill/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Andhitia Rama <andhitia.r@gmail.com>

Maintainer
----------

.. image:: https://simetri-sinergi.id/logo.png
   :alt: PT. Simetri Sinergi Indonesia
   :target: https://simetri-sinergi.id

This module is maintained by the PT. Simetri Sinergi Indonesia.
