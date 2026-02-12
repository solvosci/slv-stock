# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Lot Available At Date",
    "summary": """
        Adds lot finder with quantity at a given date
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "17.0.1.0.0",
    "category": "Warehouse",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "report/report_stock_lot_at_date_views.xml",
        "report/report_stock_lot_at_date_wizard_views.xml",
        "views/stock_lot_available_at_date_menus.xml",
    ],
    'installable': True,
}
