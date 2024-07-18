# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, fields, api


class StockPickingAssignedLineVariableWizard(models.TransientModel):
    _name = "sp.assigned.line.variable.wizard"
    _description = "sp.assigned.line.variable.wizard"
    _order = "wms_partner_code, id"

    assigned_id = fields.Many2one('sp.assigned.wizard')
    move_line_id = fields.Many2one('stock.move.line')

    variable_weight = fields.Boolean(related='assigned_id.variable_weight')

    picking_id = fields.Many2one('stock.picking', related='move_line_id.move_id.picking_id')
    partner_id = fields.Many2one('res.partner', related='move_line_id.move_id.picking_id.partner_id')
    wms_partner_code = fields.Integer(related='partner_id.wms_code', store=True)
    
    qty_variable = fields.Float()
    qty_variable_total = fields.Float()
    qty_done_demand = fields.Char(compute='_compute_qty', store=True)
    recounted = fields.Boolean(related='move_line_id.recounted')

    @api.depends('move_line_id', 'move_line_id.qty_done', 'move_line_id.move_id.product_uom_qty')
    def _compute_qty(self):
        for record in self:
            qty_done = record.move_line_id.qty_done
            qty_demand = record.move_line_id.move_id.product_uom_qty
            record.qty_done_demand = '%.2f / %.2f' % (qty_done, qty_demand)

    def acumulate_qty_variable(self):
        self.qty_variable_total += self.qty_variable
        self.qty_variable = 0

        return self.assigned_id.picking_type_id._assigned_open_wizard(self.assigned_id.id)
