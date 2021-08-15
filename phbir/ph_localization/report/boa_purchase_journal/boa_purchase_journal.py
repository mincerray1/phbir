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
        pi.posting_date, 
        pi.tax_id,
        pi.supplier,
        s.supplier_name,
        /* pi.supplier_address, */
        pi.name,
        pi.currency,
        pi.is_return,
        pi.bill_no,
        pi.total,
        (pi.total - pi.net_total) as net_discount,
        pi.taxes_and_charges_added as tax_amount,
        pi.taxes_and_charges_deducted as withholding_tax_amount,
        pi.grand_total
    FROM
        `tabPurchase Invoice` pi
    LEFT JOIN
        `tabSupplier` s
    ON 
        pi.supplier = s.name
    WHERE
        pi.docstatus = 1
        and pi.is_return = 0
        and pi.posting_date >= %s
        and pi.posting_date <= %s
        and pi.company = %s
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
        # {
        #     "fieldname": "supplier",
        #     "label": _("Supplier Code"),
        #     "fieldtype": "Link",
        #     "options": "Supplier",
        #     "width": 150
        # },
        {
            "fieldname": "supplier_name",
            "label": _("Supplier Name"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "name",
            "label": _("Document No"),
            "fieldtype": "Link",
            "options": "Purchase Invoice",
            "width": 150
        },
        # {
        #     "fieldname": "is_return",
        #     "label": _("Return"),
        #     "fieldtype": "Check",
        #     "width": 10
        # },
        {
            "fieldname": "bill_no",
            "label": _("Supplier Invoice No"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "total",
            "label": _("Amount"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "net_discount",
            "label": _("Discount"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "tax_amount",
            "label": _("VAT"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "withholding_tax_amount",
            "label": _("Withholding Tax"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "grand_total",
            "label": _("NET Purchases"),
            "fieldtype": "Currency",
            "width": 150
        }
    ]

    return columns