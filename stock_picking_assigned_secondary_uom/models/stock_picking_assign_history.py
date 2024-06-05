# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, fields, api, _



class StockPickingAssignHistory(models.Model):
    _inherit = "stock.picking.assign.history"
    _description = "stock.picking.assign.history"

    secondary_uom_id = fields.Many2one('product.secondary.unit')
    secondary_uom_factor = fields.Float()


class StockPickingAssignHistoryLine(models.Model):
    _inherit = "stock.picking.assign.history.line"
    _description = "stock.picking.assign.history.line"

    secondary_uom_qty_demand = fields.Integer(compute='_compute_secondary_uom_qty', store=True)
    secondary_uom_qty_done = fields.Integer(compute='_compute_secondary_uom_qty', store=True)
    secondary_uom_qty_to_add = fields.Integer()

    @api.depends('move_id.quantity_done', 'move_id.product_uom_qty', 'assign_history_id.secondary_uom_factor') 
    def _compute_secondary_uom_qty(self):
        for record in self.filtered(lambda x: x.assign_history_id.secondary_uom_factor):
            record.secondary_uom_qty_demand = round(record.move_id.product_uom_qty / record.assign_history_id.secondary_uom_factor)
            record.secondary_uom_qty_done = round(record.move_id.quantity_done / record.assign_history_id.secondary_uom_factor)
