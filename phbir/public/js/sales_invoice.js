frappe.ui.form.on('Sales Taxes and Charges', {
    atc_rate: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (frm.doc.docstatus == 0 && row.charge_type != 'Actual') {
            frappe.model.set_value(cdt, cdn, "rate", row.atc_rate);
            refresh_field("rate");
        }
    },
    
    atc: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (frm.doc.docstatus == 0 && !row.atc) {
            frappe.model.set_value(cdt, cdn, "atc_rate", 0);
            refresh_field("atc_rate");
        }
    }
});