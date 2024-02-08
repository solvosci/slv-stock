# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    'name': 'Logistics Planning Purchase',
    'summary': '''
        Links Logistics Planning with Purchases
    ''',
    'author': 'Solvos',
    'license': 'LGPL-3',
    'version': '13.0.1.0.0',
    'category': 'stock',
    'website': 'https://github.com/solvosci/slv-stock',
    "depends": [
        "purchase_stock",
        "logistics_planning_invoicing",
    ],
    "data": [
        "views/account_incoterms_views.xml",
        "views/logistics_schedule_views.xml",
        "views/purchase_order_views.xml",
        "wizards/logistics_schedule_purchase_add_wizard_views.xml",
    ],
}
