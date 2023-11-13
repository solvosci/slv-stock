# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "FCD",
    "summary": """
        Adds new models for fishing capture document
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "14.0.1.4.0",
    "category": "Stock",
    "website": "",
    "depends": [
        "stock",
        "product_expiry",
        "customer_product_code_inherit",
        "quality_control_stock_oca"
    ],
    "data": [
        'data/fcd_fao_zone.xml',
        'data/fcd_fao_subzone.xml',
        'data/fcd_fishing_gear.xml',
        'data/fcd_presentation.xml',
        'data/fcd_production_method.xml',
        'data/fcd_ship.xml',
        'data/fcd_qc_inspections.xml',
        'data/res_country.xml',
        'security/fcd_security.xml',
        'security/ir.model.access.csv',
        'views/product_product_views.xml',
        'views/product_template_views.xml',
        'views/qc_inspection_views.xml',
        'views/fcd_document_views.xml',
        'views/fcd_document_line_views.xml',
        'views/res_partner_views.xml',
        'views/stock_production_lot_views.xml',
        'views/fcd_fao_zone_views.xml',
        'views/fcd_fao_subzone_views.xml',
        'views/fcd_fishing_gear_views.xml',
        'views/fcd_presentation_views.xml',
        'views/fcd_production_method_views.xml',
        'views/fcd_ship_views.xml',
        'views/fcd_menu.xml',
    ],
    'installable': True,
}
