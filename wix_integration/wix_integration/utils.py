# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
import hashlib
import hmac
import json
from frappe.utils import cstr

def validate_webhook_signature(payload, signature, secret):
    """Validate webhook signature from Wix"""
    if not secret:
        return False
    
    # Create expected signature
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures
    return hmac.compare_digest(signature, expected_signature)

def format_wix_error(error_response):
    """Format Wix API error response"""
    if isinstance(error_response, dict):
        if 'message' in error_response:
            return error_response['message']
        elif 'error' in error_response:
            return error_response['error']
        else:
            return json.dumps(error_response)
    return cstr(error_response)

def get_item_image_url(item_doc):
    """Get full URL for item image"""
    if not item_doc.image:
        return None
    
    from frappe.utils import get_site_url
    site_url = get_site_url()
    
    # Handle both relative and absolute URLs
    if item_doc.image.startswith('http'):
        return item_doc.image
    else:
        return f"{site_url}{item_doc.image}"

def sanitize_html(text):
    """Remove HTML tags from text"""
    if not text:
        return text
    
    import re
    # Remove HTML tags
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def format_currency(amount, currency='USD'):
    """Format currency for Wix"""
    if not amount:
        return "0"
    return str(float(amount))

def get_wix_product_type(item_doc):
    """Determine Wix product type based on item properties"""
    # For now, default to PHYSICAL
    # This can be enhanced based on item properties or custom fields
    return "PHYSICAL"

def log_wix_api_call(operation, method, url, headers, payload, response, execution_time):
    """Log Wix API calls for debugging"""
    if frappe.conf.get('developer_mode'):
        frappe.log_error(
            message=json.dumps({
                'operation': operation,
                'method': method,
                'url': url,
                'headers': {k: v for k, v in headers.items() if k.lower() != 'authorization'},
                'payload': payload,
                'response': response,
                'execution_time_ms': execution_time
            }, indent=2),
            title=f"Wix API Call - {operation}"
        )

def retry_failed_syncs():
    """Retry failed sync operations (can be called via scheduler)"""
    settings = frappe.get_single("Wix Settings")
    if not settings.enabled:
        return
    
    # Get failed sync logs that haven't exceeded retry limit
    failed_logs = frappe.get_all(
        "Wix Integration Log",
        filters={
            "status": "Failed",
            "retry_count": ("<", settings.max_retry_attempts)
        },
        fields=["name", "document_type", "document_name", "operation", "retry_count"]
    )
    
    for log in failed_logs:
        try:
            if log.document_type == "Item" and log.operation == "Product Sync":
                item_doc = frappe.get_doc("Item", log.document_name)
                if item_doc.sync_with_wix:
                    # Update retry count
                    frappe.db.set_value(
                        "Wix Integration Log", 
                        log.name, 
                        "retry_count", 
                        log.retry_count + 1
                    )
                    
                    # Retry sync
                    from .api import sync_product_to_wix
                    sync_product_to_wix(item_doc)
                    
        except Exception as e:
            frappe.log_error(
                message=str(e),
                title=f"Failed to retry sync for {log.document_name}"
            )

def clean_old_logs(days=30):
    """Clean up old integration logs"""
    from frappe.utils import add_days, today
    cutoff_date = add_days(today(), -days)
    
    frappe.db.sql(
        "DELETE FROM `tabWix Integration Log` WHERE DATE(creation) < %s",
        (cutoff_date,)
    )
    
    frappe.db.commit()