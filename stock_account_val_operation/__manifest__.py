# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Account Valuation Operation",
    "summary": """
        Adds two fields on account.move.line (val_operation, val_operation_origin) to easy visualization
        of it's original type operation (incoming, outgoing, in_return, out_return, inv_adjust, scrap) and
        the name of the operation itself.
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "15.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": [
        "stock_account",
    ],
    "data": [
        "views/account_move_views.xml"
    ],
    'installable': True,
    "pre_init_hook": "pre_init_hook",
}
