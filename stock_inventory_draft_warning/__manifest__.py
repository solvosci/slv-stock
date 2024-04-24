# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Stock Inventory Draft Warning",
    "summary": """
        Adds warning that show draft stocks move in Inventory Adjustments.
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "15.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": [
        "stock_inventory",
    ],
    "data": [
        'security/ir.model.access.csv',
        "wizard/stock_quant_draft_warn_wiz_views.xml",
        ],
    'installable': True,
}
