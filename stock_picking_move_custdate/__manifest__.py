# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Move Custom Date when done - link with pickings",
    "summary": """
        Passes custom effective planned date to stock moves when are done
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "15.0.2.0.0",
    "category": "Inventory/Inventory",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock_move_action_done_custdate"],
    "data": ["views/stock_picking_views.xml"],
    'installable': True,
}
