# Copyright (c) 2013, SERVIO Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import (getdate)
from frappe import _

def execute(filters=None):
    columns, data = [], []
    data = get_data(filters.company, filters.supplier, filters.doctype, filters.purchase_invoice, filters.payment_entry, filters.from_date, filters.to_date)
    columns = get_columns()
    return columns, data

# works on net total only
# TODO: custom tax base
def get_data(company, supplier, doctype, purchase_invoice, payment_entry, from_date, to_date):
    result = []
    data_pi = []
    data_pe = []
    pi_condition = ''
    pe_condition = ''
    
    if doctype == "Purchase Invoice" and purchase_invoice:
        pi_condition += ' AND pi.name = %s' % frappe.db.escape(purchase_invoice)

    if doctype == "Payment Entry" and payment_entry:
        pe_condition += ' AND pe.name = %s' % frappe.db.escape(payment_entry)


    if not payment_entry:
        data_pi = frappe.db.sql("""
            SELECT 
                (CASE 
                    WHEN ptac.atc IN (SELECT atc FROM `tabATC` WHERE LEFT(atc, 2) IN ('WI', 'WC')) 
                        THEN 'Income Payment' 
                    WHEN ptac.atc IN (SELECT atc FROM `tabATC` WHERE LEFT(atc, 2) IN ('WB', 'WV'))  
                        THEN 'Money Payment' 
                END) AS payment_type,
                ptac.atc AS atc,
                pi.name AS document_no,
                (CASE WHEN MONTH(pi.posting_date) IN (1, 4, 7, 10) THEN pi.base_total ELSE 0 END) AS month_1,
                (CASE WHEN MONTH(pi.posting_date) IN (2, 5, 8, 11) THEN pi.base_total ELSE 0 END) AS month_2,
                (CASE WHEN MONTH(pi.posting_date) IN (3, 6, 9, 12) THEN pi.base_total ELSE 0 END) AS month_3,
                pi.base_total AS total,
                ABS(ptac.base_tax_amount) AS tax_withheld_for_the_quarter
            FROM 
                `tabPurchase Invoice` pi
            LEFT JOIN
                `tabPurchase Taxes and Charges` ptac
            ON
                pi.name = ptac.parent
            LEFT JOIN 
                `tabSupplier` as s
            ON
                pi.supplier = s.name
            WHERE
                pi.docstatus = 1
                and pi.is_return = 0
                and ((ptac.base_tax_amount < 0 and ptac.add_deduct_tax != 'Deduct') or (ptac.base_tax_amount >= 0 and ptac.add_deduct_tax = 'Deduct'))
                and ptac.atc IN (SELECT atc FROM `tabATC` WHERE tax_type_code IN ('WE', 'WB', 'WV'))
                and pi.supplier = %s
                and pi.posting_date >= %s
                and pi.posting_date <= %s
                and pi.company = %s {0}
            """.format(pi_condition), (supplier, getdate(from_date), getdate(to_date), company), as_dict=1)
    
        result.extend(data_pi)
    
    if not purchase_invoice:
        data_pe = frappe.db.sql("""
            SELECT 
                (CASE 
                    WHEN atac.atc IN (SELECT atc FROM `tabATC` WHERE LEFT(atc, 2) IN ('WI', 'WC')) 
                        THEN 'Income Payment' 
                    WHEN atac.atc IN (SELECT atc FROM `tabATC` WHERE LEFT(atc, 2) IN ('WB', 'WV'))  
                        THEN 'Money Payment' 
                END) AS payment_type,
                atac.atc AS atc,
                pe.name AS document_no,
                (CASE WHEN MONTH(pe.posting_date) IN (1, 4, 7, 10) THEN pe.base_paid_amount ELSE 0 END) AS month_1,
                (CASE WHEN MONTH(pe.posting_date) IN (2, 5, 8, 11) THEN pe.base_paid_amount ELSE 0 END) AS month_2,
                (CASE WHEN MONTH(pe.posting_date) IN (3, 6, 9, 12) THEN pe.base_paid_amount ELSE 0 END) AS month_3,
                pe.base_paid_amount AS total,
                ABS(atac.base_tax_amount) AS tax_withheld_for_the_quarter
            FROM 
                `tabPayment Entry` pe
            LEFT JOIN
                `tabAdvance Taxes and Charges` atac
            ON
                pe.name = atac.parent
            LEFT JOIN 
                `tabSupplier` as s
            ON
                pe.party = s.name
            WHERE
                pe.docstatus = 1
                and pe.payment_type = 'Pay'
                and pe.party_type = 'Supplier'
                and ((atac.base_tax_amount < 0 and atac.add_deduct_tax != 'Deduct') or (atac.base_tax_amount >= 0 and atac.add_deduct_tax = 'Deduct'))
                and atac.atc IN (SELECT atc FROM `tabATC` WHERE tax_type_code IN ('WE', 'WB', 'WV'))
                and pe.party = %s
                and pe.posting_date >= %s
                and pe.posting_date <= %s
                and pe.company = %s {0}
            """.format(pe_condition), (supplier, getdate(from_date), getdate(to_date), company), as_dict=1)
    
        result.extend(data_pe)

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
            "fieldname": "document_no",
            "label": _("Document No"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "month_1",
            "label": _("1st Month"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "month_2",
            "label": _("2nd Month"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "month_3",
            "label": _("3rd Month"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "total",
            "label": _("Total"),
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