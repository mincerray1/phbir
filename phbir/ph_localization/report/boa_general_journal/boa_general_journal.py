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
    result = frappe.db.sql("""
    SELECT 
        ge.posting_date,
        ge.voucher_type,
        ge.voucher_no,
        (CASE WHEN UPPER(ge.remarks) = 'NO REMARKS' THEN '' ELSE ge.remarks END) AS remarks,
        a.account_number,
        a.account_name,
        ge.debit,
        ge.credit
    FROM 
        `tabGL Entry` ge
    LEFT JOIN
        `tabAccount` a
    ON
        ge.account = a.name
    WHERE
        ge.docstatus = 1
        and ge.posting_date >= %s
        and ge.posting_date <= %s
        and ge.company = %s
    ORDER BY
        ge.posting_date ASC, ge.voucher_no, (CASE WHEN ge.debit > 0 THEN 0 ELSE 1 END) ASC
    """, (getdate(filters.from_date), getdate(filters.to_date), filters.company), as_dict=1)

    return result

def get_columns():
    columns = [
        {
            "fieldname": "posting_date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 120
        },
        {
            "fieldname": "voucher_type",
            "label": _("Reference Type"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "voucher_no",
            "label": _("Reference"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "remarks",
            "label": _("Brief Description/Explanation"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "account_number",
            "label": _("Account Code"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "account_name",
            "label": _("Account Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "debit",
            "label": _("Debit"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "credit",
            "label": _("Credit"),
            "fieldtype": "Currency",
            "width": 150
        },
    ]

    return columns