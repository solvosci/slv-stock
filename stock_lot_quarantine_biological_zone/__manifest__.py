# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Stock Lot Quarantine Biological Zone",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "description": "Lets the receiving line declare the biological "
                "classification zone a lot was captured from, alongside "
                "its capture zone, so each lot's origin resolves to a "
                "single, unambiguous sanitary classification.",
    "author": "Solvos",
    "license": "LGPL-3",
    "depends": ["stock_lot_quarantine_capture_zone", "stock_intecmar_biological_zone"],
    "data": [
        "views/stock_move_line_views.xml",
        "views/stock_lot_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
