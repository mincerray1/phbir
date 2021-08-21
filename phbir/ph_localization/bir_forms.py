import frappe
from frappe import _
from frappe.utils.pdf import get_pdf
from frappe.utils import getdate, flt, cint, add_days, add_months, cstr, get_datetime, nowdate, today
from datetime import datetime
from phbir.ph_localization.utils import get_company_information, get_supplier_information
import pytz
import json

options = {
    "margin-left": "0mm",
    "margin-right": "0mm",
    "margin-top": "0mm",
    "margin-bottom": "0mm"
}

@frappe.whitelist()
def bir_2307(company, supplier, purchase_invoice, from_date, to_date, response_type="pdf"):
    frappe.has_permission('BIR 2307', throw=True)

    from phbir.ph_localization.report.bir_2307.bir_2307 import get_data as get_data_bir_2307
    data = get_data_bir_2307(company, supplier, purchase_invoice, from_date, to_date)

    data_ip = []
    data_mp = []

    ip_month_1_total = 0
    ip_month_2_total = 0
    ip_month_3_total = 0
    ip_grand_total = 0
    ip_tax_withheld_for_the_quarter_total = 0

    mp_month_1_total = 0
    mp_month_2_total = 0
    mp_month_3_total = 0
    mp_grand_total = 0
    mp_tax_withheld_for_the_quarter_total = 0

    for entry in data:
        if entry.payment_type == 'Income Payment':
            ip_month_1_total = ip_month_1_total + entry.month_1
            ip_month_2_total = ip_month_2_total + entry.month_2
            ip_month_3_total = ip_month_3_total + entry.month_3
            ip_grand_total = ip_grand_total + entry.total
            ip_tax_withheld_for_the_quarter_total = ip_tax_withheld_for_the_quarter_total + entry.tax_withheld_for_the_quarter

            data_ip.append(entry)
        elif entry.payment_type == 'Money Payment':
            mp_month_1_total = mp_month_1_total + entry.month_1
            mp_month_2_total = mp_month_2_total + entry.month_2
            mp_month_3_total = mp_month_3_total + entry.month_3
            mp_grand_total = mp_grand_total + entry.total
            mp_tax_withheld_for_the_quarter_total = mp_tax_withheld_for_the_quarter_total + entry.tax_withheld_for_the_quarter

            data_mp.append(entry)

    context = {
        'from_date': getdate(from_date),
        'to_date': getdate(to_date),
        'payor': get_company_information(company),
        'payee': get_supplier_information(supplier),
        'data_ip': data_ip,
        'ip_month_1_total': ip_month_1_total,
        'ip_month_2_total': ip_month_2_total,
        'ip_month_3_total': ip_month_3_total,
        'ip_grand_total': ip_grand_total,
        'ip_tax_withheld_for_the_quarter_total': ip_tax_withheld_for_the_quarter_total,
        'data_mp': data_mp,
        'mp_month_1_total': mp_month_1_total,
        'mp_month_2_total': mp_month_2_total,
        'mp_month_3_total': mp_month_3_total,
        'mp_grand_total': mp_grand_total,
        'mp_tax_withheld_for_the_quarter_total': mp_tax_withheld_for_the_quarter_total
    }

    filename = "BIR 2307 {} {} {} {}".format(company, supplier, from_date, to_date)
    
    context["build_version"] = frappe.utils.get_build_version()
    html = frappe.render_template("templates/bir_forms/bir_2307_template.html", context)
    options["page-size"] = "Legal"

    return_pdf_document(html, filename, options, response_type)

@frappe.whitelist()
def bir_2550m(company, year, month, response_type="pdf"):
    precision = cint(frappe.db.get_default("currency_precision")) or 2
    frappe.has_permission('BIR 2550M', throw=True)

    tax_declaration_setup = frappe.get_doc('Tax Declaration Setup', 'Tax Declaration Setup')

    totals = {
        'vat_sales': {
            'total_base_tax_base': 0,
            'total_base_tax_amount': 0
        },
        'sales_to_government': {
            'total_base_tax_base': 0,
            'total_base_tax_amount': 0
        },
        'zero_rated_sales': {
            'total_base_tax_base': 0,
            'total_base_tax_amount': 0
        },
        'exempt_sales': {
            'total_base_tax_base': 0,
            'total_base_tax_amount': 0
        },
        'capital_goods': {
            'total_base_tax_base': 0,
            'total_base_tax_amount': 0
        },
        'capital_goods_exceeding_1m': {
            'total_base_tax_base': 0,
            'total_base_tax_amount': 0
        },
        'domestic_purchases_of_goods': {
            'total_base_tax_base': 0,
            'total_base_tax_amount': 0
        },
        'importation_of_goods': {
            'total_base_tax_base': 0,
            'total_base_tax_amount': 0
        },
        'domestic_purchase_of_services': {
            'total_base_tax_base': 0,
            'total_base_tax_amount': 0
        },
        'services_rendered_by_non_residents': {
            'total_base_tax_base': 0,
            'total_base_tax_amount': 0
        },
        'purchases_not_qualified_for_input_tax': {
            'total_base_tax_base': 0,
            'total_base_tax_amount': 0
        },
        'others': {
            'total_base_tax_base': 0,
            'total_base_tax_amount': 0
        },
        'directly_attributable_to_exempt_sales': {
            'total_base_tax_base': 0,
            'total_base_tax_amount': 0
        },
        'directly_attributable_to_sale_to_government': {
            'total_base_tax_base': 0,
            'total_base_tax_amount': 0
        }
    }

    pi_base_net_amounts = frappe.db.sql("""
        SELECT 
            pi.name, pii.item_code, pii.item_tax_template, pi.taxes_and_charges, SUM(base_net_amount) AS base_net_amount 
        FROM
            `tabPurchase Invoice Item` pii
        LEFT JOIN
            `tabPurchase Invoice` pi
        ON
            pii.parent = pi.name
        WHERE
            pi.company = %s
            AND pi.docstatus = 1
            AND YEAR(pi.posting_date) = %s
            AND MONTH(pi.posting_date) = %s
        GROUP BY pi.name, item_code, pii.item_tax_template, pi.taxes_and_charges;
        """, (company, year, month), as_dict=1)

    pi_base_tax_amounts = frappe.db.sql("""
        SELECT
            pi.name,
            ptac.base_tax_amount,
            ptac.item_wise_tax_detail
        FROM
            `tabPurchase Invoice` pi
        INNER JOIN
            `tabPurchase Taxes and Charges` ptac
        ON
            pi.name = ptac.parent
        WHERE
            pi.company = %s
            AND pi.docstatus = 1
            AND ptac.base_tax_amount >= 0
            AND YEAR(pi.posting_date) = %s
            AND MONTH(pi.posting_date) = %s
        """, (company, year, month), as_dict=1)
    
    si_base_net_amounts = frappe.db.sql("""
        SELECT 
            si.name, sii.item_code, sii.item_tax_template, si.taxes_and_charges, SUM(base_net_amount) AS base_net_amount 
        FROM
            `tabSales Invoice Item` sii
        LEFT JOIN
            `tabSales Invoice` si
        ON
            sii.parent = si.name
        WHERE
            si.company = %s
            AND si.docstatus = 1
            AND YEAR(si.posting_date) = %s
            AND MONTH(si.posting_date) = %s
        GROUP BY si.name, item_code, sii.item_tax_template, si.taxes_and_charges;
        """, (company, year, month), as_dict=1)

    si_base_tax_amounts = frappe.db.sql("""
        SELECT
            si.name,
            stac.base_tax_amount,
            stac.item_wise_tax_detail
        FROM
            `tabSales Invoice` si
        INNER JOIN
            `tabSales Taxes and Charges` stac
        ON
            si.name = stac.parent
        WHERE
            si.company = %s
            AND si.docstatus = 1
            AND stac.base_tax_amount >= 0
            AND YEAR(si.posting_date) = %s
            AND MONTH(si.posting_date) = %s
        """, (company, year, month), as_dict=1)
    
    # item_wise_tax_detail looks like {"FF01":[5.0,599.0506],"1234":[12.0,146.20896],"Item 8":[12.0,60.006594]} 
    for tax_line in pi_base_tax_amounts:
        item_wise_tax_detail = json.loads(tax_line.item_wise_tax_detail)
        for item in item_wise_tax_detail.keys():
            # loop to find net amount
            for item_net_amount in pi_base_net_amounts:                
                if item_net_amount.name == tax_line.name and item_net_amount.item_code == item:
                    item_tax_template = item_net_amount.item_tax_template
                    taxes_and_charges = item_net_amount.taxes_and_charges
                    
                    if tax_declaration_setup.item_capital_goods and item_tax_template == tax_declaration_setup.item_capital_goods:
                        totals['capital_goods']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['capital_goods']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                    elif tax_declaration_setup.capital_goods and taxes_and_charges == tax_declaration_setup.capital_goods:
                        totals['capital_goods']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['capital_goods']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                        
                    elif tax_declaration_setup.item_domestic_purchases_of_goods and item_tax_template == tax_declaration_setup.item_domestic_purchases_of_goods:
                        totals['domestic_purchases_of_goods']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['domestic_purchases_of_goods']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                    elif tax_declaration_setup.domestic_purchases_of_goods and taxes_and_charges == tax_declaration_setup.domestic_purchases_of_goods:
                        totals['domestic_purchases_of_goods']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['domestic_purchases_of_goods']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                        
                    elif tax_declaration_setup.item_importation_of_goods and item_tax_template == tax_declaration_setup.item_importation_of_goods:
                        totals['importation_of_goods']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['importation_of_goods']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                    elif tax_declaration_setup.importation_of_goods and taxes_and_charges == tax_declaration_setup.importation_of_goods:
                        totals['importation_of_goods']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['importation_of_goods']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                        
                    elif tax_declaration_setup.item_domestic_purchase_of_services and item_tax_template == tax_declaration_setup.item_domestic_purchase_of_services:
                        totals['domestic_purchase_of_services']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['domestic_purchase_of_services']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                    elif tax_declaration_setup.domestic_purchase_of_services and taxes_and_charges == tax_declaration_setup.domestic_purchase_of_services:
                        totals['domestic_purchase_of_services']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['domestic_purchase_of_services']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                        
                    elif tax_declaration_setup.item_services_rendered_by_non_residents and item_tax_template == tax_declaration_setup.item_services_rendered_by_non_residents:
                        totals['services_rendered_by_non_residents']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['services_rendered_by_non_residents']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                    elif tax_declaration_setup.services_rendered_by_non_residents and taxes_and_charges == tax_declaration_setup.services_rendered_by_non_residents:
                        totals['services_rendered_by_non_residents']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['services_rendered_by_non_residents']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                        
                    # not qualified for input tax (zero rated and exempt)
                    elif tax_declaration_setup.item_zero_rated_purchase and item_tax_template == tax_declaration_setup.item_zero_rated_purchase:
                        totals['purchases_not_qualified_for_input_tax']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['purchases_not_qualified_for_input_tax']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                    elif tax_declaration_setup.zero_rated_purchase and taxes_and_charges == tax_declaration_setup.zero_rated_purchase:
                        totals['purchases_not_qualified_for_input_tax']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['purchases_not_qualified_for_input_tax']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                        
                    elif tax_declaration_setup.item_exempt_purchase and item_tax_template == tax_declaration_setup.item_exempt_purchase:
                        totals['purchases_not_qualified_for_input_tax']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['purchases_not_qualified_for_input_tax']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                    elif tax_declaration_setup.exempt_purchase and taxes_and_charges == tax_declaration_setup.exempt_purchase:
                        totals['purchases_not_qualified_for_input_tax']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['purchases_not_qualified_for_input_tax']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                    # end - not qualified for input tax 
                        
                    elif tax_declaration_setup.item_others and item_tax_template == tax_declaration_setup.item_others:
                        totals['others']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['others']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                    elif tax_declaration_setup.others and taxes_and_charges == tax_declaration_setup.others:
                        totals['others']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['others']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                    
                    # others special handling, blank tax templates go to others
                    else:
                        totals['others']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['others']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                    
                    # TODO: exempt / government
                    # elif tax_declaration_setup.item_directly_attributable_to_exempt_sales and item_tax_template == tax_declaration_setup.item_directly_attributable_to_exempt_sales:
                    #     totals['directly_attributable_to_exempt_sales']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                    #     totals['directly_attributable_to_exempt_sales']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                    # elif tax_declaration_setup.directly_attributable_to_exempt_sales and taxes_and_charges == tax_declaration_setup.directly_attributable_to_exempt_sales:
                    #     totals['directly_attributable_to_exempt_sales']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                    #     totals['directly_attributable_to_exempt_sales']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                        
                    # elif tax_declaration_setup.item_directly_attributable_to_sale_to_government and item_tax_template == tax_declaration_setup.item_directly_attributable_to_sale_to_government:
                    #     totals['directly_attributable_to_sale_to_government']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                    #     totals['directly_attributable_to_sale_to_government']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                    # elif tax_declaration_setup.directly_attributable_to_sale_to_government and taxes_and_charges == tax_declaration_setup.directly_attributable_to_sale_to_government:
                    #     totals['directly_attributable_to_sale_to_government']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                    #     totals['directly_attributable_to_sale_to_government']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)

                    # net amount row is found, exit loop
                    break

    # capital goods base exceeds 1m, move amounts
    if totals['capital_goods']['total_base_tax_base'] > 1000000:
        totals['capital_goods_exceeding_1m']['total_base_tax_base'] = totals['capital_goods']['total_base_tax_base']
        totals['capital_goods_exceeding_1m']['total_base_tax_amount'] = totals['capital_goods']['total_base_tax_amount']

        totals['capital_goods']['total_base_tax_base'] = 0
        totals['capital_goods']['total_base_tax_amount'] = 0

    for tax_line in si_base_tax_amounts:
        item_wise_tax_detail = json.loads(tax_line.item_wise_tax_detail)
        for item in item_wise_tax_detail.keys():
            # loop to find net amount
            for item_net_amount in si_base_net_amounts:                
                if item_net_amount.name == tax_line.name and item_net_amount.item_code == item:
                    item_tax_template = item_net_amount.item_tax_template
                    taxes_and_charges = item_net_amount.taxes_and_charges

                    if tax_declaration_setup.item_vat_sales and item_tax_template == tax_declaration_setup.item_vat_sales:
                        totals['vat_sales']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['vat_sales']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                    elif tax_declaration_setup.vat_sales and taxes_and_charges == tax_declaration_setup.vat_sales:
                        totals['vat_sales']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['vat_sales']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                        
                    if tax_declaration_setup.item_sales_to_government and item_tax_template == tax_declaration_setup.item_sales_to_government:
                        totals['sales_to_government']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['sales_to_government']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                    elif tax_declaration_setup.sales_to_government and taxes_and_charges == tax_declaration_setup.sales_to_government:
                        totals['sales_to_government']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['sales_to_government']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                        
                    if tax_declaration_setup.item_zero_rated_sales and item_tax_template == tax_declaration_setup.item_zero_rated_sales:
                        totals['zero_rated_sales']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['zero_rated_sales']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                    elif tax_declaration_setup.zero_rated_sales and taxes_and_charges == tax_declaration_setup.zero_rated_sales:
                        totals['zero_rated_sales']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['zero_rated_sales']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                        
                    if tax_declaration_setup.item_exempt_sales and item_tax_template == tax_declaration_setup.item_exempt_sales:
                        totals['exempt_sales']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['exempt_sales']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)
                    elif tax_declaration_setup.exempt_sales and taxes_and_charges == tax_declaration_setup.exempt_sales:
                        totals['exempt_sales']['total_base_tax_base'] += flt(item_net_amount.base_net_amount, 2)
                        totals['exempt_sales']['total_base_tax_amount'] += flt(item_wise_tax_detail[item][1], 2)

                    # net amount row is found, exit loop
                    break


    context = {
        'company': get_company_information(company),
        'year': year,
        'month': month,
        'totals': totals
    }

    filename = "BIR 2550M {} {} {}".format(company, year, month)
    
    context["build_version"] = frappe.utils.get_build_version()
    html = frappe.render_template("templates/bir_forms/bir_2550m_template.html", context)
    options["page-size"] = "Legal"

    return_pdf_document(html, filename, options, response_type)

@frappe.whitelist()
def bir_1601_eq(company, year, quarter, response_type="pdf"):
    precision = cint(frappe.db.get_default("currency_precision")) or 2
    frappe.has_permission('BIR 1601-EQ', throw=True)

    year = int(year)
    quarter = int(quarter)
    total_remittances_made = 0
    total_taxes_withheld = 0
    tax_still_due = 0
    total_penalties = 0
    total_amount_still_due = 0

    # TODO: custom base amount
    data = frappe.db.sql("""
        SELECT 
            temp.atc,
            temp.base_tax_base,
            a.rate AS tax_rate,
            temp.base_tax_withheld
        FROM
            (
            SELECT 
                ptac.atc AS atc,
                SUM(pi.base_total) AS base_tax_base,
                SUM(ABS(ptac.base_tax_amount)) AS base_tax_withheld
            FROM 
                `tabPurchase Invoice` pi
            LEFT JOIN
                `tabPurchase Taxes and Charges` ptac
            ON
                pi.name = ptac.parent
            WHERE
                pi.docstatus = 1
                and pi.is_return = 0
                and (ptac.base_tax_amount < 0 or ptac.add_deduct_tax = 'Deduct')
                and pi.company = %s
                and YEAR(pi.posting_date) = %s
                and QUARTER(pi.posting_date) = %s
            GROUP BY
                ptac.atc
            ) AS temp
        INNER JOIN 
            `tabATC` as a
        ON
            temp.atc = a.name
        WHERE
            a.tax_type_code IN ('WE', 'WB', 'WV')
        """, (company, year, quarter), as_dict=1)

    for entry in data:
        total_taxes_withheld += entry.base_tax_withheld
    
    tax_still_due = total_taxes_withheld - total_remittances_made
    total_amount_still_due = tax_still_due + total_penalties

    context = {
        'company': get_company_information(company),
        'year': year,
        'quarter': quarter,
        'data': data,
        'total_taxes_withheld': total_taxes_withheld,
        'total_remittances_made': total_remittances_made,
        'tax_still_due': tax_still_due,
        'total_penalties': total_penalties,
        'total_amount_still_due': total_amount_still_due
    }

    filename = "BIR 1601-EQ {} {} {}".format(company, year, quarter)
    
    context["build_version"] = frappe.utils.get_build_version()
    html = frappe.render_template("templates/bir_forms/bir_1601_eq_template.html", context)
    options["page-size"] = "Legal"

    return_pdf_document(html, filename, options, response_type)

@frappe.whitelist()
def bir_1601_eq_qap(company, year, quarter, response_type="download"):
    precision = cint(frappe.db.get_default("currency_precision")) or 2
    frappe.has_permission('BIR 1601-EQ', throw=True)

    year = int(year)
    quarter = int(quarter)
    total_remittances_made = 0
    total_taxes_withheld = 0
    tax_still_due = 0
    total_penalties = 0
    total_amount_still_due = 0

    # TODO: custom base amount
    data = frappe.db.sql("""
        SELECT 
            temp.atc,
            temp.base_tax_base,
            a.rate AS tax_rate,
            temp.base_tax_withheld
        FROM
            (
            SELECT 
                ptac.atc AS atc,
                SUM(pi.base_total) AS base_tax_base,
                SUM(ABS(ptac.base_tax_amount)) AS base_tax_withheld
            FROM 
                `tabPurchase Invoice` pi
            LEFT JOIN
                `tabPurchase Taxes and Charges` ptac
            ON
                pi.name = ptac.parent
            WHERE
                pi.docstatus = 1
                and pi.is_return = 0
                and (ptac.base_tax_amount < 0 or ptac.add_deduct_tax = 'Deduct')
                and pi.company = %s
                and YEAR(pi.posting_date) = %s
                and QUARTER(pi.posting_date) = %s
            GROUP BY
                ptac.atc
            ) AS temp
        INNER JOIN 
            `tabATC` as a
        ON
            temp.atc = a.name
        WHERE
            a.tax_type_code IN ('WE', 'WB', 'WV')
        """, (company, year, quarter), as_dict=1)

    for entry in data:
        total_taxes_withheld += entry.base_tax_withheld
    
    tax_still_due = total_taxes_withheld - total_remittances_made
    total_amount_still_due = tax_still_due + total_penalties

    context = {
        'company': get_company_information(company),
        'year': year,
        'quarter': quarter,
        'data': data,
        'total_taxes_withheld': total_taxes_withheld,
        'total_remittances_made': total_remittances_made,
        'tax_still_due': tax_still_due,
        'total_penalties': total_penalties,
        'total_amount_still_due': total_amount_still_due
    }

    filename = "BIR 1601-EQ {} {} {}".format(company, year, quarter)
    file_extension = "dat"
    
    context["build_version"] = frappe.utils.get_build_version()
    content = 'hellow'

    return_document(content, filename, file_extension, response_type)

@frappe.whitelist()
def bir_1601_fq(company, year, quarter, response_type="pdf"):
    precision = cint(frappe.db.get_default("currency_precision")) or 2
    frappe.has_permission('BIR 1601-FQ', throw=True)

    tax_declaration_setup = frappe.get_doc('Tax Declaration Setup', 'Tax Declaration Setup')

    context = {
        'company': get_company_information(company),
        'year': year,
        'quarter': quarter
    }

    filename = "BIR 1601-EQ {} {} {}".format(company, year, quarter)
    
    context["build_version"] = frappe.utils.get_build_version()
    html = frappe.render_template("templates/bir_forms/bir_1601_fq_template.html", context)
    options["page-size"] = "Legal"

    return_pdf_document(html, filename, options, response_type)

@frappe.whitelist()
def return_pdf_document(html, filename="document", options=options, response_type="download"):
    frappe.local.response.filename = "{filename}.pdf".format(filename=filename)
    frappe.local.response.filecontent = get_pdf(html, options)
    frappe.local.response.type = response_type

@frappe.whitelist()
def return_document(content, filename, file_extension, response_type="download"):
    frappe.local.response.filename = "{filename}.{file_extension}".format(filename=filename, file_extension=file_extension)
    frappe.local.response.filecontent = content
    frappe.local.response.type = response_type

def make_ordinal(n):
    '''
    Convert an integer into its ordinal representation::

        make_ordinal(0)   => '0th'
        make_ordinal(3)   => '3rd'
        make_ordinal(122) => '122nd'
        make_ordinal(213) => '213th'
    '''
    n = int(n)
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return str(n) + suffix