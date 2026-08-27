# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_user_id_editable = fields.Boolean(
        compute="_compute_is_user_id_editable",
    )

    @api.depends("state", "sale_id")
    def _compute_is_user_id_editable(self):
        for picking in self:
            if picking.state in ['done', 'cancel']:
                picking.is_user_id_editable = False
            elif picking.sale_id:
                picking.is_user_id_editable = (self.env.user.has_group("sale_stock_picking_update_responsible.group_sale_stock_picking_preparer")
                or self.env.user.has_group("sales_team.group_sale_manager"))
            else:
                picking.is_user_id_editable = True
