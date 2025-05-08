# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Moves - Advanced S/N reservation",
    "summary": """
        Enables s/n secure reservation in moves, preventing
        undesired situations when a s/n is manually assigned
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "15.0.1.1.0",
    "category": "Inventory/Inventory",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock"],
    "data": [
        "security/stock_product_sn_reservation.xml",
        "security/ir.model.access.csv", 
        "views/stock_picking_views.xml",
        "views/stock_move_views.xml",
        "views/stock_move_line_views.xml",
        "wizards/stock_move_line_add_sn_wizard_views.xml",
        "wizards/stock_move_line_exchange_sn_wizard_views.xml",        
    ],
}
