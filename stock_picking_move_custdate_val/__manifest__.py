# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Move Custom Date when done - link with pickings & valuations",
    "summary": """
        When passing picking scheduled date to stock moves when are done,
        accounting data (moves and SVLs) are also updated
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "15.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": [
        "stock_picking_move_custdate",
        "stock_move_action_done_custdate_val",
    ],
    'installable': True,
}
