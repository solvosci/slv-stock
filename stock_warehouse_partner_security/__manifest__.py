# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Warehouse Partner Security",
    "summary": """
        Add a group with limited permissions for partners in Stock.
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "13.0.1.0.0",
    "category": "stock",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": [
        "stock"
    ],
    "data": [
        "security/stock_warehouse_partner_security.xml",
        "views/stock_warehouse_partner_security_menus.xml",
        "views/product_views.xml",
        "views/stock_picking_views.xml",
    ],
    'installable': True,
}
