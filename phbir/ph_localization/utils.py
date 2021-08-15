import frappe
from frappe.utils import flt, rounded, getdate
from frappe import _

@frappe.whitelist()
def get_custom_formatted_address(address):
    result = ""
    if frappe.db.exists("Address", {'name': address}):
        address_doc = frappe.get_last_doc("Address", filters={"name": address})
        result = address_doc.address_line1 or ''
        result = result + (', ' if result and address_doc.address_line2 else '') + address_doc.address_line2
        result = result + (', ' if result and address_doc.city else '') + address_doc.city
        result = result + (', ' if result and address_doc.state else '') + address_doc.state
    return result