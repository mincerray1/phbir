// Copyright (c) 2016, SERVIO Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["BOA Sales Journal"] = {
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
            fieldname:"from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -12),
            reqd: 1
        },
        {
            fieldname:"to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1
        }
    ]
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