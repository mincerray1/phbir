# Copyright (c) 2013, SERVIO Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import (getdate)
from frappe import _

def execute(filters=None):
    columns, data = [], []
    data = get_data(filters)
    columns = get_columns()
    return columns, data

def get_data(filters):
    result = [{
        'payment_type': 'Income Payment',
        'atc': 'WC158',
        'month_1': 10000,
        'month_2': 20000,
        'month_3': 30000,
        'total': 60000,
        'tax_withheld_for_the_quarter': 60
    }]
    return result

def get_columns():
    columns = [
        {
            "fieldname": "payment_type",
            "label": _("Type"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "atc",
            "label": _("ATC"),
            "fieldtype": "Link",
            "options": "ATC",
            "width": 60
        },
        {
            "fieldname": "month_1",
            "label": _("1st Month"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "month_2",
            "label": _("Amount"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "month_3",
            "label": _("Amount"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "total",
            "label": _("Amount"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "tax_withheld_for_the_quarter",
            "label": _("Tax Withheld"),
            "fieldtype": "Currency",
            "width": 150
        }
    ]

    return columns