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
    data = [
        {
            'bir_1601_fq': '✓'
        }
    ]

    return data

def get_columns():
    columns = [
        {
            "fieldname": "bir_1601_fq",
            "label": _("BIR 1601-FQ"),
            "fieldtype": "Data",
            "width": 120
        }
    ]

    return columns