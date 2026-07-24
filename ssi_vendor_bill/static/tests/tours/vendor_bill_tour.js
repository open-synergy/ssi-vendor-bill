// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define("ssi_vendor_bill.vendor_bill_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    // Shared navigation block reused by every tour below -- corresponds to
    // Flow 1 of every vendor_bill IK: "Open the Financial Accounting >
    // Account Payable > Vendor Bill menu."
    function openVendorBillList() {
        return [
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
                content: "Open the Vendor Bill menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_vendor_bill.vendor_bill_menu"]',
            },
            {
                // Gerbang: tunggu action TUJUAN benar-benar terpasang, bukan
                // sekadar "ada list di layar" (lihat patterns.md skill
                // odoo-development-ui-test §A).
                content: "Vendor Bills list is displayed",
                trigger: ".o_control_panel .breadcrumb-item.active:contains(Vendor Bills)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only.
                },
            },
        ];
    }

    // IK: docs/vendor_bill/01-create.md
    tour.register(
        "ssi_vendor_bill_vendor_bill_create",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Financial Accounting > Account Payable >
            // Vendor Bill menu.
            openVendorBillList(),
            [
                // Flow 2 -- Click the New button.
                {
                    content: "Click New",
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

                // Flow 3 -- Fill in the required fields: Type.
                {
                    content: "Select the vendor bill type",
                    trigger: ".o_field_many2one[name='type_id'] input",
                    extra_trigger: ".o_form_view.o_form_editable",
                    run: "text TOUR Vendor Bill Type",
                },
                {
                    content: "Pick the type from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR Vendor Bill Type)",
                    in_modal: false,
                },

                // Flow 3 -- Partner.
                {
                    content: "Select the vendor",
                    trigger: ".o_field_many2one[name='partner_id'] input",
                    run: "text TOUR Create Vendor",
                },
                {
                    content: "Pick the vendor from the dropdown",
                    trigger: ".ui-autocomplete .ui-menu-item a:contains(TOUR Create Vendor)",
                    in_modal: false,
                },

                // Flow 3 -- Date Due (required; no default, unlike Date).
                {
                    content: "Fill in Date Due",
                    trigger: ".o_field_widget[name='date_due'] input",
                    run: "text 12/31/2030",
                },

                // Flow 3 -- Currency.
                {
                    content: "Select the currency",
                    trigger: ".o_field_many2one[name='currency_id'] input",
                    run: "text USD",
                },
                {
                    content: "Pick the currency from the dropdown",
                    trigger: ".ui-autocomplete .ui-menu-item a:contains(USD)",
                    in_modal: false,
                },

                // Flow 3 -- Pricelist.
                {
                    content: "Select the pricelist",
                    trigger: ".o_field_many2one[name='pricelist_id'] input",
                    run: "text Public Pricelist",
                },
                {
                    content: "Pick the pricelist from the dropdown",
                    trigger: ".ui-autocomplete .ui-menu-item a:contains(Public Pricelist)",
                    in_modal: false,
                },
                // Journal and Payable Account are automatically filled from
                // Type (onchange) -- IK step 3 says "Change if needed", so
                // the tour leaves them as-is.

                // Flow 5 -- On the Detail tab, add a line.
                {
                    content: "Open the Detail tab",
                    trigger: ".o_notebook .nav-link:contains(Detail)",
                },
                {
                    content: "Add a line",
                    trigger: ".o_field_x2many .o_field_x2many_list_row_add a",
                },
                {
                    content: "Select the product",
                    trigger: ".o_selected_row .o_field_widget[name='product_id'] input",
                    run: "text TOUR Vendor Bill Product",
                },
                {
                    content: "Pick the product from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR Vendor Bill Product)",
                    in_modal: false,
                },
                // Description and UoM are automatically filled from Product.
                {
                    content: "Select the account",
                    trigger: ".o_selected_row .o_field_widget[name='account_id'] input",
                    run: "text TOUR Vendor Bill Expense",
                },
                {
                    content: "Pick the account from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR Vendor Bill Expense)",
                    in_modal: false,
                },
                {
                    // Commit the last edited cell by selecting another
                    // already-existing cell on the same row -- never
                    // `press Tab` (patterns.md skill odoo-development-ui-test
                    // §C jebakan 2).
                    content: "Commit the line",
                    trigger: ".o_selected_row .o_field_widget[name='product_id']",
                    run: "click",
                },

                // Flow 6 -- Click Save.
                {
                    content: "Save the record",
                    trigger: ".o_form_button_save",
                },

                // Post-Condition -- a new record is created in Draft status.
                {
                    content: "Record is saved",
                    trigger: ".o_form_view.o_form_readonly",
                    run: function () {
                        // Assertion only.
                    },
                },
                {
                    content: "Status is Draft",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='draft'].btn-primary",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/vendor_bill/02-edit.md
    tour.register(
        "ssi_vendor_bill_vendor_bill_edit",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Vendor Bill menu.
            openVendorBillList(),
            [
                // Flow 2 -- Find and open the record to edit.
                {
                    content: "Open the record",
                    trigger: ".o_data_row:contains(TOUR Edit Vendor) .o_data_cell:first",
                    extra_trigger: ".o_list_view",
                },
                {
                    content: "Form is open",
                    trigger: ".o_form_view",
                    run: function () {
                        // Assertion only.
                    },
                },
                // 14.0: an existing record opens read-only -- Edit first.
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

                // Flow 3 -- Change a header field.
                {
                    content: "Change the Vendor Document Number",
                    trigger: ".o_field_widget[name='partner_document_number']",
                    run: "text TOUR Edited Document Number",
                },

                // Flow 4 -- Click Save.
                {
                    content: "Save the record",
                    trigger: ".o_form_button_save",
                },

                // Post-Condition -- the record is updated with the new value.
                {
                    content: "Record is saved",
                    trigger: ".o_form_view.o_form_readonly",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/vendor_bill/03-delete.md
    tour.register(
        "ssi_vendor_bill_vendor_bill_delete",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Vendor Bill menu.
            openVendorBillList(),
            [
                // Flow 2 -- Select the record to delete (checkbox).
                {
                    content: "Select the record to delete",
                    trigger:
                        ".o_data_row:contains(TOUR Delete Vendor) .o_list_record_selector input",
                    run: "click",
                },

                // Flow 3 -- Click Action > Delete.
                {
                    content: "Open the Action menu",
                    trigger: ".o_cp_action_menus button:contains(Action)",
                },
                {
                    content: "Click Delete",
                    // Item Action menu adalah komponen Owl; cocokkan LABEL
                    // PERSIS -- :contains(Delete) sebagai substring bisa
                    // keliru menunjuk item lain (mis. "Archive"). Lihat
                    // patterns.md skill odoo-development-ui-test §I.
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

                // Flow 4 -- Click OK to confirm.
                {
                    content: "Confirm deletion",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },

                // Post-Condition -- the record is permanently removed.
                {
                    content: "Record no longer appears in the list",
                    trigger:
                        ".o_list_view:not(:has(.o_data_row:contains(TOUR Delete Vendor)))",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/vendor_bill/04-confirm.md
    tour.register(
        "ssi_vendor_bill_vendor_bill_confirm",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Vendor Bill menu.
            openVendorBillList(),
            [
                // Flow 2 -- Open the record to confirm.
                {
                    content: "Open the record",
                    trigger: ".o_data_row:contains(TOUR Confirm Vendor) .o_data_cell:first",
                    extra_trigger: ".o_list_view",
                },
                {
                    trigger: ".o_form_view",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 3 -- Click the Confirm button.
                {
                    content: "Click the Confirm button",
                    trigger: ".o_statusbar_buttons button[name='action_confirm']",
                    extra_trigger: ".o_form_view",
                },

                // Flow 4 -- Click OK on the confirmation dialog.
                {
                    content: "Confirm the dialog",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },

                // Post-Condition -- status changes to Waiting for Approval.
                {
                    content: "Status is Waiting for Approval",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='confirm'].btn-primary",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/vendor_bill/05-approve.md
    tour.register(
        "ssi_vendor_bill_vendor_bill_approve",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Vendor Bill menu.
            openVendorBillList(),
            [
                // Flow 2 -- Open the record to approve.
                {
                    content: "Open the record",
                    trigger:
                        ".o_data_row:contains(TOUR Approve Vendor) .o_data_cell:first",
                    extra_trigger: ".o_list_view",
                },
                {
                    trigger: ".o_form_view",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 3 -- Click the Approve button.
                {
                    content: "Click the Approve button",
                    trigger:
                        ".o_statusbar_buttons button[name='action_approve_approval']",
                    extra_trigger: ".o_form_view",
                },

                // Flow 4 -- Click OK on the confirmation dialog.
                {
                    content: "Confirm the dialog",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },

                // Post-Condition -- all approval levels fulfilled: record
                // moves to Unpaid (document has one detail line).
                {
                    content: "Status is Unpaid",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='open'].btn-primary",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/vendor_bill/06-reject.md
    tour.register(
        "ssi_vendor_bill_vendor_bill_reject",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Vendor Bill menu.
            openVendorBillList(),
            [
                // Flow 2 -- Open the record to reject.
                {
                    content: "Open the record",
                    trigger: ".o_data_row:contains(TOUR Reject Vendor) .o_data_cell:first",
                    extra_trigger: ".o_list_view",
                },
                {
                    trigger: ".o_form_view",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 3 -- Click the Reject button.
                {
                    content: "Click the Reject button",
                    trigger: ".o_statusbar_buttons button[name='action_reject_approval']",
                    extra_trigger: ".o_form_view",
                },

                // Flow 4 -- Click OK on the confirmation dialog.
                {
                    content: "Confirm the dialog",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },

                // Post-Condition -- status changes to Rejected.
                {
                    content: "Status is Rejected",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='reject'].btn-primary",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/vendor_bill/10-cancel.md
    tour.register(
        "ssi_vendor_bill_vendor_bill_cancel",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Vendor Bill menu.
            openVendorBillList(),
            [
                // Flow 2 -- Open the record to cancel.
                {
                    content: "Open the record",
                    trigger: ".o_data_row:contains(TOUR Cancel Vendor) .o_data_cell:first",
                    extra_trigger: ".o_list_view",
                },
                {
                    trigger: ".o_form_view",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 3 -- Click the Cancel button (opens the reason
                // wizard; the rendered button name is a numeric action id,
                // so match by label instead of button[name=...]).
                {
                    content: "Click the Cancel button",
                    trigger: ".o_statusbar_buttons button:enabled:contains('Cancel')",
                    extra_trigger: ".o_form_view",
                },
                {
                    // 14.0: JANGAN prefiks trigger in-modal dengan `.modal`
                    // (lihat patterns.md skill odoo-development-ui-test §H).
                    content: "Wizard is open",
                    trigger: ".o_form_view",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 4 -- Select the Cancellation Reason (radio widget).
                {
                    content: "Select the cancellation reason",
                    trigger:
                        ".o_field_widget[name='cancel_reason_id'] " +
                        ".o_radio_item:contains(TOUR Vendor Bill Cancel Reason) input",
                    run: "click",
                },

                // Flow 5 -- Click Confirm.
                {
                    content: "Confirm the wizard",
                    trigger: ".modal-footer button[name='action_confirm']",
                },
                {
                    // The wizard's Confirm button itself carries a
                    // "Are you sure?" confirm attribute, stacking a second
                    // dialog on top; `$modal_displayed` now resolves to that
                    // topmost dialog.
                    content: "Confirm the Are you sure? dialog",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },

                // Post-Condition -- status changes to Cancelled.
                {
                    content: "Status is Cancelled",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='cancel'].btn-primary",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/vendor_bill/12-restart.md
    tour.register(
        "ssi_vendor_bill_vendor_bill_restart",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Vendor Bill menu.
            openVendorBillList(),
            [
                // Flow 2 -- Open the record to restart.
                {
                    content: "Open the record",
                    trigger:
                        ".o_data_row:contains(TOUR Restart Vendor) .o_data_cell:first",
                    extra_trigger: ".o_list_view",
                },
                {
                    trigger: ".o_form_view",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 3 -- Click the Restart button.
                {
                    content: "Click the Restart button",
                    trigger: ".o_statusbar_buttons button[name='action_restart']",
                    extra_trigger: ".o_form_view",
                },

                // Flow 4 -- Click OK on the confirmation dialog.
                {
                    content: "Confirm the dialog",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },

                // Post-Condition -- status returns to Draft.
                {
                    content: "Status is Draft",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='draft'].btn-primary",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/vendor_bill/14-compute-tax.md
    tour.register(
        "ssi_vendor_bill_vendor_bill_compute_tax",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Vendor Bill menu.
            openVendorBillList(),
            [
                // Flow 2 -- Open the record.
                {
                    content: "Open the record",
                    trigger:
                        ".o_data_row:contains(TOUR Compute Tax Vendor) .o_data_cell:first",
                    extra_trigger: ".o_list_view",
                },
                {
                    trigger: ".o_form_view",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 3 -- On the Detail tab, click the Compute Tax button.
                {
                    content: "Open the Detail tab",
                    trigger: ".o_notebook .nav-link:contains(Detail)",
                },
                {
                    content: "Click the Compute Tax button",
                    trigger: "button[name='action_compute_tax']",
                    extra_trigger: ".o_form_view",
                },

                // Post-Condition -- the Taxes table is recomputed (values
                // are not asserted here -- that is unit test territory).
                // The tour only verifies the form stays rendered and the
                // button remains clickable.
                {
                    content: "Form remains rendered and Compute Tax stays clickable",
                    trigger: ".o_form_view button[name='action_compute_tax']:enabled",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );
});
