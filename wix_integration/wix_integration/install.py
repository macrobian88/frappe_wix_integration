# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
    """Called after app installation"""
    create_wix_settings_doctype()
    create_custom_fields_for_item()
    create_wix_settings_record()
    create_wix_integration_log_doctype()
    print("Wix Integration app installed successfully!")

def create_wix_settings_doctype():
    """Create Wix Settings DocType if it doesn't exist"""
    if not frappe.db.exists("DocType", "Wix Settings"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Wix Settings",
            "module": "Wix Integration",
            "custom": 1,
            "istable": 0,
            "issingle": 1,
            "track_changes": 1,
            "fields": [
                {
                    "fieldname": "enabled",
                    "label": "Enable Wix Integration",
                    "fieldtype": "Check",
                    "default": "0",
                    "description": "Enable or disable Wix integration"
                },
                {
                    "fieldname": "section_break_1",
                    "fieldtype": "Section Break",
                    "label": "Wix API Credentials"
                },
                {
                    "fieldname": "site_id",
                    "label": "Wix Site ID",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "description": "Your Wix site ID"
                },
                {
                    "fieldname": "api_key",
                    "label": "Wix API Key",
                    "fieldtype": "Password",
                    "reqd": 1,
                    "description": "Your Wix API key for authentication"
                },
                {
                    "fieldname": "account_id",
                    "label": "Wix Account ID",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "description": "Your Wix account ID"
                },
                {
                    "fieldname": "column_break_1",
                    "fieldtype": "Column Break"
                },
                {
                    "fieldname": "api_url",
                    "label": "Wix API URL",
                    "fieldtype": "Data",
                    "default": "https://www.wixapis.com",
                    "reqd": 1,
                    "description": "Base URL for Wix API"
                },
                {
                    "fieldname": "webhook_secret",
                    "label": "Webhook Secret",
                    "fieldtype": "Password",
                    "description": "Secret for validating incoming webhooks"
                },
                {
                    "fieldname": "section_break_2",
                    "fieldtype": "Section Break",
                    "label": "Sync Settings"
                },
                {
                    "fieldname": "sync_products",
                    "label": "Sync Products to Wix",
                    "fieldtype": "Check",
                    "default": "1",
                    "description": "Automatically sync items to Wix when created/updated"
                },
                {
                    "fieldname": "sync_orders",
                    "label": "Sync Orders from Wix",
                    "fieldtype": "Check",
                    "default": "1",
                    "description": "Automatically sync orders from Wix to ERPNext"
                },
                {
                    "fieldname": "default_item_group",
                    "label": "Default Item Group",
                    "fieldtype": "Link",
                    "options": "Item Group",
                    "description": "Default item group for products synced from Wix"
                },
                {
                    "fieldname": "column_break_2",
                    "fieldtype": "Column Break"
                },
                {
                    "fieldname": "default_customer_group",
                    "label": "Default Customer Group",
                    "fieldtype": "Link",
                    "options": "Customer Group",
                    "description": "Default customer group for customers from Wix"
                },
                {
                    "fieldname": "default_territory",
                    "label": "Default Territory",
                    "fieldtype": "Link",
                    "options": "Territory",
                    "description": "Default territory for customers from Wix"
                },
                {
                    "fieldname": "default_company",
                    "label": "Default Company",
                    "fieldtype": "Link",
                    "options": "Company",
                    "description": "Default company for transactions"
                },
                {
                    "fieldname": "section_break_3",
                    "fieldtype": "Section Break",
                    "label": "Error Handling"
                },
                {
                    "fieldname": "max_retry_attempts",
                    "label": "Max Retry Attempts",
                    "fieldtype": "Int",
                    "default": "3",
                    "description": "Maximum number of retry attempts for failed sync operations"
                },
                {
                    "fieldname": "log_errors",
                    "label": "Log Sync Errors",
                    "fieldtype": "Check",
                    "default": "1",
                    "description": "Log all sync errors for debugging"
                }
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1
                },
                {
                    "role": "Administrator",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1
                }
            ]
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()

def create_custom_fields_for_item():
    """Create custom fields for Item DocType"""
    custom_fields = {
        "Item": [
            {
                "fieldname": "wix_integration_section",
                "label": "Wix Integration",
                "fieldtype": "Section Break",
                "insert_after": "description",
                "collapsible": 1
            },
            {
                "fieldname": "sync_with_wix",
                "label": "Sync with Wix",
                "fieldtype": "Check",
                "insert_after": "wix_integration_section",
                "default": "0",
                "description": "Enable sync with Wix for this item"
            },
            {
                "fieldname": "wix_product_id",
                "label": "Wix Product ID",
                "fieldtype": "Data",
                "insert_after": "sync_with_wix",
                "read_only": 1,
                "description": "Wix product ID (auto-generated)"
            },
            {
                "fieldname": "wix_product_slug",
                "label": "Wix Product Slug",
                "fieldtype": "Data",
                "insert_after": "wix_product_id",
                "description": "URL slug for Wix product"
            },
            {
                "fieldname": "column_break_wix",
                "fieldtype": "Column Break",
                "insert_after": "wix_product_slug"
            },
            {
                "fieldname": "wix_last_sync",
                "label": "Last Synced",
                "fieldtype": "Datetime",
                "insert_after": "column_break_wix",
                "read_only": 1,
                "description": "Last sync timestamp"
            },
            {
                "fieldname": "wix_sync_status",
                "label": "Sync Status",
                "fieldtype": "Select",
                "options": "\nPending\nSuccess\nFailed\nSkipped",
                "insert_after": "wix_last_sync",
                "read_only": 1,
                "default": "Pending"
            }
        ]
    }
    
    create_custom_fields(custom_fields)

def create_wix_integration_log_doctype():
    """Create Wix Integration Log DocType"""
    if not frappe.db.exists("DocType", "Wix Integration Log"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Wix Integration Log",
            "module": "Wix Integration",
            "custom": 1,
            "istable": 0,
            "naming_rule": "By fieldname",
            "autoname": "field:log_id",
            "title_field": "log_id",
            "sort_field": "creation",
            "sort_order": "DESC",
            "track_changes": 1,
            "fields": [
                {
                    "fieldname": "log_id",
                    "label": "Log ID",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "unique": 1
                },
                {
                    "fieldname": "operation",
                    "label": "Operation",
                    "fieldtype": "Select",
                    "options": "\nProduct Sync\nOrder Sync\nWebhook\nManual Sync",
                    "reqd": 1
                },
                {
                    "fieldname": "status",
                    "label": "Status",
                    "fieldtype": "Select",
                    "options": "\nSuccess\nFailed\nPending\nRetrying",
                    "reqd": 1,
                    "default": "Pending"
                },
                {
                    "fieldname": "column_break_1",
                    "fieldtype": "Column Break"
                },
                {
                    "fieldname": "document_type",
                    "label": "Document Type",
                    "fieldtype": "Data",
                    "description": "ERPNext document type (Item, Sales Order, etc.)"
                },
                {
                    "fieldname": "document_name",
                    "label": "Document Name",
                    "fieldtype": "Data",
                    "description": "ERPNext document name"
                },
                {
                    "fieldname": "wix_id",
                    "label": "Wix ID",
                    "fieldtype": "Data",
                    "description": "Wix product/order ID"
                },
                {
                    "fieldname": "section_break_1",
                    "fieldtype": "Section Break",
                    "label": "Details"
                },
                {
                    "fieldname": "request_data",
                    "label": "Request Data",
                    "fieldtype": "Code",
                    "options": "JSON",
                    "description": "Request payload sent to Wix"
                },
                {
                    "fieldname": "response_data",
                    "label": "Response Data",
                    "fieldtype": "Code",
                    "options": "JSON",
                    "description": "Response received from Wix"
                },
                {
                    "fieldname": "column_break_2",
                    "fieldtype": "Column Break"
                },
                {
                    "fieldname": "error_message",
                    "label": "Error Message",
                    "fieldtype": "Long Text",
                    "description": "Error details if operation failed"
                },
                {
                    "fieldname": "retry_count",
                    "label": "Retry Count",
                    "fieldtype": "Int",
                    "default": "0"
                },
                {
                    "fieldname": "execution_time",
                    "label": "Execution Time (ms)",
                    "fieldtype": "Int",
                    "description": "Time taken for operation in milliseconds"
                }
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1
                },
                {
                    "role": "Sales Manager",
                    "read": 1
                },
                {
                    "role": "Stock Manager",
                    "read": 1
                }
            ]
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()

def create_wix_settings_record():
    """Create default Wix Settings record"""
    if not frappe.db.exists("Wix Settings", "Wix Settings"):
        doc = frappe.get_doc({
            "doctype": "Wix Settings",
            "name": "Wix Settings",
            "enabled": 0,
            "api_url": "https://www.wixapis.com",
            "sync_products": 1,
            "sync_orders": 1,
            "max_retry_attempts": 3,
            "log_errors": 1
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()