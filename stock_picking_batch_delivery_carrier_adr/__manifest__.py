# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Picking Batch Delivery Carrier ADR",
    "summary": """
        Enhances Odoo's batch picking process with integrated ADR compliance and carrier support.
        This module allows you to manage dangerous goods (ADR) information directly within picking batches,
        generate official ADR consignment notes for transport, and leverages delivery_carrier_partner
        to automatically use relevant carrier information from the partner.
    """,
    "version": "17.0.1.0.0",
    "author": "Solvos",
    "category": "stock",
    "license": "AGPL-3",
    "website": "https://github.com/solvosci/slv-stock",
    "depends":[
        "stock_picking_batch_delivery_carrier",
        "l10n_eu_product_adr_local",
        "delivery_carrier_partner",
        ],
    "data": [
        "views/stock_picking_views.xml",
        "views/stock_picking_batch_views.xml",
        "reports/stock_picking_batch_report.xml",
        "reports/stock_picking_batch_template.xml"
    ],
    'installable': True,
}
