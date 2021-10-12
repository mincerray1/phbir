// Copyright (c) 2016, SERVIO Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

{% include 'phbir/public/js/utils.js' %}

frappe.query_reports["RELIEF Summary List of Sales"] = {
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
            "default": moment(frappe.datetime.get_today()).year(),
            "reqd": 1
		},
		{
			"fieldname":"month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            "default": moment(frappe.datetime.get_today()).month(),
            "reqd": 1
		},
	],
<<<<<<< HEAD
    "onload": function(report) {
        report.page.remove_inner_button(__("Set Chart"));
        report.page.add_inner_button(__("Generate Data File (.DAT)"), function() {
            let d = new frappe.ui.Dialog({
                title: 'Enter details',
                fields: [
                    {
                        label: 'Fiscal Month End',
                        fieldname: 'fiscal_month_end',
                        fieldtype: 'Select',
                        options: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
                        default: '12'
                    },
                ],
                primary_action_label: 'Submit',
                primary_action(values) {
                    d.hide();

                    let filters = {
                        'company': frappe.query_report.get_filter_value('company'),
                        'year': frappe.query_report.get_filter_value('year'),
                        'month': frappe.query_report.get_filter_value('month'),
                    };
                    let context = Object.assign({}, filters, values);
                    let u = new URLSearchParams(context).toString();
                    
                    var sls_url = frappe.urllib.get_full_url('/api/method/phbir.ph_localization.report.relief_summary_list_of_sales.relief_summary_list_of_sales.generate_sls_data_file?' + u + '&response_type=download');
                    let sls = window.open(sls_url);
                }
            });
            
            d.show();
        });
    }
=======
>>>>>>> 7c932d40d250f471c157f8f8aa277478ba591342
};
