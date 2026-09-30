# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Stock Barcodes Detailed Operations All",
    "summary": """
        Show every detailed operation line of the picking in the barcode
        wizard
    """,
    "author": "Solvos, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "version": "17.0.1.0.0",
    "category": "Extra Tools",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "depends": ["stock_barcodes"],
    "data": [
        "wizard/stock_barcodes_read_picking_views.xml",
    ],
    "installable": True,
}
