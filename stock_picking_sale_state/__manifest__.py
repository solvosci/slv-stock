# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Picking Sale State",
    "summary": """
        Add Picking Status field to Sale Order.
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "13.0.1.0.0",
    "category": "stock, sale",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": [
        "stock_picking_mixins",
        "sale",
    ],
    "data": [
        "views/stock_picking_sale_state.xml",
    ],
    'installable': True,
}
