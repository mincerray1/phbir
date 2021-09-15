// Copyright (c) 2016, SERVIO Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["BIR 0619-F"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
            "reqd": 1
		},
		{
			"fieldname":"year",
			"label": __("Year"),
            "fieldtype": "Select",
            "options": get_years(),
            "reqd": 1
		},
		{
			"fieldname":"month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            "reqd": 1
		},
        {
            fieldname:"due_date",
            label: __("Due Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1
        }
	],
    "onload": function(report) {
        report.page.add_inner_button(__("Print BIR 0619-F"), function() {
            let filter_values = {
                    'company': frappe.query_report.get_filter_value('company'),
                    'year': frappe.query_report.get_filter_value('year'),
                    'month': frappe.query_report.get_filter_value('month'),
                    'due_date': frappe.query_report.get_filter_value('due_date'),
                };
            let u = new URLSearchParams(filter_values).toString();
            
            var bir_form_url = frappe.urllib.get_full_url('/api/method/phbir.ph_localization.bir_forms.bir_0619_f?' + u + '&response_type=pdf');
            let bir_form = window.open(bir_form_url);
        });
    }
};

function get_years() {
    let result = [];
    frappe.call({
        async: false,
        method: "phbir.ph_localization.utils.get_years",
        type: "GET",
        callback: function(r) {
            if (!r.exc) {
                result = r.message;
            }
        }
    });
    return result;
}