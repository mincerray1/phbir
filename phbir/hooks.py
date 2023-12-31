# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "phbir"
app_title = "PH Localization"
app_publisher = "SERVIO Technologies"
app_description = "This app is for Philippine-specific features."
app_icon = "book"
app_color = "grey"
app_email = "mmacutay@servio.ph"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/phbir/css/phbir.css"
# app_include_js = "/assets/phbir/js/phbir.js"

# include js, css files in header of web template
# web_include_css = "/assets/phbir/css/phbir.css"
# web_include_js = "/assets/phbir/js/phbir.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "phbir/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}

doctype_js = {
    "Purchase Invoice" : "public/js/purchase_invoice.js",
    "Sales Invoice" : "public/js/sales_invoice.js",
    "Payment Entry" : "public/js/payment_entry.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "phbir.install.before_install"
# after_install = "phbir.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "phbir.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

doc_events = {
    "Sales Invoice": {
        "validate": "phbir.ph_localization.doc_events.sales_invoice_validate",
    },
    "Purchase Invoice": {
        "validate": "phbir.ph_localization.doc_events.purchase_invoice_validate",
    },
    "Payment Entry": {
        "validate": "phbir.ph_localization.doc_events.payment_entry_validate",
    },
}

jenv = {
	"methods": [
		"is_local_dev:phbir.ph_localization.utils.is_local_dev",
		"preformat_tin:phbir.ph_localization.utils.preformat_tin",
		"preformat_tin_with_dash:phbir.ph_localization.utils.preformat_tin_with_dash"
	]
}


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"phbir.tasks.all"
# 	],
# 	"daily": [
# 		"phbir.tasks.daily"
# 	],
# 	"hourly": [
# 		"phbir.tasks.hourly"
# 	],
# 	"weekly": [
# 		"phbir.tasks.weekly"
# 	]
# 	"monthly": [
# 		"phbir.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "phbir.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "phbir.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "phbir.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

fixtures = [
    {
        "dt": "Letter Head", "filters": [
            [
                "name", "in", [
                    "BOA Letterhead"
                ]
            ]
        ]
    },
    {
        "dt": "PH Tax Type Code"
    },
    {
        "dt": "ATC"
    },
    {
        "dt": "VAT Industry"
    }
]