from . import __version__ as app_version

app_name = "medical_app"
app_title = "medical app"
app_publisher = "rasiin"
app_description = "medical app"
app_email = "rasiin@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/medical_app/css/medical_app.css"
# app_include_js = "/assets/medical_app/js/medical_app.js"

# include js, css files in header of web template
# web_include_css = "/assets/medical_app/css/medical_app.css"
# web_include_js = "/assets/medical_app/js/medical_app.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "medical_app/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
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

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "medical_app.utils.jinja_methods",
#	"filters": "medical_app.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "medical_app.install.before_install"
# after_install = "medical_app.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "medical_app.uninstall.before_uninstall"
# after_uninstall = "medical_app.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "medical_app.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"medical_app.tasks.all"
#	],
#	"daily": [
#		"medical_app.tasks.daily"
#	],
#	"hourly": [
#		"medical_app.tasks.hourly"
#	],
#	"weekly": [
#		"medical_app.tasks.weekly"
#	],
#	"monthly": [
#		"medical_app.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "medical_app.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "medical_app.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "medical_app.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["medical_app.utils.before_request"]
# after_request = ["medical_app.utils.after_request"]

# Job Events
# ----------
# before_job = ["medical_app.utils.before_job"]
# after_job = ["medical_app.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"medical_app.auth.validate"
# ]
