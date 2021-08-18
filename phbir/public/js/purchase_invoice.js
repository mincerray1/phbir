
frappe.ui.form.on('Purchase Invoice', {
    refresh: function(frm) {
        if(frm.doc.is_return == 0) {
            frm.add_custom_button(__('BIR 2307'), function() {
                frappe.route_options = {
                    company: frm.doc.company,
                    supplier: frm.doc.supplier,
                    purchase_invoice: frm.doc.name,
                    from_date: moment(frm.doc.posting_date).format('YYYY-MM-DD'),
                    to_date: moment(frm.doc.posting_date).format('YYYY-MM-DD')
                };
                frappe.set_route("query-report", "BIR 2307");
            }, __("View"));
        }
    }
});