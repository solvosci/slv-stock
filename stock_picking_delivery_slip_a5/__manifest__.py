# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Picking Delivery Slip A5",
    "summary": """
        Adds report in A5 format, and customizes delivery slip with basic layout and contact information.
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "16.0.1.0.1",
    "category": "Operations/Stock",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock"],
    "data": [
        "data/report_paperformat_data.xml",
        "report/stock_picking_report_a5.xml",
        "report/stock_picking_template_a5.xml",

    ],
    "installable": True,
}
