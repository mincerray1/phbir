import frappe
from frappe import _
from frappe.utils.pdf import get_pdf
from datetime import datetime
from phbir.ph_localization.utils import get_company_information, get_supplier_information
import pytz
import json

options = {
    "margin-left": "0mm",
    "margin-right": "0mm",
    "margin-top": "0mm",
    "margin-bottom": "0mm"
}


@frappe.whitelist()
def bir_2307(company, supplier, purchase_invoice, from_date, to_date, response_type="pdf"):
    # check 2307 perms instead
    if frappe.session.user=='Guest':
        frappe.throw(_("You need to be logged in to access this page"), frappe.PermissionError)

    filters = {
        'company' : company, 
        'supplier': supplier, 
        'purchase_invoice': purchase_invoice, 
        'from_date': from_date, 
        'to_date': to_date
    }

    from phbir.ph_localization.report.bir_2307.bir_2307 import get_data as get_data_bir_2307
    data = get_data_bir_2307(filters, 1)

    context = {
        'data': data,
        'payor': get_company_information(company),
        'payee': get_supplier_information(supplier)
    }

    filename = "BIR 2307"
    
    context["build_version"] = frappe.utils.get_build_version()
    html = frappe.render_template("templates/bir_forms/bir_2307_template.html", context)
    options["page-size"] = "Legal"

    return_document(html, filename, options, response_type)

@frappe.whitelist()
def return_document(html, filename="document", options=options, response_type="download"):
    frappe.local.response.filename = "{filename}.pdf".format(filename=filename)
    frappe.local.response.filecontent = get_pdf(html, options)
    frappe.local.response.type = response_type

def make_ordinal(n):
    '''
    Convert an integer into its ordinal representation::

        make_ordinal(0)   => '0th'
        make_ordinal(3)   => '3rd'
        make_ordinal(122) => '122nd'
        make_ordinal(213) => '213th'
    '''
    n = int(n)
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return str(n) + suffix