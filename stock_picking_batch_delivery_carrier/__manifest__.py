# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Stock Picking Batch Delivery Carrier",
    "summary": """
        This module introduces a mandatory delivery method (carrier_id)
        field on stock.picking.batch. It ensures that only pickings with
        the same delivery method can be grouped in a batch,
        and blocks the addition of pickings without an assigned carrier.
    """,
    "version": "17.0.1.0.0",
    "author": "Solvos",
    "category": "stock",
    "license": "LGPL-3",
    "website": "https://github.com/solvosci/slv-stock",
    "depends":[
        "delivery_stock_picking_batch",
        ],
    "data": [
        "views/stock_picking_batch_views.xml",
        "wizard/stock_picking_to_batch_views.xml",
    ],
}
