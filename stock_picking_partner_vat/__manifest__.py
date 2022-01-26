# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Picking - Partner/Customer VAT",
    "summary": """
        Adds customer/vendor VAT to picking.
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "13.0.1.1.0",
    "category": "Warehouse",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock"],
    "data": [
        "views/report_delivery_document.xml",
        "views/stock_picking_views.xml"
    ],
    'installable': True,
}
