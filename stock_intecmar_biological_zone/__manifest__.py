# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Stock INTECMAR Biological Zone",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "description": "Syncs the Intecmar biological sanitary "
                "classification (A/B/C) per capture zone and product type.",
    "author": "Solvos",
    "license": "LGPL-3",
    "depends": ["stock_intecmar_capture_zone"],
    "data": [
        "security/ir.model.access.csv",
        "views/biological_zone_views.xml",
        "views/capture_zone_views.xml",
        "views/res_config_settings_views.xml",
        "views/stock_intecmar_biological_zone_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
