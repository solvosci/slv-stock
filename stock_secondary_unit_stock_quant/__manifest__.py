# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Stock Secondary Unit - Stock Quant addition",
    "summary": """
        Adds secondary unit quants to Stock Quant and Lot/Serial Numbers
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "14.0.1.0.0",
    "category": "Inventory",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock_secondary_unit"],
    "data": [
        "views/stock_quant_views.xml",
        "views/stock_production_lot_views.xml",
    ],
    'installable': True,
}
