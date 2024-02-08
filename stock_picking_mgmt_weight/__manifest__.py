# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Picking Move Weight",
    "summary": """
        Weight and classification improvements for waste sector
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "13.0.1.23.1",
    "category": "stock",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": [
        "purchase_stock",
        "vehicle",
        "scale",
        "base_waste_mgmt_data",
        "web",
        "purchase_discount",
        "purchase_order_internal_note",
        "camera",
        "purchase_order_partner_user",
        "purchase_order_line_menu",
        # "asm",
        "purchase_pricelist_slv",
        "stock_valuation",
        "account_payment_term_base_date",
        "sale_stock",
        "sale_order_line_menu",
        "base_model_code_mixin",
    ],
    "data": [
        "security/stock_picking_mgmt_weight_security.xml",
        "security/ir.model.access.csv",
        "report/stock_picking_tag_template.xml",
        "report/stock_picking_tag_report.xml",
        "views/assets.xml",
        "views/stock_move_views.xml",
        "wizards/move_line_weight_views.xml",
        "wizards/move_weight_views.xml",
        "wizards/sale_order_confirm_views.xml",
        "views/stock_picking_type.xml",
        "views/stock_picking_views.xml",
        "views/res_partner_views.xml",
        "views/vehicle_vehicle_views.xml",
        "views/purchase_order_views.xml",
        "views/purchase_order_line_views.xml",
        "views/res_config_settings_views.xml",
        "views/stock_picking_mgmt_weight_menus.xml",
        "views/stock_picking_classification.xml",
        "views/product_product_views.xml",
        "views/product_template_views.xml",
        # "report/report_stock_expected_quantity.xml",
        "views/sale_order_views.xml",
        "views/sale_order_line_views.xml",
        "views/shipping_resource_views.xml",
        "views/supply_condition_views.xml",
        "views/vehicle_type_views.xml",
    ],
    "qweb": [
        "static/src/xml/iot_weight.xml",
        # "static/src/xml/iot_asm_field.xml",
        "static/src/xml/iot_camera_field.xml",
        "static/src/xml/iot_weight_viewer.xml",
    ],
    "post_init_hook": "post_init_hook",
    'installable': True,
}
