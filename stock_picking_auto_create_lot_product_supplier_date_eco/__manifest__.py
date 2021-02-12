# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Picking Auto Create Lot Custom Format",
    "summary": """
        Adds new format sequence to add lot automatic. 
        Product_DefaultCode + Partner_Ref + CurrentDate + 1/0(ECO)
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "13.0.1.1.0",
    "category": "stock",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": [
        "stock_picking_auto_create_lot"
    ],
    "data": [
        "views/product_views.xml",
        "views/partner_views.xml"
    ],
    'installable': True,
}
