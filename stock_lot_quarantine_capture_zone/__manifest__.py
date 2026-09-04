# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Stock Lot Quarantine Capture Zone",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "description": "Blocks lots captured from administratively closed "
                "(toxin) production zones, with manual, reviewed release.",
    "author": "Solvos",
    "license": "LGPL-3",
    "depends": ["stock_lot_quarantine", "stock_intecmar_capture_zone"],
    "data": [
        "security/ir.model.access.csv",
        "security/lot_capture_zone_origin_security.xml",
        "views/stock_move_line_views.xml",
        "views/stock_lot_views.xml",
        "views/stock_lot_quarantine_capture_zone_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
