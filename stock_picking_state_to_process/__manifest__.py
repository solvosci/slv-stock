# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Picking State To Process",
    "summary": """Changes the state of the picking to 'To process (Stock Pending)' when is 'waiting' and 'To process' when is 'assigned' or 'confirmed'.
The button in 'Delivery Orders' shows all 'To Process' pickings.""",
    "version": "17.0.1.0.0",
    "author": "Solvos",
    "category": "stock",
    "license": "LGPL-3",
    "website": "https://github.com/solvosci/slv-sale",
    "depends": ["stock"],
    "data": [
        "views/stock_picking_type_views.xml",
    ],
}
