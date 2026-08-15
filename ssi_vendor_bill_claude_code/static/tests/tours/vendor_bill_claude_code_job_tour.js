/* Copyright 2026 OpenSynergy Indonesia
 * Copyright 2026 PT. Simetri Sinergi Indonesia
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
odoo.define("ssi_vendor_bill_claude_code.vendor_bill_claude_code_job_tour", function (
    require
) {
    "use strict";

    var tour = require("web_tour.tour");

    // IK: docs/vendor_bill_claude_code_job/01-import.md
    //
    // Boundary (skill odoo-development-ui-test, patterns.md §Q): the AI
    // Import wizard is a file-upload wizard (<input type="file"> on
    // data_file). Attaching a real file to a hidden file input is not
    // reliable across browsers, so this tour stops at "the wizard opens"
    // and discards it, instead of uploading a file and clicking Import.
    // The full import flow (attachment created, job enqueued) is covered
    // by odoo_yaml_test scenarios in
    // tests/test_vendor_bill_claude_code_import_wizard.yaml and the
    // mocked-HTTP Python tests in
    // tests/test_vendor_bill_claude_code_import.py.
    tour.register(
        "ssi_vendor_bill_claude_code_vendor_bill_claude_code_job_import",
        {
            test: true,
            url: "/web",
        },
        [
            // Flow 1 — Open the Financial Accounting > Account Payable >
            // Bills menu
            tour.stepUtils.showAppsMenuItem(),
            {
                content: "Open the Financial Accounting app",
                trigger:
                    '.o_app[data-menu-xmlid="ssi_financial_accounting.menu_root_financial_accounting"]',
            },
            {
                content: "Open the Account Payable menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_financial_accounting.menu_account_payable"]',
            },
            {
                content: "Open the Bills menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_financial_accounting.vendor_bill_menu"]',
            },
            {
                content: "Bills list is displayed",
                trigger: ".o_control_panel .breadcrumb-item.active:contains(Bills)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only.
                },
            },

            // Flow 2 — Open the draft vendor bill prepared in setUpClass
            {
                content: "Open the draft vendor bill",
                trigger:
                    ".o_data_row:contains(Tour AI Import Vendor) .o_data_cell:first",
                extra_trigger: ".o_list_view",
            },
            {
                content: "The vendor bill is open",
                trigger: ".o_form_view",
                run: function () {
                    // Assertion only.
                },
            },

            // Flow 3 — Click AI Import in the header
            {
                content: "Click the AI Import button",
                trigger:
                    ".o_statusbar_buttons button[name='action_open_vendor_bill_claude_code_wizard']:enabled",
            },
            {
                content: "The AI Import wizard is open",
                // 14.0: do NOT prefix with `.modal` — the trigger is already
                // searched inside the modal (patterns.md §H).
                trigger: ".o_form_view",
                run: function () {
                    // Assertion only.
                },
            },

            // Flow 4/5/6 stop here — see the boundary note above. Discard
            // the wizard instead of uploading a file and clicking Import.
            {
                content: "Discard the wizard",
                trigger: ".modal-footer button.btn-secondary",
            },
            {
                content: "Wizard is closed",
                trigger: "body:not(:has(.modal))",
                run: function () {
                    // Assertion only.
                },
            },
        ]
    );

    // IK: docs/vendor_bill_claude_code_job/02-retry.md
    tour.register(
        "ssi_vendor_bill_claude_code_vendor_bill_claude_code_job_retry",
        {
            test: true,
            url: "/web",
        },
        [
            // Flow 1 — Open the Vendor Bill AI Import Jobs menu
            tour.stepUtils.showAppsMenuItem(),
            {
                content: "Open the Financial Accounting app",
                trigger:
                    '.o_app[data-menu-xmlid="ssi_financial_accounting.menu_root_financial_accounting"]',
            },
            {
                content: "Open the Configuration menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_financial_accounting.menu_financial_accounting_configuration"]',
            },
            {
                // "Account" is a grouping header with no action — no step
                // for it. Its children are flattened into this dropdown.
                content: "Open the Vendor Bill AI Import Jobs menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_vendor_bill_claude_code.menu_vendor_bill_claude_code_job"]',
            },
            {
                content: "Vendor Bill AI Import Jobs list is displayed",
                trigger:
                    ".o_control_panel .breadcrumb-item.active:contains(Vendor Bill AI Import Jobs)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only.
                },
            },

            // Flow 2 — Open the failed job prepared in setUpClass
            {
                content: "Open the failed job",
                trigger: ".o_data_row:contains(TOUR-RETRY-FILE.pdf) .o_data_cell:first",
                extra_trigger: ".o_list_view",
            },
            {
                content: "The job is open, status is Failed",
                trigger:
                    ".o_statusbar_status .o_arrow_button[data-value='failed'].btn-primary",
                run: function () {
                    // Assertion only.
                },
            },

            // Flow 3 — Click Retry (no confirmation dialog on this button)
            {
                content: "Click the Retry button",
                trigger: ".o_statusbar_buttons button[name='action_retry']:enabled",
            },

            // Post-Condition — Status changes to Queued
            {
                content: "Status is Queued",
                trigger:
                    ".o_statusbar_status .o_arrow_button[data-value='queued'].btn-primary",
                run: function () {
                    // Assertion only.
                },
            },
        ]
    );
});
