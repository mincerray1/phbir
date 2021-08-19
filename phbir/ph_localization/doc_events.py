from __future__ import unicode_literals
from frappe import _
import frappe

from frappe.utils import (add_days, cstr, flt, get_datetime, getdate, nowdate, today)

def sales_invoice_validate(doc, method):
    validate_item_tax_template(doc)

def purchase_invoice_validate(doc, method):
    validate_item_tax_template(doc)

def validate_item_tax_template(doc):
    message = ''
    multiple_distinct_item_tax_template = []

    for i in doc.items:
        if i.item_code in multiple_distinct_item_tax_template:
            break
        for j in doc.items:
            if i.idx != j.idx and i.item_code == j.item_code and i.item_tax_template != j.item_tax_template:
                if not i.item_code in multiple_distinct_item_tax_template:
                    multiple_distinct_item_tax_template.append(i.item_code)
                    break
        
    if multiple_distinct_item_tax_template:
        message = "The following item(s) cannot be assigned to multiple different tax templates: <ul>"
        for i in multiple_distinct_item_tax_template:
            message = message + "<li><strong>" + i + "</strong></li>"
        message = message + "</ul>"

        frappe.throw(
            title="Item Tax Template",
            msg=message
        )
    