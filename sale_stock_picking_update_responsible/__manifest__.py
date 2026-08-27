# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Sale Stock Picking Update Responsible",
    "summary": """
        Update responsible when user print picking operations.
        Now only sales administrators and picking preparer can modify the responsible.
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "17.0.1.0.0",
    "category": "Stock",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": [
        "sale_stock",
    ],
    "data": [
        "security/sale_stock_picking_update_responsible.xml",
        "views/stock_picking_views.xml",
    ],
    'installable': True,
}
