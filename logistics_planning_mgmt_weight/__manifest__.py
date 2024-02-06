# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    'name': 'Logistics Planning Move Weight',
    'summary': '''
        Links Logistics Planning with Move Weight management
    ''',
    'author': 'Solvos',
    'license': 'LGPL-3',
    'version': '13.0.1.0.0',
    'category': 'stock',
    'website': 'https://github.com/solvosci/slv-stock',
    "depends": [
        "logistics_planning_purchase",
        "logistics_planning_sale",
        "stock_picking_mgmt_weight",
    ],
    "data": [
        "views/vehicle_type_views.xml",
        "views/sale_order_line_views.xml",
        "views/logistics_schedule_views.xml",
    ],
}
