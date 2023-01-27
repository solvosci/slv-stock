# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    'name': 'Stock Picking Move Weight Classification Images',
    'summary': '''
        Allows adding images in the classification of a weighing scale.
    ''',
    'author': 'Solvos',
    'license': 'LGPL-3',
    'version': '13.0.1.0.0',
    'category': 'stock',
    'website': 'https://github.com/solvosci/slv-stock',
    'depends': [
        'stock_picking_mgmt_weight',
        'dms',
    ],
    'data': [
        'data/dms_access_group.xml',
        'data/dms_storage.xml',
        'data/dms_directory.xml',
        'views/dms_file_views.xml',
        'views/res_config_settings_views.xml',
        'views/stock_picking_classification.xml',
        'wizards/move_weight_views.xml'
    ],
    'installable': True,
}
