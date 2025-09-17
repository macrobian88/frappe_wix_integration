# -*- coding: utf-8 -*-
from __future__ import unicode_literals

source_link = "https://github.com/macrobian88/frappe_wix_integration"
docs_base_url = "https://github.com/macrobian88/frappe_wix_integration/wiki"
headline = "Production-grade Frappe application for bidirectional sync between Wix e-commerce and ERPNext"
sub_heading = "Sync products, orders, and customers between Wix and ERPNext"

def get_context(context):
    context.brand_html = "Wix Integration"
    context.top_bar_items = [
        {"label": "User Guide", "url": docs_base_url + "/User-Guide", "right": 1},
        {"label": "API Documentation", "url": docs_base_url + "/API-Documentation", "right": 1},
        {"label": "GitHub", "url": source_link, "right": 1}
    ]
