# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Stock Lot Quarantine",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Per-lot purification hold for purifiable products, held in a "
                "quarantine bin until released. Which operations may move a "
                "blocked lot is configurable.",
    "author": "Solvos",
    "license": "LGPL-3",
    "depends": ["stock"],
    "data": [
        "security/stock_lot_quarantine_security.xml",
        "data/ir_cron_data.xml",
        "views/product_views.xml",
        "views/stock_warehouse_views.xml",
        "views/stock_location_views.xml",
        "views/stock_picking_type_views.xml",
        "views/stock_lot_views.xml",
        "views/stock_lot_quarantine_views.xml",
        "views/stock_move_line_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
