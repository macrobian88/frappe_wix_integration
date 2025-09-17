# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
import requests
import json

class WixSettings(Document):
	"""Wix Settings DocType for managing Wix integration configuration"""
	
	def validate(self):
		"""Validate Wix settings before saving"""
		if self.enable_sync:
			if not self.wix_site_id:
				frappe.throw(_("Wix Site ID is required when sync is enabled"))
			
			if not self.wix_api_key:
				frappe.throw(_("Wix API Key is required when sync is enabled"))
			
			if not self.default_item_group:
				frappe.throw(_("Default Item Group is required when sync is enabled"))
		
		# Validate API credentials if provided
		if self.wix_site_id and self.wix_api_key:
			self.validate_wix_credentials()
	
	def validate_wix_credentials(self):
		"""Validate Wix API credentials"""
		try:
			# Test connection to Wix API
			headers = {
				'Authorization': f'Bearer {self.wix_api_key}',
				'Content-Type': 'application/json',
				'wix-site-id': self.wix_site_id
			}
			
			# Try to fetch site info to validate credentials
			response = requests.get(
				f'https://www.wixapis.com/stores/v3/products?limit=1',
				headers=headers,
				timeout=10
			)
			
			if response.status_code == 401:
				frappe.throw(_("Invalid Wix API credentials. Please check your API Key and Site ID."))
			elif response.status_code == 403:
				frappe.throw(_("Access denied. Please ensure your Wix API Key has the necessary permissions."))
			elif response.status_code != 200:
				frappe.throw(_(f"Failed to connect to Wix API. Status code: {response.status_code}"))
			
			frappe.msgprint(_("Wix API credentials validated successfully!"), alert=True)
			
		except requests.exceptions.RequestException as e:
			frappe.throw(_(f"Failed to connect to Wix API: {str(e)}"))
		except Exception as e:
			frappe.log_error(f"Error validating Wix credentials: {str(e)}")
			frappe.throw(_(f"Error validating credentials: {str(e)}"))
	
	@frappe.whitelist()
	def test_connection(self):
		"""Test connection to Wix API"""
		try:
			self.validate_wix_credentials()
			return {"status": "success", "message": "Connection successful!"}
		except Exception as e:
			frappe.log_error(f"Wix connection test failed: {str(e)}")
			return {"status": "error", "message": str(e)}
	
	def on_update(self):
		"""Called when document is updated"""
		# Clear cache when settings are updated
		frappe.cache().delete_value("wix_settings")
		
		# Log the update
		frappe.logger().info("Wix Settings updated")
	
	@staticmethod
	def get_settings():
		"""Get Wix settings with caching"""
		cached_settings = frappe.cache().get_value("wix_settings")
		if cached_settings:
			return cached_settings
		
		settings = frappe.get_single("Wix Settings")
		frappe.cache().set_value("wix_settings", settings, expires_in_sec=300)  # Cache for 5 minutes
		return settings
