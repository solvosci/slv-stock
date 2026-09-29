# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('backorder_id'):
                vals['user_id'] = False
        return super(StockPicking, self).create(vals_list)
