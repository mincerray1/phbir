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
        si.posting_date, 
        (CASE WHEN IFNULL(si.tax_id, '') = '' THEN c.tax_id ELSE si.tax_id END) AS tax_id,
        si.customer,
        c.customer_name,
        /* si.customer_address, */
        si.name,
        si.currency,
        si.is_return,
        si.po_no,
        si.total,
        (si.total - si.net_total) as net_discount,
        IFNULL(stac_add.tax_amount, 0) as tax_amount,
        ABS(IFNULL(stac_deduct.tax_amount, 0)) as withholding_tax_amount,
        si.grand_total
    FROM
        `tabSales Invoice` si
    LEFT JOIN
        `tabCustomer` c
    ON 
        si.customer = c.name
    LEFT JOIN
        (
            SELECT stac.parent, SUM(stac.tax_amount) AS tax_amount, SUM(stac.base_tax_amount) AS base_tax_amount, 
                SUM(stac.tax_amount_after_discount_amount) AS tax_amount_after_discount_amount, SUM(stac.base_tax_amount_after_discount_amount) AS base_tax_amount_after_discount_amount
            FROM `tabSales Taxes and Charges` stac
            WHERE stac.tax_amount >= 0
            GROUP BY stac.parent
        ) stac_add
    ON
        si.name = stac_add.parent
    LEFT JOIN
        (
            SELECT stac.parent, SUM(stac.tax_amount) AS tax_amount, SUM(stac.base_tax_amount) AS base_tax_amount, 
                SUM(stac.tax_amount_after_discount_amount) AS tax_amount_after_discount_amount, SUM(stac.base_tax_amount_after_discount_amount) AS base_tax_amount_after_discount_amount
            FROM `tabSales Taxes and Charges` stac
            WHERE stac.tax_amount < 0
            GROUP BY stac.parent
        ) stac_deduct
    ON
        si.name = stac_deduct.parent
    WHERE
        si.docstatus = 1
        and si.is_return = 0
        and si.posting_date >= %s
        and si.posting_date <= %s
        and si.company = %s
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
        #     "fieldname": "customer",
        #     "label": _("Customer Code"),
        #     "fieldtype": "Link",
        #     "options": "Customer",
        #     "width": 150
        # },
        {
            "fieldname": "customer_name",
            "label": _("Customer Name"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "tax_id",
            "label": _("TIN"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "name",
            "label": _("Document No"),
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 150
        },
        # {
        #     "fieldname": "is_return",
        #     "label": _("Return"),
        #     "fieldtype": "Check",
        #     "width": 10
        # },
        {
            "fieldname": "po_no",
            "label": _("Customer PO No"),
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
            "label": _("Net Sales"),
            "fieldtype": "Currency",
            "width": 150
        }
    ]

    return columns