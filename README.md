# Wix Integration for ERPNext

A production-grade Frappe application that enables bidirectional synchronization between Wix e-commerce stores and ERPNext. This app allows you to automatically sync products, orders, and customers between your Wix store and ERPNext system.

## ✅ **FIXED: Proper Frappe App Structure**

The app now has the correct Frappe directory structure:

```
wix_integration/
├── wix_integration/
│   ├── wix_integration/
│   │   ├── __init__.py
│   │   ├── hooks.py                    # ✅ Required
│   │   ├── modules.txt                 # ✅ Required  
│   │   ├── patches.txt                 # ✅ Required
│   │   ├── api.py                      # Core API functions
│   │   ├── install.py                  # Installation and setup
│   │   ├── utils.py                    # Utility functions
│   │   ├── tasks.py                    # Scheduled tasks
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── desktop.py              # Desktop module config
│   │   │   └── docs.py                 # Documentation config
│   │   └── public/
│   │       └── js/
│   │           └── item.js             # Client-side JavaScript
│   ├── setup.py
│   ├── requirements.txt
│   ├── README.md
│   └── LICENSE
```

## Features

### Product Synchronization ✅
- **Automatic Sync**: Products created or updated in ERPNext are automatically synced to Wix
- **Manual Sync**: Force sync individual products with a button click
- **Configurable**: Choose which products to sync with the \"Sync with Wix\" checkbox
- **Status Tracking**: Real-time sync status and detailed logs
- **Error Handling**: Robust error handling with retry mechanisms

### Order Management (Framework Ready)
- Automatic import of orders from Wix to ERPNext
- Customer creation and management
- Order status synchronization
- Inventory updates

### Webhook Support
- Secure webhook handling for real-time updates
- Signature validation for enhanced security
- Comprehensive logging of all webhook activities

### Monitoring & Logging
- Detailed integration logs with request/response data
- Sync status tracking for each item
- Health check monitoring
- Weekly sync reports
- Automatic cleanup of old logs

## Installation

### Prerequisites
- Frappe Framework v13+ or ERPNext v13+
- Python 3.6+
- Valid Wix account with API access

### Install via Frappe Bench

1. Navigate to your frappe-bench directory:
```bash
cd frappe-bench
```

2. Install the app:
```bash
bench get-app https://github.com/macrobian88/frappe_wix_integration.git
```

3. Install on your site:
```bash
bench --site [your-site] install-app wix_integration
```

4. Restart bench:
```bash
bench restart
```

### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/macrobian88/frappe_wix_integration.git
```

2. Copy to your apps directory:
```bash
cp -r frappe_wix_integration /path/to/frappe-bench/apps/wix_integration
```

3. Install the app:
```bash
bench --site [your-site] install-app wix_integration
```

## Configuration

### 1. Wix API Setup

1. Go to your [Wix Developer Console](https://dev.wix.com/)
2. Create a new app or use an existing one
3. Obtain your API credentials:
   - Site ID
   - API Key (OAuth Token)
   - Account ID

### 2. ERPNext Configuration

1. Navigate to **Wix Settings** in ERPNext
2. Enable the integration by checking **\"Enable Wix Integration\"**
3. Enter your Wix API credentials:
   - **Wix Site ID**: Your Wix site identifier
   - **Wix API Key**: Your API authentication key
   - **Wix Account ID**: Your Wix account identifier
4. Configure sync settings:
   - **Default Item Group**: Item group for products synced from Wix
   - **Default Customer Group**: Customer group for Wix customers
   - **Default Territory**: Territory for Wix customers
   - **Default Company**: Company for transactions

### 3. Product Configuration

For each product you want to sync:
1. Open the Item in ERPNext
2. Go to the **Wix Integration** section
3. Check **\"Sync with Wix\"**
4. Optionally set a custom **Wix Product Slug**
5. Save the item

## Usage

### Syncing Products to Wix

**Automatic Sync:**
- Products with \"Sync with Wix\" enabled are automatically synced when created or updated
- Sync status is displayed in the Wix Integration section

**Manual Sync:**
1. Open any Item with Wix sync enabled
2. Click **Wix Integration > Sync to Wix**
3. Monitor the sync status in real-time

**Bulk Operations:**
- Use the **Wix Integration Log** to monitor all sync activities
- View detailed request/response data for debugging

### Monitoring

**Sync Status:**
- View sync status directly on each Item
- Check **\"Last Synced\"** timestamp
- Monitor success/failure status

**Integration Logs:**
- Navigate to **Wix Integration Log** to view all activities
- Filter by operation type, status, or date range
- View detailed error messages and execution times

**Health Checks:**
- Use **Test Connection** button to verify Wix API connectivity
- Automatic health checks run daily
- System managers receive notifications for connection issues

## API Reference

### Whitelisted Methods

#### `wix_integration.wix_integration.api.manual_sync_item(item_name)`
Manually sync a specific item to Wix.

**Parameters:**
- `item_name`: Name of the Item document to sync

**Returns:**
```json
{
    \"message\": \"Item sync initiated successfully\",
    \"status\": \"success\"
}
```

#### `wix_integration.wix_integration.api.test_wix_connection()`
Test connectivity to Wix API.

**Returns:**
```json
{
    \"success\": true,
    \"message\": \"Connection successful\"
}
```

#### `wix_integration.wix_integration.api.get_sync_status(item_name)`
Get detailed sync status for an item.

**Parameters:**
- `item_name`: Name of the Item document

**Returns:**
```json
{
    \"item\": {
        \"wix_product_id\": \"abc123\",
        \"wix_last_sync\": \"2023-10-15 14:30:00\",
        \"wix_sync_status\": \"Success\"
    },
    \"logs\": [...]
}
```

## Troubleshooting

### Common Issues

**1. \"Wix Settings not found\" Error**
- Ensure the app is properly installed with correct directory structure
- Check if Wix Settings document exists
- Try reinstalling the app

**2. \"Invalid API credentials\" Error**
- Verify all API credentials in Wix Settings
- Ensure the API key has necessary permissions
- Test connection using the \"Test Connection\" button

**3. Products not syncing**
- Check if \"Sync with Wix\" is enabled on the item
- Verify Wix Integration is enabled in settings
- Check integration logs for error details

**4. Directory structure errors**
- Ensure you have the proper nested directory structure
- The app should be in `apps/wix_integration/wix_integration/wix_integration/`
- All required files (`hooks.py`, `patches.txt`, `modules.txt`) must be present

## Technical Implementation

### Wix API Integration
- ✅ **Wix Catalog V3 API** support
- ✅ **Product creation/update** with full metadata
- ✅ **Media upload** and image handling
- ✅ **Variant support** and pricing
- ✅ **Proper error handling** and rate limiting

### ERPNext Integration
- ✅ **Document hooks** for automatic sync
- ✅ **Custom fields** without modifying core
- ✅ **Permission integration** with ERPNext roles
- ✅ **Multi-company support** ready

### Data Mapping
- ✅ **Item to Product** mapping with validation
- ✅ **Price synchronization** with currency handling
- ✅ **Image/media** synchronization
- ✅ **Stock status** and availability tracking

## Development

### Setting up Development Environment

1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/frappe_wix_integration.git
```

3. Install in development mode:
```bash
bench get-app /path/to/frappe_wix_integration --skip-assets
bench --site [site-name] install-app wix_integration
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Ensure all tests pass
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [Wiki](https://github.com/macrobian88/frappe_wix_integration/wiki)
- **Issues**: [GitHub Issues](https://github.com/macrobian88/frappe_wix_integration/issues)
- **Discussions**: [GitHub Discussions](https://github.com/macrobian88/frappe_wix_integration/discussions)

## Quick Start Checklist

- [ ] Clone/Install the application from GitHub
- [ ] Get Wix API credentials (Site ID, API Key, Account ID)
- [ ] Configure credentials in **Wix Settings**
- [ ] Test connection using built-in test function
- [ ] Enable sync on your first Item
- [ ] Monitor progress through **Wix Integration Log**

---

**Built with ❤️ for the Frappe/ERPNext community**

The application is now production-ready with proper Frappe app structure, robust error handling, comprehensive logging, and all necessary validations for a secure and reliable Wix-ERPNext integration.
