.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================================
SSI Vendor Bill Claude Code Import
===================================

Import vendor bills from PDF/PNG files using the
``odoo-vendor-bill-claude-code-extract`` AI extraction service.

This module adds an **AI Import** button to draft vendor bills
(``account.move``, ``move_type='in_invoice'``). The uploaded file is queued and
processed asynchronously via ``queue_job``: the extraction service returns the
partner, dates, reference and invoice lines, which are written back onto the
vendor bill, and the original file is attached. Because a single extraction can
take up to the service timeout, processing never blocks the web request.


Work Instruction
================

Vendor Bill AI Backend
-----------------------

* `Create Vendor Bill AI Backend <docs/vendor_bill_claude_code_backend/01-create.html>`_
* `Edit Vendor Bill AI Backend <docs/vendor_bill_claude_code_backend/02-edit.html>`_
* `Delete Vendor Bill AI Backend <docs/vendor_bill_claude_code_backend/03-delete.html>`_
* `Deactivate Vendor Bill AI Backend <docs/vendor_bill_claude_code_backend/04-deactivate.html>`_
* `Activate Vendor Bill AI Backend <docs/vendor_bill_claude_code_backend/05-activate.html>`_

Vendor Bill AI Import Job
--------------------------

* `Import Vendor Bill via AI <docs/vendor_bill_claude_code_job/01-import.html>`_
* `Retry Vendor Bill AI Import Job <docs/vendor_bill_claude_code_job/02-retry.html>`_


Installation
============

To install this module, you need to:

1.  Clone the branch 14.0 of the repository https://github.com/open-synergy/ssi-vendor-bill
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list (Must be on developer mode)
4.  Go to menu *Apps -> Apps -> Main Apps*
5.  Search For *SSI Vendor Bill Claude Code Import*
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
