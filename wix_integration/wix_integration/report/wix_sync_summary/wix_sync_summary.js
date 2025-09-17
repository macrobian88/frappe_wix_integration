// Copyright (c) 2024, Your Company and contributors
// For license information, please see license.txt

frappe.query_reports["Wix Sync Summary"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_days(frappe.datetime.get_today(), -30),
			reqd: 1
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1
		},
		{
			fieldname: "sync_type",
			label: __("Sync Type"),
			fieldtype: "Select",
			options: ["All", "Product Sync", "Order Sync", "Inventory Sync", "Customer Sync"],
			default: "All"
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: ["All", "Pending", "Success", "Failed", "Retrying"],
			default: "All"
		}
	],

	onload: function(report) {
		// Add custom buttons
		report.page.add_inner_button(__("Refresh Data"), function() {
			report.refresh();
		});

		report.page.add_inner_button(__("Export to Excel"), function() {
			frappe.utils.export_query_report(
				report.report_name,
				report.get_filter_values(),
				"Excel"
			);
		});

		report.page.add_inner_button(__("View Sync Logs"), function() {
			frappe.set_route("List", "Wix Sync Log");
		});
	},

	formatter: function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		// Format success rate with color coding
		if (column.fieldname === "success_rate" && data) {
			let success_rate = data.success_rate;
			let color = "";
			
			if (success_rate >= 95) {
				color = "green";
			} else if (success_rate >= 85) {
				color = "orange";
			} else {
				color = "red";
			}
			
			value = `<span style="color: ${color}; font-weight: bold;">${value}</span>`;
		}

		// Format sync type with icons
		if (column.fieldname === "sync_type" && data) {
			let icon = "";
			switch(data.sync_type) {
				case "Product Sync":
					icon = "<i class='fa fa-cube' style='margin-right: 5px;'></i>";
					break;
				case "Order Sync":
					icon = "<i class='fa fa-shopping-cart' style='margin-right: 5px;'></i>";
					break;
				case "Inventory Sync":
					icon = "<i class='fa fa-warehouse' style='margin-right: 5px;'></i>";
					break;
				case "Customer Sync":
					icon = "<i class='fa fa-users' style='margin-right: 5px;'></i>";
					break;
			}
			value = icon + value;
		}

		return value;
	}
};
