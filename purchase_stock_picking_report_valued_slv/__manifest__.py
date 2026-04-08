# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Valued Picking Report",
    "summary": "Adding Valued Picking on Delivery Slip report",
    "version": "13.0.1.1.0",
    "author": "Solvos, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-reporting",
    "category": "Warehouse Management",
    "license": "AGPL-3",
    "depends": [
        "stock_picking_report_valued",
        "purchase_discount",
        "stock"
    ],
    "data": ["report/purchase_stock_picking_report_valued.xml"],
    "installable": True,
}
