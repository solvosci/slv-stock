# -*- coding: utf-8 -*-
{
    "name": "Stock Picking Lock Indicator",
    "version": "17.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Visualize the lock status of transfers (stock.picking)",
    "description": """
Stock Picking Lock Indicator
=============================

Odoo already stores whether a transfer (stock.picking) is locked in the
native ``is_locked`` field, but that information is only visible as a
button on the form view. This module makes the lock status visible in
three places, without touching any other view:

* **Form view**: a "Locked" ribbon badge in the top-right corner, the
  same way it is displayed on locked Sales Orders.
* **Search view**: a "Locked" filter to quickly find locked transfers.
* **List view**: a small padlock icon to the left of the transfer
  reference (the "name" field), shown only when the transfer is locked.

No model changes are required: the module only adds view inheritances
and a small, read-only widget to render the icon in the list view.
""",
    "author": "Your Company",
    "license": "LGPL-3",
    "website": "https://www.example.com",
    "depends": ["stock"],
    "data": [
        "views/stock_picking_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "stock_picking_lock_indicator/static/src/js/lock_indicator_field.js",
            "stock_picking_lock_indicator/static/src/xml/lock_indicator_field.xml",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
