# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Stock INTECMAR Capture Zone",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "description": "Models INTECMAR capture zones, product "
                "types and their administrative status history, with "
                "automatic sync against the official 'EstadoZonasBiotoxinas' "
                "API.",
    "author": "Solvos",
    "license": "LGPL-3",
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "data/capture_zone_state_mapping_data.xml",
        "views/product_views.xml",
        "views/capture_zone_views.xml",
        "views/capture_product_type_views.xml",
        "views/capture_zone_state_mapping_views.xml",
        "views/capture_zone_status_history_views.xml",
        "views/stock_intecmar_capture_zone_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
