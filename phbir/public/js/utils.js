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
<<<<<<< HEAD
}

function remove_commas(str) {
    while (str.search(",") >= 0) {
        str = (str + "").replace(',', '');
    }
    return str;
};
=======
}
>>>>>>> 7c932d40d250f471c157f8f8aa277478ba591342
