# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Move Line Partner Tree",
    "summary": """
        Adds new column 'Partner' to stock move lines
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "14.0.1.0.0",
    "category": "Inventory",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock"],
    "data": [
        "views/stock_move_line_views.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    'installable': True,
}
