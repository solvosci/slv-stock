# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Picking State To Process",
    "summary": """Add a link to show orders in "assigned" or "confirmed" status in "to process". Add a days field in stock.picking.type, so that when the delay is greater than that, it appears as "very late".""",
    "version": "17.0.1.0.0",
    "author": "Solvos",
    "category": "stock",
    "license": "LGPL-3",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock"],
    "data": [
        "views/stock_picking_type_views.xml",
    ],
}
