# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Stock Move Custom Date when done - link with OCA's Inventory",
    "summary": """
        Passes stock inventory date to stock moves when are done
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "15.0.2.0.0",
    "category": "Inventory/Inventory",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": [
        "stock_move_action_done_custdate",
        "stock_inventory",
    ],
    "data": ["views/stock_quant_views.xml"],
    'installable': True,
}
