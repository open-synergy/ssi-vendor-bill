/* Copyright 2026 OpenSynergy Indonesia
 * Copyright 2026 PT. Simetri Sinergi Indonesia
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
odoo.define(
    "ssi_vendor_bill_claude_code.vendor_bill_claude_code_backend_tour",
    function (require) {
        "use strict";

        var tour = require("web_tour.tour");

        // IK: docs/vendor_bill_claude_code_backend/01-create.md
        tour.register(
            "ssi_vendor_bill_claude_code_vendor_bill_claude_code_backend_create",
            {
                test: true,
                url: "/web",
            },
            [
                // Flow 1 — Open the Financial Accounting > Configuration > Account >
                // Vendor Bill AI Backends menu
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
                    // "Account" (menu_account_configuration) is a grouping header
                    // with no action of its own — no step for it. Its children
                    // are flattened into this same Configuration dropdown.
                    content: "Open the Vendor Bill AI Backends menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_vendor_bill_claude_code.menu_vendor_bill_claude_code_backend"]',
                },
                {
                    content: "Vendor Bill AI Backends list is displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Vendor Bill AI Backends)",
                    extra_trigger: ".o_list_view",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 2 — Click the New button
                {
                    content: "Click Create",
                    trigger: ".o_list_button_add",
                    extra_trigger: ".o_list_view",
                },
                {
                    content: "Form is open in edit mode",
                    trigger: ".o_form_view.o_form_editable",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 3 — Fill in Code and Name
                {
                    content: "Fill in Code",
                    trigger: ".o_field_widget[name='code']",
                    extra_trigger: ".o_form_view.o_form_editable",
                    run: "text TOUR-BACKEND-01",
                },
                {
                    content: "Fill in Name",
                    trigger: ".o_field_widget[name='name']",
                    extra_trigger: ".o_form_view.o_form_editable",
                    run: "text Tour Test Backend Create",
                },

                // Flow 4 — Fill in the Claude Code Settings tab
                {
                    content: "Open the Claude Code Settings tab",
                    trigger: ".o_notebook .nav-link:contains(Claude Code Settings)",
                },
                {
                    content: "Fill in Base URL",
                    trigger: ".o_field_widget[name='base_url']",
                    extra_trigger: ".o_form_view.o_form_editable",
                    run: "text https://vendor-bill.example.com",
                },
                {
                    content: "Fill in Bearer Token",
                    trigger: ".o_field_widget[name='bearer_token']",
                    extra_trigger: ".o_form_view.o_form_editable",
                    run: "text tour-test-token",
                },

                // Flow 5 — Test Connection is available (inline action). Not
                // clicked: it calls a real external service, and this Base URL
                // does not resolve to one — see the Python docstring.
                {
                    content: "Test Connection button is available",
                    trigger:
                        ".o_statusbar_buttons button[name='action_test_connection']:enabled",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 6 — Click Save
                {
                    content: "Save the record",
                    trigger: ".o_form_button_save",
                },
                {
                    content: "Record is saved",
                    trigger: ".o_form_view.o_form_readonly",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Post-Condition — a new Vendor Bill AI Backend record is created
                {
                    content: "The new backend's name appears in the breadcrumb",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Tour Test Backend Create)",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        );

        // IK: docs/vendor_bill_claude_code_backend/02-edit.md
        tour.register(
            "ssi_vendor_bill_claude_code_vendor_bill_claude_code_backend_edit",
            {
                test: true,
                url: "/web",
            },
            [
                // Flow 1 — Open the Vendor Bill AI Backends menu
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
                    content: "Open the Vendor Bill AI Backends menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_vendor_bill_claude_code.menu_vendor_bill_claude_code_backend"]',
                },
                {
                    content: "Vendor Bill AI Backends list is displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Vendor Bill AI Backends)",
                    extra_trigger: ".o_list_view",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 2 — Find and open the record to edit
                {
                    content: "Open the backend to edit",
                    trigger:
                        ".o_data_row:contains(TOUR-BACKEND-EDIT) .o_data_cell:first",
                    extra_trigger: ".o_list_view",
                },
                {
                    content: "Record is open",
                    trigger: ".o_form_view",
                    run: function () {
                        // Assertion only.
                    },
                },
                // 14.0 — the opened record is read-only; click Edit before
                // touching any field.
                {
                    content: "Click the Edit button",
                    trigger: ".o_form_button_edit",
                },
                {
                    content: "Form is now editable",
                    trigger: ".o_form_view.o_form_editable",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 3 — Change the required fields (Name)
                {
                    content: "Change the Name",
                    trigger: ".o_field_widget[name='name']",
                    extra_trigger: ".o_form_view.o_form_editable",
                    run: "text Tour Test Backend Edited",
                },

                // Flow 4 — Change the Claude Code Settings tab
                {
                    content: "Open the Claude Code Settings tab",
                    trigger: ".o_notebook .nav-link:contains(Claude Code Settings)",
                },
                {
                    content: "Change the Base URL",
                    trigger: ".o_field_widget[name='base_url']",
                    extra_trigger: ".o_form_view.o_form_editable",
                    run: "text https://vendor-bill-edited.example.com",
                },

                // Flow 5 — Test Connection is available after the edit (inline
                // action). Not clicked — see Flow 5 of the create tour above.
                {
                    content: "Test Connection button is available",
                    trigger:
                        ".o_statusbar_buttons button[name='action_test_connection']:enabled",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 6 — Click Save
                {
                    content: "Save the record",
                    trigger: ".o_form_button_save",
                },
                {
                    content: "Record is saved",
                    trigger: ".o_form_view.o_form_readonly",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Post-Condition — the record is updated with the new values.
                // A freshly-saved record is read-only; the new Name is only
                // reliably readable as text once back on the readonly form.
                {
                    content: "The new Name appears in the breadcrumb",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Tour Test Backend Edited)",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        );

        // IK: docs/vendor_bill_claude_code_backend/03-delete.md
        tour.register(
            "ssi_vendor_bill_claude_code_vendor_bill_claude_code_backend_delete",
            {
                test: true,
                url: "/web",
            },
            [
                // Flow 1 — Open the Vendor Bill AI Backends menu
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
                    content: "Open the Vendor Bill AI Backends menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_vendor_bill_claude_code.menu_vendor_bill_claude_code_backend"]',
                },
                {
                    content: "Vendor Bill AI Backends list is displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Vendor Bill AI Backends)",
                    extra_trigger: ".o_list_view",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 2 — Open the record, then delete via the form's Action menu
                {
                    content: "Open the backend to delete",
                    trigger:
                        ".o_data_row:contains(TOUR-BACKEND-DELETE) .o_data_cell:first",
                    extra_trigger: ".o_list_view",
                },
                {
                    content: "Record is open",
                    trigger: ".o_form_view",
                    run: function () {
                        // Assertion only.
                    },
                },
                {
                    content: "Open the Action menu",
                    trigger: ".o_cp_action_menus button:contains(Action)",
                },
                {
                    content: "Click Delete",
                    trigger: ".o_cp_action_menus .o_menu_item a",
                    run: function () {
                        var $delete = $(".o_cp_action_menus .o_menu_item a").filter(
                            function () {
                                return $(this).text().trim() === "Delete";
                            }
                        );
                        $delete[0].click();
                    },
                },
                {
                    content: "Confirm deletion",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },
                {
                    content:
                        "Click the [Vendor Bill AI Backends] breadcrumb to return to the list",
                    trigger:
                        ".breadcrumb-item.o_back_button a:contains(Vendor Bill AI Backends)",
                },

                // Post-Condition — the selected record is permanently removed
                {
                    content: "Backend no longer appears in the list",
                    trigger:
                        ".o_list_view:not(:has(.o_data_row:contains(TOUR-BACKEND-DELETE)))",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        );

        // IK: docs/vendor_bill_claude_code_backend/04-deactivate.md
        tour.register(
            "ssi_vendor_bill_claude_code_vendor_bill_claude_code_backend_deactivate",
            {
                test: true,
                url: "/web",
            },
            [
                // Flow 1 — Open the Vendor Bill AI Backends menu
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
                    content: "Open the Vendor Bill AI Backends menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_vendor_bill_claude_code.menu_vendor_bill_claude_code_backend"]',
                },
                {
                    content: "Vendor Bill AI Backends list is displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Vendor Bill AI Backends)",
                    extra_trigger: ".o_list_view",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 2 — Select the record to deactivate
                {
                    content: "Select the backend to deactivate",
                    trigger:
                        ".o_data_row:contains(TOUR-BACKEND-DEACTIVATE) .o_list_record_selector input",
                },

                // Flow 3 — Click Action > Archive
                {
                    content: "Open the Action menu",
                    trigger: ".o_cp_action_menus button:contains(Action)",
                },
                {
                    content: "Click Archive",
                    trigger: ".o_cp_action_menus .o_menu_item a",
                    run: function () {
                        var $archive = $(".o_cp_action_menus .o_menu_item a").filter(
                            function () {
                                return $(this).text().trim() === "Archive";
                            }
                        );
                        $archive[0].click();
                    },
                },

                // Flow 4 — Click OK to confirm
                {
                    content: "Confirm archiving",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },

                // Post-Condition — the record is archived and no longer appears
                // in the default list view
                {
                    content: "Backend no longer appears in the default list view",
                    trigger:
                        ".o_list_view:not(:has(.o_data_row:contains(TOUR-BACKEND-DEACTIVATE)))",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        );

        // IK: docs/vendor_bill_claude_code_backend/05-activate.md
        tour.register(
            "ssi_vendor_bill_claude_code_vendor_bill_claude_code_backend_activate",
            {
                test: true,
                url: "/web",
            },
            [
                // Flow 1 — Open the Vendor Bill AI Backends menu
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
                    content: "Open the Vendor Bill AI Backends menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_vendor_bill_claude_code.menu_vendor_bill_claude_code_backend"]',
                },
                {
                    content: "Vendor Bill AI Backends list is displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Vendor Bill AI Backends)",
                    extra_trigger: ".o_list_view",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 2 — Enable the Archived filter
                {
                    content: "Open the Filters menu",
                    trigger: ".o_cp_searchview .o_filter_menu button",
                },
                {
                    content: "Enable the Archived filter",
                    // Owl dropdown items are not always opened by a synthetic
                    // click — use a native click on the anchor.
                    trigger: ".o_filter_menu .o_menu_item a:contains(Archived)",
                    run: function () {
                        this.$anchor[0].click();
                    },
                },
                {
                    content: "Archived filter is enabled",
                    trigger:
                        ".o_filter_menu .o_menu_item a:contains(Archived)[aria-checked='true']",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 3 — Select the record to reactivate
                {
                    content: "Select the backend to reactivate",
                    trigger:
                        ".o_data_row:contains(TOUR-BACKEND-ACTIVATE) .o_list_record_selector input",
                    extra_trigger: ".o_list_view",
                },

                // Flow 4 — Click Action > Unarchive (no confirmation dialog)
                {
                    content: "Open the Action menu",
                    trigger: ".o_cp_action_menus button:contains(Action)",
                },
                {
                    content: "Click Unarchive",
                    trigger: ".o_cp_action_menus .o_menu_item a",
                    run: function () {
                        var $unarchive = $(".o_cp_action_menus .o_menu_item a").filter(
                            function () {
                                return $(this).text().trim() === "Unarchive";
                            }
                        );
                        $unarchive[0].click();
                    },
                },

                // Post-Condition — the record no longer matches the Archived
                // filter (it is active again) and reappears in the default list
                {
                    content: "Backend no longer appears under the Archived filter",
                    trigger:
                        ".o_list_view:not(:has(.o_data_row:contains(TOUR-BACKEND-ACTIVATE)))",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        );
    }
);
