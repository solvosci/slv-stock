# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Barcodes GS1 Secondary Unit",
    "summary": """
        Adds Secondary Unit in Stock Barcodes GS1 implementation
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "14.0.1.1.0",
    "category": "Stock",
    "website": "",
    "depends": [
        "stock_barcodes_gs1",
        "stock_secondary_unit"
    ],
    "data": [
        "wizard/stock_barcodes_read_picking_views.xml",
    ],
    "installable": True,
}
