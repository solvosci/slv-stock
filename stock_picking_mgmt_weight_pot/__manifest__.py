# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Picking Move Weight - Purchase Order Type link",
    "summary": """
        Adds Purchase Order Type functionality to Weight and classification
        improvements for waste sector
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "13.0.1.0.0",
    "category": "stock",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": [
        "stock_picking_mgmt_weight",
        "purchase_order_type_dashboard",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking_type_views.xml",
        "views/purchase_order_views.xml",
        "views/purchase_order_type_views.xml",
    ],
    'installable': True,
}
