# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Sale Purchase according declared stock",
    "summary": """
        Create purchase orders when confirming sales orders 
        based on declared stock in suppliers warehouses
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "13.0.1.0.0",
    "category": "stock",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": [
        "stock",
        "sale_purchase"
    ],
    "data": [
    ],
    'installable': True,
}