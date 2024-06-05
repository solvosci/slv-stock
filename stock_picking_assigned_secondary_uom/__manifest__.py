# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)
{
    "name": "Stock Picking Assigned Secondary UoM",
    "summary": """
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "14.0.1.0.0",
    "category": "Stock",
    "website": "",
    "depends": [
        "stock_picking_assigned",
        "fcd_purchase_order",
        "purchase_stock_secondary_unit"
    ],
    "data": [
        "reports/stock_picking_assigned_template.xml",
        "views/stock_picking_assign_history_views.xml",
        "wizard/sp_assigned_wizard_views.xml",
    ],
    "installable": True,
}
