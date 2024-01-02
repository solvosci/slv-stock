# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    'name': 'Logistics Planning Invoicing',
    'summary': '''
        Links Logistics Planning with Invoicing
    ''',
    'author': 'Solvos',
    'license': 'LGPL-3',
    'version': '13.0.1.0.0',
    'category': 'stock',
    'website': 'https://github.com/solvosci/slv-stock',
    'depends': [
        'account',
        'logistics_planning_base',
    ],
    'data': [
        'views/account_move_views.xml',
        'views/logistics_schedule_views.xml',
        'views/res_config_settings_views.xml',
        'wizards/logistics_schedule_account_move_wizard_views.xml'
    ],
    'installable': True,
}
