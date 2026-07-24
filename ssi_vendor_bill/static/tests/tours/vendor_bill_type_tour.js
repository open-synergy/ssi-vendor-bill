// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define("ssi_vendor_bill.vendor_bill_type_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    // Shared navigation block reused by every tour below -- corresponds to
    // Flow 1 of every vendor_bill_type IK: "Open the Financial Accounting >
    // Configuration > Vendor Bill Types menu."
    function openVendorBillTypeList() {
        return [
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
                content: "Open the Vendor Bill Types menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_vendor_bill.vendor_bill_type_menu"]',
            },
            {
                // Gerbang: tunggu action TUJUAN benar-benar terpasang, bukan
                // sekadar "ada list di layar" (lihat patterns.md skill
                // odoo-development-ui-test §A).
                content: "Vendor Bill Types list is displayed",
                trigger:
                    ".o_control_panel .breadcrumb-item.active:contains(Vendor Bill Types)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only.
                },
            },
        ];
    }

    // IK: docs/vendor_bill_type/01-create.md
    tour.register(
        "ssi_vendor_bill_vendor_bill_type_create",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Financial Accounting > Configuration >
            // Vendor Bill Types menu.
            openVendorBillTypeList(),
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

                // Flow 3 -- Fill in the required fields: Name, Code.
                {
                    content: "Fill in the Name",
                    trigger: ".o_field_widget[name='name']",
                    extra_trigger: ".o_form_view.o_form_editable",
                    run: "text TOUR VBT Create",
                },
                {
                    content: "Fill in the Code",
                    trigger: ".o_field_widget[name='code']",
                    run: "text /",
                },

                // Flow 4 -- On the Accounting tab, select Journal and
                // Payable Account.
                {
                    content: "Open the Accounting tab",
                    trigger: ".o_notebook .nav-link:contains(Accounting)",
                },
                {
                    content: "Select the journal",
                    trigger: ".o_field_many2one[name='journal_id'] input",
                    run: "text TOUR Vendor Bill Type Journal",
                },
                {
                    content: "Pick the journal from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR Vendor Bill Type Journal)",
                    in_modal: false,
                },
                {
                    content: "Select the payable account",
                    trigger: ".o_field_many2one[name='payable_account_id'] input",
                    run: "text TOUR Vendor Bill Type Payable",
                },
                {
                    content: "Pick the payable account from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR Vendor Bill Type Payable)",
                    in_modal: false,
                },

                // Flow 5 -- Go to the Product Configuration tab. Selection
                // Method is left at its "Domain" default -- asserting the
                // allow-list values themselves is unit test territory, not
                // tour territory.
                {
                    content: "Open the Product Configuration tab",
                    trigger: ".o_notebook .nav-link:contains(Product Configuration)",
                },
                {
                    content: "Product Configuration tab is displayed",
                    trigger: ".o_field_widget[name='product_selection_method']",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 6 -- Go to the Currency Configuration tab.
                {
                    content: "Open the Currency Configuration tab",
                    trigger: ".o_notebook .nav-link:contains(Currency Configuration)",
                },
                {
                    content: "Currency Configuration tab is displayed",
                    trigger: ".o_field_widget[name='currency_selection_method']",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 7 -- Go to the Pricelist Configuration tab.
                {
                    content: "Open the Pricelist Configuration tab",
                    trigger: ".o_notebook .nav-link:contains(Pricelist Configuration)",
                },
                {
                    content: "Pricelist Configuration tab is displayed",
                    trigger: ".o_field_widget[name='pricelist_selection_method']",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 8 -- Click Save.
                {
                    content: "Save the record",
                    trigger: ".o_form_button_save",
                },

                // Post-Condition -- a new Vendor Bill Type record is
                // created (availability as Type on a vendor bill is
                // exercised by the ssi_vendor_bill_vendor_bill_create tour).
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

    // IK: docs/vendor_bill_type/02-edit.md
    tour.register(
        "ssi_vendor_bill_vendor_bill_type_edit",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Vendor Bill Types menu.
            openVendorBillTypeList(),
            [
                // Flow 2 -- Find and open the record to edit.
                {
                    content: "Open the record",
                    trigger: ".o_data_row:contains(TOUR VBT Edit) .o_data_cell:first",
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

                // Flow 3 -- Change the required fields.
                {
                    content: "Change the Name",
                    trigger: ".o_field_widget[name='name']",
                    run: "text TOUR VBT Edit Changed",
                },

                // Flow 4 -- Click Save.
                {
                    content: "Save the record",
                    trigger: ".o_form_button_save",
                },

                // Post-Condition -- the record is updated with the new
                // values.
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

    // IK: docs/vendor_bill_type/03-delete.md
    tour.register(
        "ssi_vendor_bill_vendor_bill_type_delete",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Vendor Bill Types menu.
            openVendorBillTypeList(),
            [
                // Flow 2 -- Select the record to delete (checkbox).
                {
                    content: "Select the record to delete",
                    trigger:
                        ".o_data_row:contains(TOUR VBT Delete) .o_list_record_selector input",
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
                    // keliru menunjuk item lain. Lihat patterns.md skill
                    // odoo-development-ui-test §I.
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

                // Post-Condition -- the selected record is permanently
                // removed from the system.
                {
                    content: "Record no longer appears in the list",
                    trigger:
                        ".o_list_view:not(:has(.o_data_row:contains(TOUR VBT Delete)))",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/vendor_bill_type/04-deactivate.md
    tour.register(
        "ssi_vendor_bill_vendor_bill_type_deactivate",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Vendor Bill Types menu.
            openVendorBillTypeList(),
            [
                // Flow 2 -- Select the record to deactivate (checkbox).
                {
                    content: "Select the record to deactivate",
                    trigger:
                        ".o_data_row:contains(TOUR VBT Deactivate) .o_list_record_selector input",
                    run: "click",
                },

                // Flow 3 -- Click Action > Archive.
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

                // Flow 4 -- Click OK to confirm.
                {
                    content: "Confirm the dialog",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },

                // Post-Condition -- the record is archived and no longer
                // appears in the default (active) list view. (Its
                // unavailability as Type on new vendor bills, and that
                // existing vendor bills already using it are unaffected,
                // are not kasatmata UI facts -- out of tour scope.)
                {
                    content: "Record no longer appears in the active list",
                    trigger:
                        ".o_list_view:not(:has(.o_data_row:contains(TOUR VBT Deactivate)))",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/vendor_bill_type/05-activate.md
    tour.register(
        "ssi_vendor_bill_vendor_bill_type_activate",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Vendor Bill Types menu.
            openVendorBillTypeList(),
            [
                // Flow 2 -- Enable the Archived filter in the search bar.
                {
                    content: "Open the Filters menu",
                    trigger: ".o_filter_menu .o_dropdown_toggler_btn",
                    // 14.0: the Filters dropdown is an Owl component that
                    // does not always open on a synthetic click -- use a
                    // real browser click (patterns.md skill
                    // odoo-development-ui-test §I/§J).
                    run: function () {
                        this.$anchor[0].click();
                    },
                },
                {
                    content: "Enable the Archived filter",
                    trigger: ".o_filter_menu .o_menu_item a:contains(Archived)",
                    run: function () {
                        this.$anchor[0].click();
                    },
                },

                // Flow 3 -- Select the record to reactivate (checkbox).
                {
                    content: "Select the record to reactivate",
                    trigger:
                        ".o_data_row:contains(TOUR VBT Activate) .o_list_record_selector input",
                    run: "click",
                },

                // Flow 4 -- Click Action > Unarchive.
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

                // Flow 5 (IK text) -- "Click OK to confirm." Verified
                // against Odoo 14.0 core
                // (web/static/src/js/views/list/list_controller.js
                // `_getActionMenuItems`): only the "Archive" action wraps
                // its callback in `Dialog.confirm(...)`; "Unarchive" calls
                // `_toggleArchiveState(false)` directly with no
                // confirmation dialog. There is therefore no dialog step
                // to add here -- this is a known inaccuracy in the IK
                // text (docs/vendor_bill_type/05-activate.md), out of
                // scope for this tour-only change.

                // Enable/disable the Archived filter re-opens the Filters
                // dropdown -- selecting "Unarchive" above closed it
                // (any click outside the dropdown closes it; see
                // web.DropdownMenu `_onWindowClick`).
                {
                    content: "Open the Filters menu again",
                    trigger: ".o_filter_menu .o_dropdown_toggler_btn",
                    run: function () {
                        this.$anchor[0].click();
                    },
                },
                {
                    content: "Disable the Archived filter",
                    trigger: ".o_filter_menu .o_menu_item a:contains(Archived)",
                    run: function () {
                        this.$anchor[0].click();
                    },
                },

                // Post-Condition -- the record is restored and appears
                // again in the default (active) list view.
                {
                    content: "Record appears again in the active list",
                    trigger: ".o_data_row:contains(TOUR VBT Activate)",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );
});
