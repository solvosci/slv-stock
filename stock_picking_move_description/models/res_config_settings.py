# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_picking_report_show_prod = fields.Boolean(string="Delivery Slip: show product column", implied_group="stock_picking_move_description.group_picking_report_show_prod")
