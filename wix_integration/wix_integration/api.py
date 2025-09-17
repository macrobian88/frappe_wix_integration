# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
import requests
import json
import time
from datetime import datetime
from frappe import _
from frappe.utils import now_datetime, get_site_url, cstr

@frappe.whitelist()
def sync_product_to_wix(doc, method=None):
    """Sync Item to Wix when created or updated"""
    # Check if Wix integration is enabled
    settings = get_wix_settings()
    if not settings or not settings.enabled or not settings.sync_products:
        return
    
    # Check if this item should be synced
    if not getattr(doc, 'sync_with_wix', False):
        return
    
    try:
        log_id = create_integration_log(
            operation="Product Sync",
            document_type="Item",
            document_name=doc.name,
            status="Pending"
        )
        
        start_time = time.time()
        
        # Prepare product data for Wix
        product_data = prepare_product_data(doc)
        
        # Check if product already exists in Wix
        if doc.wix_product_id:
            result = update_wix_product(doc.wix_product_id, product_data, settings)
        else:
            result = create_wix_product(product_data, settings)
            if result.get('success') and result.get('product', {}).get('id'):
                # Update item with Wix product ID
                frappe.db.set_value('Item', doc.name, 'wix_product_id', result['product']['id'])
        
        execution_time = int((time.time() - start_time) * 1000)
        
        if result.get('success'):
            # Update sync status
            frappe.db.set_value('Item', doc.name, {
                'wix_last_sync': now_datetime(),
                'wix_sync_status': 'Success'
            })
            
            update_integration_log(
                log_id,
                status="Success",
                response_data=json.dumps(result.get('product', {}), indent=2),
                execution_time=execution_time
            )
        else:
            frappe.db.set_value('Item', doc.name, 'wix_sync_status', 'Failed')
            update_integration_log(
                log_id,
                status="Failed",
                error_message=result.get('error', 'Unknown error'),
                response_data=json.dumps(result, indent=2),
                execution_time=execution_time
            )
            
    except Exception as e:
        frappe.log_error(
            message=str(e),
            title=f"Wix Product Sync Failed - {doc.name}"
        )
        
        frappe.db.set_value('Item', doc.name, 'wix_sync_status', 'Failed')
        
        if 'log_id' in locals():
            update_integration_log(
                log_id,
                status="Failed",
                error_message=str(e)
            )

def prepare_product_data(item_doc):
    """Prepare product data in Wix format"""
    # Get item image URL if available
    image_url = None
    if item_doc.image:
        site_url = get_site_url()
        image_url = f"{site_url}{item_doc.image}"
    
    # Basic product structure for Wix Catalog V3
    product_data = {
        "name": item_doc.item_name or item_doc.item_code,
        "productType": "PHYSICAL",  # Default to physical product
        "description": {
            "nodes": [{
                "type": "PARAGRAPH",
                "id": "paragraph-1",
                "nodes": [{
                    "type": "TEXT",
                    "textData": {
                        "text": item_doc.description or item_doc.item_name or item_doc.item_code
                    }
                }]
            }]
        } if item_doc.description else None,
        "physicalProperties": {},
        "variantsInfo": {
            "variants": [{
                "price": {
                    "actualPrice": {
                        "amount": str(item_doc.standard_rate or 0)
                    }
                },
                "physicalProperties": {
                    "weight": item_doc.weight_per_unit or 0
                }
            }]
        }
    }
    
    # Add product slug if specified
    if getattr(item_doc, 'wix_product_slug', None):
        product_data["slug"] = item_doc.wix_product_slug
    
    # Add media if image is available
    if image_url:
        product_data["media"] = {
            "main": {
                "items": [{
                    "url": image_url,
                    "altText": item_doc.item_name or item_doc.item_code
                }]
            }
        }
    
    return product_data

def create_wix_product(product_data, settings):
    """Create a new product in Wix"""
    try:
        headers = get_wix_headers(settings)
        url = f"{settings.api_url}/stores/v3/products"
        
        payload = {
            "product": product_data
        }
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "product": result.get("product", {})
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def update_wix_product(product_id, product_data, settings):
    """Update an existing product in Wix"""
    try:
        headers = get_wix_headers(settings)
        url = f"{settings.api_url}/stores/v3/products/{product_id}"
        
        # Get current product to merge data
        current_product = get_wix_product(product_id, settings)
        if not current_product.get('success'):
            return current_product
        
        # Merge update data with current product
        updated_product = current_product['product'].copy()
        updated_product.update(product_data)
        
        payload = {
            "product": updated_product
        }
        
        response = requests.patch(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "product": result.get("product", {})
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def get_wix_product(product_id, settings):
    """Get a product from Wix"""
    try:
        headers = get_wix_headers(settings)
        url = f"{settings.api_url}/stores/v3/products/{product_id}"
        
        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "product": result.get("product", {})
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def get_wix_headers(settings):
    """Get headers for Wix API requests"""
    return {
        "Authorization": f"Bearer {settings.api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "wix-site-id": settings.site_id,
        "wix-account-id": settings.account_id
    }

def get_wix_settings():
    """Get Wix integration settings"""
    try:
        return frappe.get_single("Wix Settings")
    except Exception:
        return None

def create_integration_log(operation, document_type=None, document_name=None, 
                          wix_id=None, status="Pending", request_data=None):
    """Create a new integration log entry"""
    log_id = f"{operation.replace(' ', '_').lower()}_{int(time.time() * 1000)}"
    
    log_doc = frappe.get_doc({
        "doctype": "Wix Integration Log",
        "log_id": log_id,
        "operation": operation,
        "status": status,
        "document_type": document_type,
        "document_name": document_name,
        "wix_id": wix_id,
        "request_data": json.dumps(request_data, indent=2) if request_data else None,
        "retry_count": 0
    })
    
    log_doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return log_id

def update_integration_log(log_id, status=None, response_data=None, 
                          error_message=None, execution_time=None, retry_count=None):
    """Update an existing integration log entry"""
    update_data = {}
    
    if status:
        update_data['status'] = status
    if response_data:
        update_data['response_data'] = response_data
    if error_message:
        update_data['error_message'] = error_message
    if execution_time:
        update_data['execution_time'] = execution_time
    if retry_count is not None:
        update_data['retry_count'] = retry_count
    
    if update_data:
        frappe.db.set_value("Wix Integration Log", {"log_id": log_id}, update_data)
        frappe.db.commit()

@frappe.whitelist()
def manual_sync_item(item_name):
    """Manually sync an item to Wix"""
    if not frappe.has_permission("Item", "write"):
        frappe.throw(_("You don't have permission to sync items"))
    
    item_doc = frappe.get_doc("Item", item_name)
    sync_product_to_wix(item_doc)
    
    return {
        "message": _("Item sync initiated successfully"),
        "status": "success"
    }

@frappe.whitelist()
def test_wix_connection():
    """Test Wix API connection"""
    if not frappe.has_permission("Wix Settings", "read"):
        frappe.throw(_("You don't have permission to test connection"))
    
    settings = get_wix_settings()
    if not settings:
        return {
            "success": False,
            "error": "Wix Settings not found"
        }
    
    if not all([settings.site_id, settings.api_key, settings.account_id]):
        return {
            "success": False,
            "error": "Please configure all required Wix credentials"
        }
    
    try:
        headers = get_wix_headers(settings)
        url = f"{settings.api_url}/stores/v3/products"
        
        # Test with a simple GET request with limit
        response = requests.get(
            f"{url}?limit=1",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": "Connection successful"
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
def get_sync_status(item_name):
    """Get sync status for an item"""
    item = frappe.get_value("Item", item_name, 
                           ["wix_product_id", "wix_last_sync", "wix_sync_status"],
                           as_dict=True)
    
    # Get recent logs for this item
    logs = frappe.get_all("Wix Integration Log",
                         filters={
                             "document_type": "Item",
                             "document_name": item_name
                         },
                         fields=["status", "error_message", "creation"],
                         order_by="creation desc",
                         limit=5)
    
    return {
        "item": item,
        "logs": logs
    }
