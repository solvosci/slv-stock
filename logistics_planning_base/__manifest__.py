# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    'name': 'Logistics Planning Base',
    'summary': '''
        Base addon for logistics management
    ''',
    'author': 'Solvos',
    'license': 'LGPL-3',
    'version': '13.0.1.0.0',
    'category': 'stock',
    'website': 'https://github.com/solvosci/slv-stock',
    'depends': ["stock", "base_view_inheritance_extension"],
    'data': [
        'security/logistics_planning_base_security.xml',
        'security/ir.model.access.csv',
        'views/logistics_schedule_views.xml',
        'views/logistics_schedule_menu.xml',
        'views/stock_picking_views.xml',
        'views/stock_move_views.xml',
        'views/res_config_settings_views.xml'
    ],
    'installable': True,
    "application": True,
    'post_init_hook': 'post_init_hook',
}
