# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Authorized Scrap Stock Users",
    "summary": """
        Add authorized scrap stock users
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "13.0.1.0.0",
    "category": "stock",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock"],
    "data": [
        'security/stock_scrap_security.xml',
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
}
