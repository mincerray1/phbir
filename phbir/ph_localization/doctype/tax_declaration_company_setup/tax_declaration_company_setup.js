// Copyright (c) 2021, SERVIO Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tax Declaration Company Setup', {
	refresh: function(frm) {
        if (!frm.doc.__unsaved) {
            frm.add_custom_button(__('Generate Tax Templates'), function() {            
                let company = frm.doc.company;
                if (company) {
                    frappe.call({
                        method: "phbir.ph_localization.utils.generate_company_tax_templates",
                        type: "POST",
                        args: {
                            'company': company
                        },
                        callback: function(r) {
                            if (!r.exc) {
                                let n = r.message;
                                frappe.msgprint(`Tax template(s) successfully created: <strong>${n}</strong>`);
                                frm.doc.reload();
                            }
                        }
                    });
                }
                else {
                    frappe.msgprint(`Select a company.`);
                }
            });
        }
	}
});
