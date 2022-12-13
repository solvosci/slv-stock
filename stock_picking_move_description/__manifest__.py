# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Picking - Move descriptions",
    "summary": """
        Adds required stock move descriptions within pickings
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "15.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock"],
    "data": [        
        "views/stock_picking_views.xml",
        "report/stock_picking_templates.xml",
    ],
    'installable': True,
}
