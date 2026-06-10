# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Product Label",
    "summary": """
        Adds a new report that prints product labels.
        It displays the barcode and the lot or serial number, if it has.
        It also generates an MH10 Datamatrix QR code that can be scanned to retrieve the displayed data.

        This report can be printed from the products and their variants, the delivery note, and the inventory report.

        To install this addon, the python dependency 'pylibdmtx' is required.
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "15.0.1.1.0",
    "category": "Inventory/Inventory",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template_views.xml",
        "views/product_product_views.xml",
        "views/product_category_views.xml",
        "views/product_label_template_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_quant_views.xml",
        "wizard/product_label_wizard_views.xml",
        "report/label_report.xml",
        "report/label_template.xml"
    ],
    'installable': True,
    "external_dependencies": {"python": ["pylibdmtx"]},
}
