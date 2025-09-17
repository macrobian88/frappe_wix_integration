# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from .utils import retry_failed_syncs, clean_old_logs
from .api import get_wix_settings

def hourly():
    """Hourly scheduled tasks"""
    # Retry failed syncs
    retry_failed_syncs()

def daily():
    """Daily scheduled tasks"""
    # Clean up old logs (keep last 30 days)
    clean_old_logs(days=30)
    
    # Health check - ensure Wix connection is working
    health_check()

def weekly():
    """Weekly scheduled tasks"""
    # Generate sync report
    generate_sync_report()

def health_check():
    """Check Wix integration health"""
    try:
        settings = get_wix_settings()
        if not settings or not settings.enabled:
            return
        
        from .api import test_wix_connection
        result = test_wix_connection()
        
        if not result.get('success'):
            # Log health check failure
            frappe.log_error(
                message=f"Wix integration health check failed: {result.get('error')}",
                title="Wix Integration Health Check Failed"
            )
            
            # Optionally send notification to admin
            send_health_check_notification(result.get('error'))
            
    except Exception as e:
        frappe.log_error(
            message=str(e),
            title="Wix Integration Health Check Error"
        )

def send_health_check_notification(error_message):
    """Send notification when health check fails"""
    try:
        # Get system managers
        system_managers = frappe.get_all(
            "Has Role",
            filters={"role": "System Manager"},
            fields=["parent"]
        )
        
        for manager in system_managers:
            user = manager.parent
            if frappe.db.get_value("User", user, "enabled"):
                frappe.get_doc({
                    "doctype": "Notification Log",
                    "subject": "Wix Integration Health Check Failed",
                    "for_user": user,
                    "type": "Alert",
                    "document_type": "Wix Settings",
                    "document_name": "Wix Settings",
                    "email_content": f"""
                    <p>The Wix integration health check has failed.</p>
                    <p><strong>Error:</strong> {error_message}</p>
                    <p>Please check the Wix Settings and API credentials.</p>
                    """
                }).insert(ignore_permissions=True)
                
    except Exception as e:
        frappe.log_error(
            message=str(e),
            title="Failed to send health check notification"
        )

def generate_sync_report():
    """Generate weekly sync report"""
    try:
        from frappe.utils import add_days, today
        from datetime import datetime
        
        # Get stats for the last 7 days
        week_ago = add_days(today(), -7)
        
        # Count sync operations
        total_syncs = frappe.db.count(
            "Wix Integration Log",
            filters={"creation": (">=", week_ago)}
        )
        
        successful_syncs = frappe.db.count(
            "Wix Integration Log",
            filters={
                "creation": (">=", week_ago),
                "status": "Success"
            }
        )
        
        failed_syncs = frappe.db.count(
            "Wix Integration Log",
            filters={
                "creation": (">=", week_ago),
                "status": "Failed"
            }
        )
        
        # Get operation breakdown
        operations = frappe.db.sql("""
            SELECT operation, COUNT(*) as count
            FROM `tabWix Integration Log`
            WHERE creation >= %s
            GROUP BY operation
        """, (week_ago,), as_dict=True)
        
        # Create report document
        report_data = {
            "doctype": "Wix Integration Log",
            "log_id": f"weekly_report_{int(datetime.now().timestamp())}",
            "operation": "Weekly Report",
            "status": "Success",
            "response_data": frappe.as_json({
                "report_period": f"{week_ago} to {today()}",
                "total_syncs": total_syncs,
                "successful_syncs": successful_syncs,
                "failed_syncs": failed_syncs,
                "success_rate": f"{(successful_syncs/total_syncs*100):.1f}%" if total_syncs > 0 else "0%",
                "operations_breakdown": operations
            }, indent=2)
        }
        
        report_doc = frappe.get_doc(report_data)
        report_doc.insert(ignore_permissions=True)
        
    except Exception as e:
        frappe.log_error(
            message=str(e),
            title="Failed to generate sync report"
        )
