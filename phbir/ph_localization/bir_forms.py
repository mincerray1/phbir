import frappe
from frappe import _
from frappe.utils.pdf import get_pdf
from frappe.utils import getdate
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
    frappe.has_permission('BIR 2307', throw=True)

    from phbir.ph_localization.report.bir_2307.bir_2307 import get_data as get_data_bir_2307
    data = get_data_bir_2307(company, supplier, purchase_invoice, from_date, to_date)

    data_ip = []
    data_mp = []

    ip_month_1_total = 0
    ip_month_2_total = 0
    ip_month_3_total = 0
    ip_grand_total = 0
    ip_tax_withheld_for_the_quarter_total = 0

    mp_month_1_total = 0
    mp_month_2_total = 0
    mp_month_3_total = 0
    mp_grand_total = 0
    mp_tax_withheld_for_the_quarter_total = 0

    for entry in data:
        if entry.payment_type == 'Income Payment':
            ip_month_1_total = ip_month_1_total + entry.month_1
            ip_month_2_total = ip_month_2_total + entry.month_2
            ip_month_3_total = ip_month_3_total + entry.month_3
            ip_grand_total = ip_grand_total + entry.total
            ip_tax_withheld_for_the_quarter_total = ip_tax_withheld_for_the_quarter_total + entry.tax_withheld_for_the_quarter

            data_ip.append(entry)
        elif entry.payment_type == 'Money Payment':
            mp_month_1_total = mp_month_1_total + entry.month_1
            mp_month_2_total = mp_month_2_total + entry.month_2
            mp_month_3_total = mp_month_3_total + entry.month_3
            mp_grand_total = mp_grand_total + entry.total
            mp_tax_withheld_for_the_quarter_total = mp_tax_withheld_for_the_quarter_total + entry.tax_withheld_for_the_quarter

            data_mp.append(entry)

    context = {
        'from_date': getdate(from_date),
        'to_date': getdate(to_date),
        'payor': get_company_information(company),
        'payee': get_supplier_information(supplier),
        'data_ip': data_ip,
        'ip_month_1_total': ip_month_1_total,
        'ip_month_2_total': ip_month_2_total,
        'ip_month_3_total': ip_month_3_total,
        'ip_grand_total': ip_grand_total,
        'ip_tax_withheld_for_the_quarter_total': ip_tax_withheld_for_the_quarter_total,
        'data_mp': data_mp,
        'mp_month_1_total': mp_month_1_total,
        'mp_month_2_total': mp_month_2_total,
        'mp_month_3_total': mp_month_3_total,
        'mp_grand_total': mp_grand_total,
        'mp_tax_withheld_for_the_quarter_total': mp_tax_withheld_for_the_quarter_total
    }

    filename = "BIR 2307"
    
    context["build_version"] = frappe.utils.get_build_version()
    html = frappe.render_template("templates/bir_forms/bir_2307_template.html", context)
    options["page-size"] = "Legal"

    return_document(html, filename, options, response_type)

def bir_2307(company, year, month, response_type="pdf"):
    frappe.has_permission('BIR 2550M', throw=True)

    from phbir.ph_localization.report.bir_2307.bir_2307 import get_data as get_data_bir_2307
    data = get_data_bir_2307(company, supplier, purchase_invoice, from_date, to_date)

    data_ip = []
    data_mp = []

    ip_month_1_total = 0
    ip_month_2_total = 0
    ip_month_3_total = 0
    ip_grand_total = 0
    ip_tax_withheld_for_the_quarter_total = 0

    mp_month_1_total = 0
    mp_month_2_total = 0
    mp_month_3_total = 0
    mp_grand_total = 0
    mp_tax_withheld_for_the_quarter_total = 0

    for entry in data:
        if entry.payment_type == 'Income Payment':
            ip_month_1_total = ip_month_1_total + entry.month_1
            ip_month_2_total = ip_month_2_total + entry.month_2
            ip_month_3_total = ip_month_3_total + entry.month_3
            ip_grand_total = ip_grand_total + entry.total
            ip_tax_withheld_for_the_quarter_total = ip_tax_withheld_for_the_quarter_total + entry.tax_withheld_for_the_quarter

            data_ip.append(entry)
        elif entry.payment_type == 'Money Payment':
            mp_month_1_total = mp_month_1_total + entry.month_1
            mp_month_2_total = mp_month_2_total + entry.month_2
            mp_month_3_total = mp_month_3_total + entry.month_3
            mp_grand_total = mp_grand_total + entry.total
            mp_tax_withheld_for_the_quarter_total = mp_tax_withheld_for_the_quarter_total + entry.tax_withheld_for_the_quarter

            data_mp.append(entry)

    context = {
        'from_date': getdate(from_date),
        'to_date': getdate(to_date),
        'payor': get_company_information(company),
        'payee': get_supplier_information(supplier),
        'data_ip': data_ip,
        'ip_month_1_total': ip_month_1_total,
        'ip_month_2_total': ip_month_2_total,
        'ip_month_3_total': ip_month_3_total,
        'ip_grand_total': ip_grand_total,
        'ip_tax_withheld_for_the_quarter_total': ip_tax_withheld_for_the_quarter_total,
        'data_mp': data_mp,
        'mp_month_1_total': mp_month_1_total,
        'mp_month_2_total': mp_month_2_total,
        'mp_month_3_total': mp_month_3_total,
        'mp_grand_total': mp_grand_total,
        'mp_tax_withheld_for_the_quarter_total': mp_tax_withheld_for_the_quarter_total
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