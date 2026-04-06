# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)
{
    "name": "Stock Picking Assigned",
    "summary": """
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "14.0.1.2.0",
    "category": "Stock",
    "website": "",
    "depends": [
        "stock"
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "data/report_paperformat_data.xml",
        "views/stock_picking_assigned_menu.xml",
        "reports/stock_picking_assigned_report.xml",
        "reports/stock_picking_assigned_template.xml",
        "views/stock_picking_views.xml",
        "views/stock_production_lot_views.xml",
        "views/res_partner_views.xml",
        "views/stock_picking_assign_history_views.xml",
        "wizard/sp_assigned_wizard_views.xml",
    ],
    "installable": True,
}
