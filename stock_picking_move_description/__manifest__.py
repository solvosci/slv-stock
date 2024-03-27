# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Picking - Move descriptions",
    "summary": """
        Adds required stock move descriptions within pickings
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "16.0.2.0.0",
    "category": "Inventory/Inventory",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock"],
    "data": [ 
        "security/stock_picking_move_description_security.xml",      
        "views/stock_picking_views.xml",
        "views/res_config_settings.xml",
        "report/stock_picking_templates.xml",
    ],
    'installable': True,
}
