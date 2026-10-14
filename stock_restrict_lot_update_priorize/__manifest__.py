# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Stock Restrict Lot Domain - priorize lot, even if there are existing reservations",
    "summary": """
        Only apply lot restriction on products in a domain - and enables reservation steals
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "15.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock_restrict_lot_update"],
    "data": [
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml"
    ],
    'installable': True,
}
