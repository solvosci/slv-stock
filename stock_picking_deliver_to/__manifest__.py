# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Picking Deliver TO",
    "summary": """
        Add deliver_to text field in stock picking and reports
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "16.0.0.0.0",
    "category": "Stock",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock"],
    "data": [
        "views/stock_picking.xml",
        "reports/stock_picking.xml",
    ],
    "installable": True,
}
