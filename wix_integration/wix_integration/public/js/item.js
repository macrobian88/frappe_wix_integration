// Custom JavaScript for Item DocType
frappe.ui.form.on('Item', {
    refresh: function(frm) {
        // Add custom buttons for Wix integration
        if (!frm.doc.__islocal && frm.doc.sync_with_wix) {
            add_wix_buttons(frm);
        }
        
        // Add help text for Wix integration
        if (frm.doc.sync_with_wix) {
            frm.dashboard.add_comment(
                'This item is configured for Wix sync. Changes will be automatically synced to your Wix store.',
                'blue',
                true
            );
        }
    },
    
    sync_with_wix: function(frm) {
        if (frm.doc.sync_with_wix && !frm.doc.wix_product_id) {
            frm.dashboard.add_comment(
                'Wix sync enabled. Save the item to start syncing with Wix.',
                'orange',
                true
            );
        }
    },
    
    before_save: function(frm) {
        // Validate Wix settings if sync is enabled
        if (frm.doc.sync_with_wix) {
            validate_wix_settings();
        }
    }
});

function add_wix_buttons(frm) {
    // Manual sync button
    frm.add_custom_button(__('Sync to Wix'), function() {
        sync_item_to_wix(frm);
    }, __('Wix Integration'));
    
    // View sync status button
    frm.add_custom_button(__('Sync Status'), function() {
        show_sync_status(frm);
    }, __('Wix Integration'));
    
    // Test connection button (for System Managers)
    if (frappe.user.has_role('System Manager')) {
        frm.add_custom_button(__('Test Connection'), function() {
            test_wix_connection();
        }, __('Wix Integration'));
    }
    
    // View in Wix button (if product exists in Wix)
    if (frm.doc.wix_product_id) {
        frm.add_custom_button(__('View in Wix'), function() {
            view_in_wix(frm);
        }, __('Wix Integration'));
    }
}

function sync_item_to_wix(frm) {
    frappe.call({
        method: 'wix_integration.wix_integration.api.manual_sync_item',
        args: {
            item_name: frm.doc.name
        },
        btn: $('.btn-primary'),
        callback: function(r) {
            if (r.message && r.message.status === 'success') {
                frappe.show_alert({
                    message: r.message.message,
                    indicator: 'green'
                });
                
                // Refresh form to show updated sync status
                setTimeout(function() {
                    frm.reload_doc();
                }, 2000);
            }
        },
        error: function(r) {
            frappe.show_alert({
                message: 'Sync failed. Please check error logs.',
                indicator: 'red'
            });
        }
    });
}

function show_sync_status(frm) {
    frappe.call({
        method: 'wix_integration.wix_integration.api.get_sync_status',
        args: {
            item_name: frm.doc.name
        },
        callback: function(r) {
            if (r.message) {
                show_sync_status_dialog(r.message);
            }
        }
    });
}

function show_sync_status_dialog(data) {
    let dialog = new frappe.ui.Dialog({
        title: 'Wix Sync Status',
        fields: [
            {
                fieldtype: 'HTML',
                fieldname: 'status_html'
            }
        ],
        size: 'large'
    });
    
    let html = `
        <div class="wix-sync-status">
            <h4>Current Status</h4>
            <table class="table table-bordered">
                <tr>
                    <td><strong>Wix Product ID</strong></td>
                    <td>${data.item.wix_product_id || 'Not synced'}</td>
                </tr>
                <tr>
                    <td><strong>Last Sync</strong></td>
                    <td>${data.item.wix_last_sync || 'Never'}</td>
                </tr>
                <tr>
                    <td><strong>Sync Status</strong></td>
                    <td><span class="indicator ${get_status_color(data.item.wix_sync_status)}">
                        ${data.item.wix_sync_status || 'Pending'}
                    </span></td>
                </tr>
            </table>
            
            <h4>Recent Sync Logs</h4>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Status</th>
                        <th>Error</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    if (data.logs && data.logs.length > 0) {
        data.logs.forEach(function(log) {
            html += `
                <tr>
                    <td>${frappe.datetime.str_to_user(log.creation)}</td>
                    <td><span class="indicator ${get_status_color(log.status)}">
                        ${log.status}
                    </span></td>
                    <td>${log.error_message || '-'}</td>
                </tr>
            `;
        });
    } else {
        html += '<tr><td colspan="3" class="text-center">No sync logs found</td></tr>';
    }
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    dialog.fields_dict.status_html.$wrapper.html(html);
    dialog.show();
}

function get_status_color(status) {
    const colors = {
        'Success': 'green',
        'Failed': 'red',
        'Pending': 'orange',
        'Retrying': 'yellow',
        'Skipped': 'gray'
    };
    return colors[status] || 'gray';
}

function test_wix_connection() {
    frappe.call({
        method: 'wix_integration.wix_integration.api.test_wix_connection',
        callback: function(r) {
            if (r.message && r.message.success) {
                frappe.show_alert({
                    message: 'Wix connection successful!',
                    indicator: 'green'
                });
            } else {
                frappe.show_alert({
                    message: 'Connection failed: ' + (r.message.error || 'Unknown error'),
                    indicator: 'red'
                });
            }
        }
    });
}

function view_in_wix(frm) {
    if (frm.doc.wix_product_id) {
        // This would need the actual Wix store URL
        frappe.show_alert({
            message: 'Wix Product ID: ' + frm.doc.wix_product_id,
            indicator: 'blue'
        });
    }
}

function validate_wix_settings() {
    frappe.call({
        method: 'frappe.client.get',
        args: {
            doctype: 'Wix Settings',
            name: 'Wix Settings'
        },
        callback: function(r) {
            if (r.message && !r.message.enabled) {
                frappe.show_alert({
                    message: 'Wix integration is not enabled. Please enable it in Wix Settings.',
                    indicator: 'orange'
                });
            }
        }
    });
}