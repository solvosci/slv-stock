# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)
{
    "name": "Stock Barcodes Advanced",
    "summary": """
        Adds some improvements:
            - Refresh fields after scan
            - Update quantity pending after scan
            - Change barcode button on stock.picking to only confirmed ones
            - Adds qty demand and done in kanban top
            - Adds new name_get with "LOT (QTY unit)"
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "14.0.1.3.0",
    "category": "Stock",
    "website": "",
    "depends": [
        "stock_barcodes"
    ],
    "data": [
        "views/stock_picking_views.xml",
        "wizard/stock_barcodes_read_picking_views.xml",
    ],
    "installable": True,
}
