// Copyright (c) 2021, SERVIO Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tax Declaration Setup', {
	refresh: function(frm) {
        frm.add_custom_button(__('Generate Tax Templates'), function() {            
            frappe.call({
                method: "phbir.ph_localization.utils.generate_tax_templates",
                type: "POST",
                callback: function(r) {
                    if (!r.exc) {
                        let n = r.message;
                        frappe.msgprint(`Tax template(s) successfully created: <strong>${n}</strong>`);
                        frm.doc.reload();
                    }
                }
            });
        });
	}
});
