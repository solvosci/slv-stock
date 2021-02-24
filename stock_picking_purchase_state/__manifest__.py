# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Picking Purchase State",
    "summary": """
        Add Picking Status field to Purchase Order.
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "13.0.1.0.0",
    "category": "stock, purchase",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": [
        "stock_picking_mixins",
        "purchase",
    ],
    "data": [
        "views/stock_picking_purchase_state.xml",
    ],
    'installable': True,
}
