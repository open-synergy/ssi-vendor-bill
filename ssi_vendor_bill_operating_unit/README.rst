.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
Vendor Bill + Operating Unit
============================

This is a glue module that adds Operating Unit support to the
``vendor_bill`` model. Users can pick an operating unit on the vendor bill
tree and form views, editable while the document is in draft. The
operating unit set on the bill is propagated to the ``account.move``
generated when the bill is opened and to every ``account.move.line``
posted with it, keeping the resulting journal entries scoped to the same
operating unit. Visibility of vendor bills is restricted per operating
unit through a record rule.

Work Instruction
================

* `Create Vendor Bill <docs/vendor_bill/01-create.html>`_


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
