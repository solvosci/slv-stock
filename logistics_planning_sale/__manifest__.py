# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    'name': 'Logistics Planning Sale',
    'summary': '''
        Links Logistics Planning with Sales
    ''',
    'author': 'Solvos',
    'license': 'LGPL-3',
    'version': '13.0.1.0.0',
    'category': 'stock',
    'website': 'https://github.com/solvosci/slv-stock',
    "depends": [
        "sale_stock",
        "logistics_planning_invoicing",
    ],
    "data": [
        "views/logistics_schedule_views.xml",
        "views/sale_order_views.xml",
        "wizards/logistics_schedule_sale_add_wizard_views.xml",
    ],
}
