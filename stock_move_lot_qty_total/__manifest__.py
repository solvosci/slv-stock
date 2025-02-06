# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Move - Complete Stock Quantity for Lot deliveries",
    "summary": """
        Enables configuring desired products tracked by lot to be delivered
        using current available stock
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "15.0.1.0.2",
    "category": "Inventory/Inventory",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock"],
    "data": [
        "views/product_template_views.xml",
        "views/stock_picking_views.xml",
    ],
    'installable': True,
}
