import frappe
from frappe.utils import flt, rounded, getdate
from frappe import _
from erpnext import __version__
import json

@frappe.whitelist()
def get_custom_formatted_address(address):
    result = ""
    if frappe.db.exists("Address", {'name': address}):
        address_doc = frappe.get_doc("Address", address)
        result = address_doc.address_line1 or ''

        if result and address_doc.address_line2:
            result = result + ', ' + address_doc.address_line2
        elif not result and address_doc.address_line2:
            result = address_doc.address_line2
        
        if result and address_doc.city:
            result = result + ', ' + address_doc.city
        elif not result and address_doc.city:
            result = address_doc.city

        if result and address_doc.state:
            result = result + ', ' + address_doc.state
        elif not result and address_doc.state:
            result = address_doc.state
    return result

@frappe.whitelist()
def get_company_information(company):
    company_doc = frappe.get_doc('Company', company)
    company_address = None

    if frappe.db.exists("Dynamic Link", {'link_doctype': 'Company', 'link_name': company, 'parenttype': 'Address'}):
        company_address = frappe.get_last_doc('Dynamic Link', filters={'link_doctype': 'Company', 'link_name': company, 'parenttype': 'Address'})

    company_address = company_address.parent if company_address and company_address.parent else ''
    print("company {} company_address {}".format(company, company_address))
    if company_address:
        company_address = get_custom_formatted_address(company_address)
    
    permit_no = frappe.db.get_single_value('PH Localization Setup', 'permit_no')
    permit_date_issued = frappe.db.get_single_value('PH Localization Setup', 'permit_date_issued')

    result = {
        'address': company_address,
        'tin': company_doc.tax_id,
        'erpnext_version': __version__,
        'permit_no': permit_no if permit_no else '',
        'permit_date_issued': permit_date_issued if permit_date_issued else ''
    }

    return result