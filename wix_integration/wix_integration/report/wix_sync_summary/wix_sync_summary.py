# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, add_days

def execute(filters=None):
	"""Generate Wix Sync Summary Report"""
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	summary = get_summary(data)
	
	return columns, data, None, chart, summary

def get_columns():
	"""Define report columns"""
	return [
		{
			"fieldname": "sync_date",
			"label": _("Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "sync_type",
			"label": _("Sync Type"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "total_syncs",
			"label": _("Total Syncs"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "successful_syncs",
			"label": _("Successful"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "failed_syncs",
			"label": _("Failed"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "success_rate",
			"label": _("Success Rate %"),
			"fieldtype": "Percent",
			"width": 120
		},
		{
			"fieldname": "avg_response_time",
			"label": _("Avg Response Time (s)"),
			"fieldtype": "Float",
			"width": 150,
			"precision": 2
		}
	]

def get_data(filters):
	"""Get report data based on filters"""
	filters = filters or {}
	
	# Set default date range if not provided
	if not filters.get("from_date"):
		filters["from_date"] = add_days(frappe.utils.today(), -30)
	if not filters.get("to_date"):
		filters["to_date"] = frappe.utils.today()
	
	# Base query
	query = """
		SELECT 
			DATE(sync_date) as sync_date,
			sync_type,
			COUNT(*) as total_syncs,
			SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) as successful_syncs,
			SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) as failed_syncs,
			(SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as success_rate,
			0 as avg_response_time
		FROM `tabWix Sync Log`
		WHERE DATE(sync_date) BETWEEN %(from_date)s AND %(to_date)s
	"""
	
	# Add sync type filter if specified
	if filters.get("sync_type"):
		query += " AND sync_type = %(sync_type)s"
	
	# Add status filter if specified
	if filters.get("status"):
		query += " AND status = %(status)s"
	
	query += " GROUP BY DATE(sync_date), sync_type ORDER BY sync_date DESC, sync_type"
	
	return frappe.db.sql(query, filters, as_dict=True)

def get_chart_data(data):
	"""Generate chart data for the report"""
	if not data:
		return None
	
	# Group data by date for chart
	date_wise_data = {}
	for row in data:
		date_str = str(row.sync_date)
		if date_str not in date_wise_data:
			date_wise_data[date_str] = {
				"total": 0,
				"successful": 0,
				"failed": 0
			}
		
		date_wise_data[date_str]["total"] += row.total_syncs
		date_wise_data[date_str]["successful"] += row.successful_syncs
		date_wise_data[date_str]["failed"] += row.failed_syncs
	
	# Sort dates
	sorted_dates = sorted(date_wise_data.keys())
	
	chart = {
		"data": {
			"labels": sorted_dates,
			"datasets": [
				{
					"name": "Successful Syncs",
					"values": [date_wise_data[date]["successful"] for date in sorted_dates],
					"chartType": "bar"
				},
				{
					"name": "Failed Syncs",
					"values": [date_wise_data[date]["failed"] for date in sorted_dates],
					"chartType": "bar"
				}
			]
		},
		"type": "bar",
		"height": 300,
		"colors": ["#28a745", "#dc3545"]
	}
	
	return chart

def get_summary(data):
	"""Generate summary statistics"""
	if not data:
		return []
	
	total_syncs = sum(row.total_syncs for row in data)
	successful_syncs = sum(row.successful_syncs for row in data)
	failed_syncs = sum(row.failed_syncs for row in data)
	overall_success_rate = (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0
	
	summary = [
		{
			"label": _("Total Sync Operations"),
			"value": total_syncs,
			"indicator": "Blue"
		},
		{
			"label": _("Successful Syncs"),
			"value": successful_syncs,
			"indicator": "Green"
		},
		{
			"label": _("Failed Syncs"),
			"value": failed_syncs,
			"indicator": "Red"
		},
		{
			"label": _("Overall Success Rate"),
			"value": f"{overall_success_rate:.1f}%",
			"indicator": "Green" if overall_success_rate >= 90 else "Orange" if overall_success_rate >= 70 else "Red"
		}
	]
	
	return summary
