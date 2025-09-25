# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Stock Secondary Unit Backorder",
    "summary": """
        This is a temporary addon that is needed meanwhile base 'stock_secondary_unit' addon is not fixed.
        Originally, when creating a partial delivery, the '_compute_secondary_uom_qty' function should be executed,
        recalculating the secondary quantity, but it does not.
        With this temporary solution, every time the partial delivery is created,
        the function is forced to be executed for all the lines on the delivery note.
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "17.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock_secondary_unit"],
    'installable': True,
}
