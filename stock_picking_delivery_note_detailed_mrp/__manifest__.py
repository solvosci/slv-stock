# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    'name': 'Stock Picking Delivery Note - Detailed MRP Components',
    'summary': 'It adds new report to the delivery note that expands'
        ' the information on manufacturing products including it\'s'
        'components and quantities used based on the manufacturing order.',
    'version': '15.0.1.0.0',
    'category': 'Stock',
    'license': 'LGPL-3',
    'author': 'Solvos',
    'website': 'https://github.com/solvosci/slv-stock',
    'depends': [
        'mrp',
    ],
    'data': [
        'report/report_deliveryslip_detailed_mrp.xml',
    ],
    'installable': True,
}
