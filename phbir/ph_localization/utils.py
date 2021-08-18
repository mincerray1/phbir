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
    company_address = ''
    zipcode = ''
    company_address_dynamic_link_doc = None

    if frappe.db.exists("Dynamic Link", {'link_doctype': 'Company', 'link_name': company, 'parenttype': 'Address'}):
        company_address_dynamic_link_doc = frappe.get_last_doc('Dynamic Link', filters={'link_doctype': 'Company', 'link_name': company, 'parenttype': 'Address'})
    

    if company_address_dynamic_link_doc:
        zipcode = frappe.db.get_value('Address', company_address_dynamic_link_doc.parent, 'pincode')
        zipcode = zipcode if zipcode else ''
        company_address = company_address_dynamic_link_doc.parent if company_address_dynamic_link_doc.parent else ''
    
    if company_address:
        company_address = get_custom_formatted_address(company_address)
    
    permit_no = frappe.db.get_single_value('PH Localization Setup', 'permit_no')
    permit_date_issued = frappe.db.get_single_value('PH Localization Setup', 'permit_date_issued')

    result = {
        'company_name': company_doc.name,
        'address': company_address if company_address else '',
        'tin': preformat_tin(company_doc.tax_id if company_doc.tax_id else ''),
        'zipcode': zipcode,
        'erpnext_version': __version__,
        'permit_no': permit_no if permit_no else '',
        'permit_date_issued': permit_date_issued if permit_date_issued else ''
    }

    return result

@frappe.whitelist()
def get_supplier_information(supplier):
    supplier_doc = frappe.get_doc('Supplier', supplier)
    supplier_address = ''
    zipcode = ''
    supplier_address_dynamic_link_doc = None

    if frappe.db.exists("Dynamic Link", {'link_doctype': 'Supplier', 'link_name': supplier, 'parenttype': 'Address'}):
        supplier_address_dynamic_link_doc = frappe.get_last_doc('Dynamic Link', filters={'link_doctype': 'Supplier', 'link_name': supplier, 'parenttype': 'Address'})
    

    if supplier_address_dynamic_link_doc:
        zipcode = frappe.db.get_value('Address', supplier_address_dynamic_link_doc.parent, 'pincode')
        zipcode = zipcode if zipcode else ''
        supplier_address = supplier_address_dynamic_link_doc.parent if supplier_address_dynamic_link_doc.parent else ''
    
    if supplier_address:
        supplier_address = get_custom_formatted_address(supplier_address)

    result = {
        'supplier_name': supplier_doc.supplier_name,
        'address': supplier_address if supplier_address else '',
        'tin': preformat_tin(supplier_doc.tax_id if supplier_doc.tax_id else ''),
        'zipcode': zipcode
    }

    return result

@frappe.whitelist()
def preformat_tin(tin):
    result = "{0}000000000000".format(tin)
    # tin is 12 digits
    return result[:12]