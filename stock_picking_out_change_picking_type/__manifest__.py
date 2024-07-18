# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Pickings - Change Picking Operation",
    "summary": """
        For outgoing picking documents, enables changing picking operation
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "13.0.1.0.0",
    "category": "stock",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock_move_change_source_location"],
    "data": [
        "wizards/stock_picking_out_change_picking_type_views.xml",
        "views/stock_picking_views.xml",
    ],
}
