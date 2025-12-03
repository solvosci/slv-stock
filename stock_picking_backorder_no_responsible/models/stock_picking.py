# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model_create_multi
    def create(self, vals_list):
        context = self.env.context
        for vals in vals_list:
            picking_type_id = vals.get('picking_type_id')
            create_backorder = False

            if picking_type_id:
                picking_type = self.env['stock.picking.type'].browse(picking_type_id)
                create_backorder = picking_type.create_backorder == 'always'

            if (
                (context.get('skip_backorder') and not context.get('cancel_backorder'))
                or create_backorder
            ):
                vals['user_id'] = False
        return super(StockPicking, self).create(vals_list)
