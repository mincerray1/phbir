# Copyright (c) 2013, SERVIO Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
from phbir.ph_localization.utils import get_company_information, get_customer_information

def execute(filters=None):
    columns, data = [], []

    data = get_data(filters.company, filters.year, filters.month)
    columns = get_columns()

    company_information = get_company_information(filters.company)

    return columns, data, None, None, company_information

def get_data(company, year, month):
    result = []

    data = frappe.db.sql("""
        SELECT 
            temp.customer,
            temp.atc,
            temp.income_payment,
            temp.atc_rate,
            temp.tax_withheld
        FROM
            (
            SELECT 
                si.company,
                si.posting_date,
                si.customer,
                stac.atc AS atc,
                si.name AS document_no,
                si.base_total as income_payment,
                stac.atc_rate,
                ABS(stac.base_tax_amount) as tax_withheld
            FROM 
                `tabSales Invoice` si
            LEFT JOIN
                `tabSales Taxes and Charges` stac
            ON
                si.name = stac.parent
            LEFT JOIN 
                `tabCustomer` as c
            ON
                si.customer = c.name
            WHERE
                si.docstatus = 1
                and si.is_return = 0
                and stac.base_tax_amount < 0 
                and stac.atc IN (SELECT atc FROM `tabATC` WHERE tax_type_code IN ('WE', 'WB', 'WV'))
            UNION ALL
            SELECT 
                pe.company,
                pe.posting_date,
                pe.party,
                atac.atc AS atc,
                pe.name AS document_no,
                pe.paid_amount as income_payment,
                atac.atc_rate,
                ABS(atac.base_tax_amount) as tax_withheld
            FROM 
                `tabPayment Entry` pe
            LEFT JOIN
                `tabAdvance Taxes and Charges` atac
            ON
                pe.name = atac.parent
            LEFT JOIN 
                `tabCustomer` as c
            ON
                pe.party = c.name
            WHERE
                pe.docstatus = 1
                and ((atac.base_tax_amount < 0 and atac.add_deduct_tax != 'Deduct') or (atac.base_tax_amount >= 0 and atac.add_deduct_tax = 'Deduct'))
                and atac.atc IN (SELECT atc FROM `tabATC` WHERE tax_type_code IN ('WE', 'WB', 'WV'))
                and pe.party_type = 'Customer'
            ) temp
        WHERE 
            temp.company = %s
            and YEAR(temp.posting_date) = %s
            and MONTH(temp.posting_date) = %s
        GROUP BY
            temp.customer,
            temp.atc,
            temp.atc_rate
    """, (company, year, month), as_dict=1)

    for entry in data:
        customer_information = get_customer_information(entry.customer)

        row = {
            'tin': customer_information['tin_with_dash'],
            'registered_name': '' if customer_information['customer_type'] == 'Individual' else entry.customer,
            'individual': '' if customer_information['customer_type'] == 'Company' 
                else "{0}, {1} {2}".format(customer_information['contact_last_name'], customer_information['contact_first_name'], customer_information['contact_middle_name']),
            'atc': entry.atc,
            'income_payment': entry.income_payment,
            'atc_rate': "{:.0%}".format(entry.atc_rate / 100),
            'tax_withheld': entry.tax_withheld
        }

        result.append(row)
    
    return result

def get_columns():
    columns = [
        {
            "fieldname": "tin",
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
            "fieldname": "atc_rate",
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