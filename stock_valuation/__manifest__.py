# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Valuation",
    "summary": """
        Creates a brand new valuation method by warehouse and date history
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "13.0.1.0.0",
    "category": "stock",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": [
        "sale_stock",
        "purchase_stock",
        "stock_move_action_done_custdate_val",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/stock_valuation_security.xml",
        "views/stock_valuation_template.xml",
        "views/product_category_views.xml",
        "views/stock_valuation_layer_views.xml",
        "views/product_history_average_price_views.xml",
        "views/product_average_price_views.xml",
        "views/product_product_views.xml",
        "report/product_average_price_date_views.xml",
        "report/product_average_price_date_wizard_views.xml",
    ],
    'installable': True,
}
