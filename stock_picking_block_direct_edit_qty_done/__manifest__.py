# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Picking Block Direct Edit Qty Done",
    "summary": """
        Be able to prevent direct editing of the done quantity on pickings
        By default, allow this only for outgoing pickings.
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "17.0.1.0.0",
    "category": "Warehouse",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock"],
    "data": [
        "views/stock_picking_type_views.xml",
        "views/stock_picking_views.xml",
    ],
    'installable': True,

}
