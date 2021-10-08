# Copyright (c) 2013, SERVIO Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate
from phbir.ph_localization.utils import get_company_information, get_customer_information
from phbir.ph_localization.bir_forms import return_document

def execute(filters=None):
    columns, data = [], []

    data = get_data(filters.company, filters.year, filters.month)
    columns = get_columns()

    return columns, data

def get_data(company, year, month):
    result = []

    return result

def get_columns():
    columns = [
        {
            "fieldname": "tin_with_dash",
            "label": _("TIN"),
            "fieldtype": "Data",
            "width": 180
        },
        {
            "fieldname": "registered_name",
            "label": _("Registered Name"),
            "fieldtype": "Link",
            "options": "Customer",
            "width": 200
        },
        {
            "fieldname": "individual",
            "label": _("Individual"),
            "fieldtype": "Data",
            "width": 220
        },
        {
            "fieldname": "atc",
            "label": _("ATC"),
            "fieldtype": "Link",
            "options": "ATC",
            "width": 80
        },
        {
            "fieldname": "income_payment",
            "label": _("Income Payment"),
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "fieldname": "formatted_atc_rate",
            "label": _("Tax Rate"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "tax_withheld",
            "label": _("Tax Withheld"),
            "fieldtype": "Currency",
            "width": 200
        },
    ]

    return columns