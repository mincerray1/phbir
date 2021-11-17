# Copyright (c) 2013, SERVIO Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import (getdate)
from frappe import _

def execute(filters=None):
    company = filters.company
    tax_declaration_company_setup = frappe.get_doc('Tax Declaration Company Setup', company)
    tax_declaration_company_setup = None
    try:
        tax_declaration_company_setup = frappe.get_doc('Tax Declaration Company Setup', company)
    except:
        frappe.throw("Please create a Tax Declaration Company Setup record for {0}".format(company))

    columns, data = [], []
    data = get_data(filters)
    columns = get_columns()
    return columns, data

def get_data(filters):
    data = [
        {
            'bir_2550m': '✓'
        }
    ]

    return data

def get_columns():
    columns = [
        {
            "fieldname": "bir_2550m",
            "label": _("BIR 2550M"),
            "fieldtype": "Data",
            "width": 120
        }
    ]

    return columns