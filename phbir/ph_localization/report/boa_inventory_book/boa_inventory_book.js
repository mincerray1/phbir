// Copyright (c) 2016, SERVIO Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["BOA Inventory Book"] = {
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
            fieldname:"as_at_date",
            label: __("As At Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1
        },
        // {
        //     fieldname:"as_at_time",
        //     label: __("As At Time"),
        //     fieldtype: "Time",
        //     default: '23:59:59',
        //     reqd: 1
        // },
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
