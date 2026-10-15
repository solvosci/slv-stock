# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Stock Sanitary Guide",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Official sanitary guide (Documento de orixe) attached to receipts.",
    "author": "Solvos",
    "license": "LGPL-3",
    "depends": ["stock_lot_quarantine_biological_zone"],
    "data": [
        "security/stock_sanitary_guide_security.xml",
        "security/ir.model.access.csv",
        "data/capture_zone_state_mapping_data.xml",
        "data/ir_cron_data.xml",
        "views/sanitary_guide_views.xml",
        "views/res_config_settings_views.xml",
        "wizards/sanitary_guide_lookup_wizard_views.xml",
        "views/stock_move_line_views.xml",
        "views/stock_lot_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
