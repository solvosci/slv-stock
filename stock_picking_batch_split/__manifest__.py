# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)
{
    "name": "Stock Picking Batch Split",
    "summary": """
        Adds split_picking functionalities from picking_batch
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "14.0.1.1.0",
    "category": "Stock",
    "website": "",
    "depends": [
        "stock_picking_batch_extended",
        "stock_split_picking",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking_views.xml",
        "views/stock_picking_batch_views.xml",
        "wizards/stock_picking_batch_split_views.xml",
    ],
    "installable": True,
}
