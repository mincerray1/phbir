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
            reqd: 1
        },
        {
            fieldname:"purchase_invoice",
            label: __("Purchase Invoice"),
            fieldtype: "Link",
            options: "Purchase Invoice",
			get_query: () => {
				var supplier = frappe.query_report.get_filter_value('supplier');
				return {
					filters: {
						'supplier': supplier
					}
				}
			},
            reqd: 0
        },
        {
            fieldname:"from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: moment(frappe.datetime.get_today()).startOf('quarter'),
            reqd: 1, 
			on_change: function() {
				frappe.query_report.set_filter_value("to_date", frappe.datetime.add_days(frappe.datetime.add_months(frappe.query_report.get_filter_value('from_date'), 3), -1));
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
            let filter_values = {
                    'company': frappe.query_report.get_filter_value('company'),
                    'supplier': frappe.query_report.get_filter_value('supplier'),
                    'purchase_invoice': frappe.query_report.get_filter_value('purchase_invoice'),
                    'from_date': frappe.query_report.get_filter_value('from_date'),
                    'to_date': frappe.query_report.get_filter_value('to_date'),
                };
            let u = new URLSearchParams(filter_values).toString();
            
            var bir_form_url = frappe.urllib.get_full_url(
                '/api/method/phbir.ph_localization.bir_forms.bir_2307?' + u + '&response_type=pdf')
            $.ajax({
                url: bir_form_url,
                type: 'GET',
                success: function(result) {
                    if(jQuery.isEmptyObject(result)){
                        frappe.msgprint(__('No Records for these filters'));
                    }
                    else{
                        let bir_form = window.open(bir_form_url);
                    }
                }
            });
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