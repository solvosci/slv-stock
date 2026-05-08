# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Stock Product Label Manufacturer",
    "summary": """
        Links 'product_manufacturer' and 'stock_product_label'
        to add the Manufacturer Product Code to the label product
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "15.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock_product_label", "product_manufacturer"],
    "data": [
        "report/label_template.xml"
    ],
    'installable': True,
}
