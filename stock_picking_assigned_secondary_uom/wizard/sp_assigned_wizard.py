# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import math


class StockPickingAssignedWizard(models.TransientModel):
    _inherit = 'sp.assigned.wizard'

    secondary_uom_id = fields.Many2one('product.secondary.unit', )
    secondary_uom_factor = fields.Float()
    secondary_uom_qty_remaining = fields.Integer(compute='_compute_secondary_uom_remaining', store=True)

    @api.onchange('lot_id') 
    def _onchange_lot_id_secondary_uom(self):
        if self.lot_id:
            pol = self.env['purchase.order.line'].search([('fcd_lot_id', '=', self.lot_id.id)])
            self.secondary_uom_id = pol.secondary_uom_id.id
            self.secondary_uom_factor = round(pol.product_qty / pol.secondary_uom_qty)

    @api.depends('line_ids', 'line_ids.secondary_uom_qty_to_add', 'line_ids.secondary_uom_qty_done', 'line_ids.qty_to_add')
    def _compute_secondary_uom_remaining(self):
        for record in self.filtered(lambda x: x.secondary_uom_factor):
            record.secondary_uom_qty_remaining = math.floor(record.lot_qty / record.secondary_uom_factor) - sum(record.line_ids.mapped('secondary_uom_qty_to_add'))

    def _prepare_assign_history_values(self):
        res = super()._prepare_assign_history_values()
        res['secondary_uom_id'] = self.secondary_uom_id.id
        res['secondary_uom_factor'] = self.secondary_uom_factor
        return res

    def _prepare_assign_history_line_values(self, line, assign_history_id):
        res = super()._prepare_assign_history_line_values(line, assign_history_id)
        res['secondary_uom_qty_to_add'] = line.secondary_uom_qty_to_add
        res['secondary_uom_qty_done'] = line.secondary_uom_qty_done
        return res

    def _prepare_exist_stock_move_line(self, line_id, assign_line_id):
        super()._prepare_exist_stock_move_line(line_id, assign_line_id)
        if line_id.qty_done == assign_line_id.qty_to_add:
            line_id.secondary_uom_qty = assign_line_id.secondary_uom_qty_to_add
        else:
            line_id.secondary_uom_qty += assign_line_id.secondary_uom_qty_to_add

    def _prepare_stock_move_line_values(self, line):
        res = super()._prepare_stock_move_line_values(line)
        res['secondary_uom_qty'] = line.secondary_uom_qty_to_add
        res['secondary_uom_id'] = self.secondary_uom_id.id
        return res

    @api.onchange('secondary_uom_factor')
    def _onchange_secondary_uom_factor(self):
        super()._onchange_lot_id()

    @api.onchange('lot_id', 'variable_weight')
    def _onchange_lot_id(self):
        if self.secondary_uom_factor:
            super()._onchange_lot_id()

    def assigned_all_lines(self):
        for line in self.line_ids:
            missing_qty = line.qty_demand - line.qty_done
            missing_qty_box = math.ceil(missing_qty / self.secondary_uom_factor)

            if self.lot_id.qty_remaining_not_done <= 0:
                pass
            elif self.secondary_uom_qty_remaining >= missing_qty_box:  
                line.secondary_uom_qty_to_add += missing_qty_box
            elif self.secondary_uom_qty_remaining:
                line.secondary_uom_qty_to_add += self.secondary_uom_qty_remaining
            else:
                pass

    def button_variable_weight_assigned(self):
        for line in self.line_variable_ids.filtered(lambda x: x.qty_variable_total):
            line.move_line_id.secondary_uom_qty = line.secondary_uom_qty_to_add
            line.secondary_uom_qty_to_add = 0

        return super().button_variable_weight_assigned()
