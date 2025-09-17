# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe import _

def after_install():
	"""Called after app installation"""
	frappe.logger().info("Starting Wix Integration app installation")
	
	# Create custom fields
	create_custom_fields_for_wix()
	
	# Create Wix Settings if it doesn't exist
	create_wix_settings_single()
	
	# Set up default sync settings
	setup_default_settings()
	
	frappe.db.commit()
	frappe.logger().info("Wix Integration app installation completed successfully")
	
	print("\n" + "="*60)
	print("🎉 Wix Integration App Installed Successfully!")
	print("="*60)
	print("Next Steps:")
	print("1. Go to Wix Settings in ERPNext")
	print("2. Configure your Wix Site ID and API credentials")
	print("3. Enable sync for Products and Orders")
	print("4. Test the connection using 'Test Connection' button")
	print("="*60 + "\n")

def create_custom_fields_for_wix():
	"""Create custom fields for Wix integration"""
	custom_fields = {
		"Item": [
			{
				"fieldname": "wix_product_id",
				"label": "Wix Product ID",
				"fieldtype": "Data",
				"read_only": 1,
				"hidden": 1,
				"description": "Unique identifier for the product in Wix"
			},
			{
				"fieldname": "sync_with_wix",
				"label": "Sync with Wix",
				"fieldtype": "Check",
				"default": 1,
				"description": "Enable sync with Wix e-commerce platform"
			},
			{
				"fieldname": "wix_sync_status",
				"label": "Wix Sync Status",
				"fieldtype": "Select",
				"options": "\nPending\nSynced\nFailed\nError",
				"read_only": 1,
				"description": "Current sync status with Wix"
			},
			{
				"fieldname": "last_wix_sync",
				"label": "Last Wix Sync",
				"fieldtype": "Datetime",
				"read_only": 1,
				"description": "Last successful sync with Wix"
			}
		],
		"Sales Order": [
			{
				"fieldname": "wix_order_id",
				"label": "Wix Order ID",
				"fieldtype": "Data",
				"read_only": 1,
				"hidden": 1,
				"description": "Unique identifier for the order in Wix"
			},
			{
				"fieldname": "wix_order_number",
				"label": "Wix Order Number",
				"fieldtype": "Data",
				"read_only": 1,
				"description": "Order number from Wix"
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	frappe.logger().info("Custom fields created for Wix integration")

def create_wix_settings_single():
	"""Create Wix Settings single doctype if it doesn't exist"""
	if not frappe.db.exists("Wix Settings", "Wix Settings"):
		doc = frappe.get_doc({
			"doctype": "Wix Settings",
			"name": "Wix Settings"
		})
		doc.insert(ignore_permissions=True)
		frappe.logger().info("Wix Settings document created")

def setup_default_settings():
	"""Set up default sync settings"""
	try:
		settings = frappe.get_single("Wix Settings")
		if not settings.default_item_group:
			# Get or create a default item group for Wix products
			default_group = frappe.db.get_value("Item Group", "Products")
			if not default_group:
				default_group = "All Item Groups"  # Fallback to system default
			
			settings.default_item_group = default_group
			settings.save(ignore_permissions=True)
			frappe.logger().info(f"Default settings configured with item group: {default_group}")
	except Exception as e:
		frappe.logger().error(f"Error setting up default settings: {str(e)}")

def before_tests():
	"""Called before running tests"""
	pass
