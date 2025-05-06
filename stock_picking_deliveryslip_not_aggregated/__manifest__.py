# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Picking Deliveryslip Not Aggregated",
    "summary": """
        By default, the stock moves on picking reports are merged.
        Merging is now prevented only on outgoing pickings.
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "17.0.1.0.0",
    "category": "Sales/Sales",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": [
        "stock",
    ],
    "data": [
        "report/report_deliveryslip.xml",
    ],
    'installable': True,
}
