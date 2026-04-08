# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Move Line Description According Sale Order Line",
    "summary": """
        Keep the description of a stock move updated according to the description of the assigned sale order line
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "13.0.1.0.0",
    "category": "stock",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": [
        "sale_stock"
    ],
    "data": [
        "report/report_deliveryslip.xml"
    ],
    'installable': True,
}
