# Copyright (c) 2013, SERVIO Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import (getdate, flt)
from frappe import _

def execute(filters=None):
    columns, data = [], []
    data = get_data(filters)
    columns = get_columns()
    return columns, data

def get_data(filters):
    result = []

    data = frappe.db.sql("""
    SELECT
        temp.posting_date,
        temp.voucher_type,
        temp.voucher_no,
        temp.party,
        temp.party_name,
        temp.remarks,
        temp.account_number,
        temp.account_name,
        temp.debit,
        temp.credit
    FROM
        (
            SELECT 
                ge.posting_date,
                ge.voucher_type,
                ge.voucher_no,
                pe.party,
                pe.party_name,
                (CASE WHEN UPPER(ge.remarks) = 'NO REMARKS' THEN '' ELSE ge.remarks END) AS remarks,
                a.account_number,
                a.account_name,
                ge.debit,
                ge.credit,
                ge.creation
            FROM 
                `tabGL Entry` ge
            LEFT JOIN
                `tabAccount` a
            ON
                ge.account = a.name
            INNER JOIN
                `tabPayment Entry` pe
            ON
                pe.payment_type = 'Pay'
                and pe.name = ge.voucher_no
                and pe.docstatus in (1, 2)
            WHERE
                ge.docstatus = 1
                and ge.posting_date >= %s
                and ge.posting_date <= %s
                and ge.company = %s
            UNION ALL
            SELECT 
                ge.posting_date,
                ge.voucher_type,
                ge.voucher_no,
                ld.applicant as party,
                c.customer_name as party_name,
                (CASE WHEN UPPER(ge.remarks) = 'NO REMARKS' THEN '' ELSE ge.remarks END) AS remarks,
                a.account_number,
                a.account_name,
                ge.debit,
                ge.credit,
                ge.creation
            FROM 
                `tabGL Entry` ge
            LEFT JOIN
                `tabAccount` a
            ON
                ge.account = a.name
            INNER JOIN
                `tabLoan Disbursement` ld
            ON
                ld.name = ge.voucher_no
                and ld.docstatus in (1, 2)
            LEFT JOIN
                `tabCustomer` c
            ON
                ld.applicant = c.name
            WHERE
                ge.docstatus = 1
                and ge.posting_date >= %s
                and ge.posting_date <= %s
                and ge.company = %s
            UNION ALL            
            SELECT 
                ge.posting_date,
                ge.voucher_type,
                ge.voucher_no,
                pi.supplier as party,
                s.supplier_name as party_name,
                (CASE WHEN UPPER(ge.remarks) = 'NO REMARKS' THEN '' ELSE ge.remarks END) AS remarks,
                a.account_number,
                a.account_name,
                ge.debit,
                ge.credit,
                ge.creation
            FROM 
                `tabGL Entry` ge
            LEFT JOIN
                `tabAccount` a
            ON
                ge.account = a.name
            INNER JOIN
                `tabPurchase Invoice` pi
            ON
                pi.name = ge.voucher_no
                and pi.is_paid = 1
                and pi.docstatus in (1, 2)
            LEFT JOIN
                `tabSupplier` s
            ON
                pi.supplier = s.name
            WHERE
                ge.docstatus = 1
                and ge.posting_date >= %s
                and ge.posting_date <= %s
                and ge.company = %s
        ) temp
    ORDER BY
        temp.posting_date ASC, temp.voucher_no ASC, (CASE WHEN temp.debit > 0 THEN 0 ELSE 1 END) ASC, temp.creation ASC
    """, (getdate(filters.from_date), getdate(filters.to_date), filters.company, 
        getdate(filters.from_date), getdate(filters.to_date), filters.company,
        getdate(filters.from_date), getdate(filters.to_date), filters.company), as_dict=1)
    
    current_voucher_no = ''
    current_voucher_type = ''

    previous_voucher_no = ''
    previous_voucher_type = ''
    subtotal_debit = 0
    subtotal_credit = 0

    data_with_subtotal = []
    
    subtotals = {}
    for row in data:

        current_voucher_no = row.voucher_no
        current_voucher_type = row.voucher_type
        if current_voucher_no == previous_voucher_no and current_voucher_type == previous_voucher_type:
            subtotal_debit = subtotal_debit + row.debit
            subtotal_credit = subtotal_credit + row.credit
        else:
            print("previous_voucher_no: {}".format(previous_voucher_no))
            print("subtotal_debit: {}".format(subtotal_debit))
            print("subtotal_credit: {}".format(subtotal_credit))

            # add subtotal row, reset subtotals
            if previous_voucher_type and previous_voucher_no: # not first row
                data_with_subtotal.append({
                    'posting_date':'',
                    'voucher_type': '',
                    'voucher_no': '',
                    'party': '',
                    'party_name': '',
                    'remarks': '',
                    'account_number': '',
                    'account_name': 'Subtotal',
                    'debit': subtotal_debit,
                    'credit': subtotal_credit,
                    'is_subtotal_row': 1
                })

            subtotal_debit = 0
            subtotal_credit = 0
            subtotal_debit = subtotal_debit + row.debit
            subtotal_credit = subtotal_credit + row.credit
        
        row['is_subtotal_row'] = 0
        data_with_subtotal.append(row)
        
        previous_voucher_no = current_voucher_no
        previous_voucher_type = current_voucher_type
    
    # subtotal for last set
    data_with_subtotal.append({
        'posting_date':'',
        'voucher_type': '',
        'voucher_no': '',
        'party': '',
        'party_name': '',
        'remarks': '',
        'account_number': '',
        'account_name': 'Subtotal',
        'debit': subtotal_debit,
        'credit': subtotal_credit,
        'is_subtotal_row': 1
    })
    
    result.extend(data_with_subtotal)
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
            "width": 180
        },
        {
            "fieldname": "party_name",
            "label": _("Customer"),
            "fieldtype": "Data",
            "width": 180
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