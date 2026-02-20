# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Barcodes Datamatrix MH10",
    "summary": """
        Scan ANSI MH10 Datamatrix barcodes in the Stock Barcode Wizard and process them with GS separators using the following configurable fields:
            - Product (1P)
            - Lot (1T)
            - Quantity (Q)
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "15.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock_barcodes"],
    "data": [
        "views/stock_barcodes_option_group_views.xml",
        "wizard/stock_barcodes_read_picking_views.xml"
    ],
    "installable": True,
}
