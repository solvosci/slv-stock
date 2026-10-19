# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Stock Picking Report 80mm",
    "summary": """
        Adds new report in Stock Picking with Ticket format (80mm)
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "15.0.1.0.0",
    "category": "Stock",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock"],
    "data": [
        "reports/stock_picking_report_80mm_template.xml",
        "reports/stock_picking_report_80mm_report.xml",
        "views/stock_picking_views.xml",
    ],
    "installable": True,
}
