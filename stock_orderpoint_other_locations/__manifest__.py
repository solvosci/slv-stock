# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Reordering Rules - adds extra locations for procurement calculation",
    "summary": """
        Adds new locations to a reordering rule, so it's possible to take their stock
        in account when setting quantity to be ordered by rule
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "15.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock"],
    "data": ["views/stock_warehouse_orderpoint_views.xml"],
    'installable': True,
}
