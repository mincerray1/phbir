// Copyright (c) 2016, SERVIO Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["BIR 2307"] = {
	"filters": [
		{
			fieldname:"company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
            reqd: 1
		},
        {
            fieldname:"supplier",
            label: __("Supplier"),
            fieldtype: "Link",
            options: "Supplier",
            // reqd: 1
        },
        {
            fieldname:"purchase_invoice",
            label: __("Purchase Invoice"),
            fieldtype: "Link",
            options: "Purchase Invoice",
            reqd: 0
        },
        {
            fieldname:"from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1, 
			on_change: function() {
				frappe.query_report.set_filter_value("to_date", frappe.datetime.add_months(moment(frappe.query_report.get_filter_value('from_date')).endOf('month'), 2));
				frappe.query_report.refresh();
			}

        },
        {
            fieldname:"to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1
        }
    ],
	onload: function(report) {
		report.page.add_inner_button(__("Print BIR 2307"), function() {
            // frappe.call({
            //     async: false,
            //     method: "phbir.ph_localization.bir_forms.bir_2307",
            //     type: "GET",
            //     args: {
            //         'filters': frappe.query_report.filters
            //     },
            //     callback: function(r) {
            //         if (!r.exc) {
            //             frappe.msgprint("hello");
            //         }
            //     }
            // });
            let u = new URLSearchParams(frappe.query_report.filters).toString();
            let bir_form_url = `/api/method/phbir.ph_localization.bir_forms.bir_2307?${u}&response_type=pdf`;
            let bir_form = window.open(bir_form_url);
		});
	}
};

function get_company_information(company){
    let company_information = {};
    frappe.call({
        async: false,
        method: "phbir.ph_localization.utils.get_company_information",
        type: "GET",
        args: {
            'company': company
        },
        callback: function(r) {
            if (!r.exc) {
                company_information = r.message;
            }
        }
    });
    return company_information
}