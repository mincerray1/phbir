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

@frappe.whitelist()
def get_years():
    result = []
    q = frappe.db.sql("""
        SELECT 
            year(min(year_start_date)) as min_year, 
            year(max(year_end_date)) as max_year 
        FROM 
            `tabFiscal Year`;
        """, (), as_dict=1)

    if q[0]:
        start = q[0].min_year
        end = q[0].max_year + 1

        for x in range(start, end):
            result.append(x)
    
    return result

#### migrate methods, move out as needed
@frappe.whitelist()
def generate_tax_templates():
    n = 0

    sales_tax_templates = {
        'VAT Sales':'',
        'Sales to Government':'',
        'Zero Rated Sales':'',
        'Exempt Sales':''
    }

    item_sales_tax_templates = {
        'VAT Sales':'',
        'Sales to Government':'',
        'Zero Rated Sales':'',
        'Exempt Sales':''
    }

    purchase_tax_templates = {
        'Capital Goods':'',
        'Capital Goods Exceeding 1M':'',
        'Domestic Purchases of Goods':'',
        'Importation of Goods':'',
        'Domestic Purchase of Services':'',
        'Services Rendered by Non-residents':'',
        'Purchases Not Qualified for Input Tax':'',
        'Others':'',
        'Allocable to Exempt Sales':''
    }

    item_purchase_tax_templates = {
        'Capital Goods':'',
        'Capital Goods Exceeding 1M':'',
        'Domestic Purchases of Goods':'',
        'Importation of Goods':'',
        'Domestic Purchase of Services':'',
        'Services Rendered by Non-residents':'',
        'Purchases Not Qualified for Input Tax':'',
        'Others':'',
        'Allocable to Exempt Sales':''
    }

    company = frappe.db.get_default("Company")

    for t in sales_tax_templates:
        if not frappe.db.exists('Sales Taxes and Charges Template', {'company': company, 'title': t}):
            stac = frappe.get_doc({
                'doctype': 'Sales Taxes and Charges Template',
                'title': t,
                'company': company
            })
            stac.insert()
            sales_tax_templates[t] = stac.name
            n += 1
        else:
            sales_tax_templates[t] = frappe.get_value('Sales Taxes and Charges Template', {'company': company, 'title': t}, 'name')

    for t in item_sales_tax_templates:
        if not frappe.db.exists('Item Tax Template', {'company': company, 'title': t}):
            itt = frappe.get_doc({
                'doctype': 'Item Tax Template',
                'title': t,
                'company': company
            })

            itt.flags.ignore_mandatory = True
            itt.insert()
            item_sales_tax_templates[t] = itt.name
            n += 1
        else:
            item_sales_tax_templates[t] = frappe.get_value('Item Tax Template', {'company': company, 'title': t}, 'name')

    for t in purchase_tax_templates:
        if not frappe.db.exists('Purchase Taxes and Charges Template', {'company': company, 'title': t}):
            ptac = frappe.get_doc({
                'doctype': 'Purchase Taxes and Charges Template',
                'title': t,
                'company': company
            })
            ptac.insert()
            purchase_tax_templates[t] = ptac.name
            n += 1
        else:
            purchase_tax_templates[t] = frappe.get_value('Purchase Taxes and Charges Template', {'company': company, 'title': t}, 'name')

    for t in item_purchase_tax_templates:
        if not frappe.db.exists('Item Tax Template', {'company': company, 'title': t}):
            itt = frappe.get_doc({
                'doctype': 'Item Tax Template',
                'title': t,
                'company': company
            })

            itt.flags.ignore_mandatory = True
            itt.insert()
            item_purchase_tax_templates[t] = itt.name
            n += 1
        else:
            item_purchase_tax_templates[t] = frappe.get_value('Item Tax Template', {'company': company, 'title': t}, 'name')
    
    tax_declaration_setup = frappe.get_doc('Tax Declaration Setup', 'Tax Declaration Setup')
    
    tax_declaration_setup.vat_sales = sales_tax_templates['VAT Sales']
    tax_declaration_setup.sales_to_government = tax_declaration_setup.sales_to_government or sales_tax_templates['Sales to Government']
    tax_declaration_setup.zero_rated_sales = tax_declaration_setup.zero_rated_sales or sales_tax_templates['Zero Rated Sales']
    tax_declaration_setup.exempt_sales = tax_declaration_setup.exempt_sales or sales_tax_templates['Exempt Sales']

    tax_declaration_setup.item_vat_sales = tax_declaration_setup.item_vat_sales or item_sales_tax_templates['VAT Sales']
    tax_declaration_setup.item_sales_to_government = tax_declaration_setup.item_sales_to_government or item_sales_tax_templates['Sales to Government']
    tax_declaration_setup.item_zero_rated_sales = tax_declaration_setup.item_zero_rated_sales or item_sales_tax_templates['Zero Rated Sales']
    tax_declaration_setup.item_exempt_sales = tax_declaration_setup.item_exempt_sales or item_sales_tax_templates['Exempt Sales']

    tax_declaration_setup.capital_goods = tax_declaration_setup.capital_goods or purchase_tax_templates['Capital Goods']
    tax_declaration_setup.capital_goods_exceeding_1m = tax_declaration_setup.capital_goods_exceeding_1m or purchase_tax_templates['Capital Goods Exceeding 1M']
    tax_declaration_setup.domestic_purchases_of_goods = tax_declaration_setup.domestic_purchases_of_goods or purchase_tax_templates['Domestic Purchases of Goods']
    tax_declaration_setup.importation_of_goods = tax_declaration_setup.importation_of_goods or purchase_tax_templates['Importation of Goods']
    tax_declaration_setup.domestic_purchase_of_services = tax_declaration_setup.domestic_purchase_of_services or purchase_tax_templates['Domestic Purchase of Services']
    tax_declaration_setup.services_rendered_by_non_residents = tax_declaration_setup.services_rendered_by_non_residents or purchase_tax_templates['Services Rendered by Non-residents']
    tax_declaration_setup.purchases_not_qualified_for_input_tax = tax_declaration_setup.purchases_not_qualified_for_input_tax or purchase_tax_templates['Purchases Not Qualified for Input Tax']
    tax_declaration_setup.others = tax_declaration_setup.others or purchase_tax_templates['Others']
    tax_declaration_setup.allocable_to_exempt_sales = tax_declaration_setup.allocable_to_exempt_sales or purchase_tax_templates['Allocable to Exempt Sales']
    
    tax_declaration_setup.item_capital_goods = tax_declaration_setup.item_capital_goods or item_purchase_tax_templates['Capital Goods']
    tax_declaration_setup.item_capital_goods_exceeding_1m = tax_declaration_setup.item_capital_goods_exceeding_1m or item_purchase_tax_templates['Capital Goods Exceeding 1M']
    tax_declaration_setup.item_domestic_purchases_of_goods = tax_declaration_setup.item_domestic_purchases_of_goods or item_purchase_tax_templates['Domestic Purchases of Goods']
    tax_declaration_setup.item_importation_of_goods = tax_declaration_setup.item_importation_of_goods or item_purchase_tax_templates['Importation of Goods']
    tax_declaration_setup.item_domestic_purchase_of_services = tax_declaration_setup.item_domestic_purchase_of_services or item_purchase_tax_templates['Domestic Purchase of Services']
    tax_declaration_setup.item_services_rendered_by_non_residents = tax_declaration_setup.item_services_rendered_by_non_residents or item_purchase_tax_templates['Services Rendered by Non-residents']
    tax_declaration_setup.item_purchases_not_qualified_for_input_tax = tax_declaration_setup.item_purchases_not_qualified_for_input_tax or item_purchase_tax_templates['Purchases Not Qualified for Input Tax']
    tax_declaration_setup.item_others = tax_declaration_setup.item_others or item_purchase_tax_templates['Others']
    tax_declaration_setup.item_allocable_to_exempt_sales = tax_declaration_setup.item_allocable_to_exempt_sales or item_purchase_tax_templates['Allocable to Exempt Sales']

    tax_declaration_setup.save()
    
    frappe.msgprint(_('Tax template(s) successfully created: <strong>{0}</strong>'.format(n)))

    return n