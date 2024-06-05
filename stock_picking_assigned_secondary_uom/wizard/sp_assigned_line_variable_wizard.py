# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, fields, api
import math


class StockPickingAssignedLineVariableWizard(models.TransientModel):
    _inherit = "sp.assigned.line.variable.wizard"

    secondary_uom_qty_done = fields.Integer(compute='_compute_secondary_uom_qty_done', store=True)
    secondary_uom_qty_to_add = fields.Integer(compute='_compute_secondary_uom_qty_to_add', store=True)
    secondary_uom_demand_done = fields.Char(compute='_compute_secondary_uom_demand_done', store=True)

    @api.depends('qty_variable', 'assigned_id.secondary_uom_factor') 
    def _compute_secondary_uom_qty_to_add(self):
        for record in self.filtered(lambda x: x.assigned_id.secondary_uom_factor):
            record.secondary_uom_qty_to_add = round(record.qty_variable_total / record.assigned_id.secondary_uom_factor)

    @api.depends('move_line_id.qty_done', 'assigned_id.secondary_uom_factor') 
    def _compute_secondary_uom_qty_done(self):
        for record in self.filtered(lambda x: x.assigned_id.secondary_uom_factor):
            record.secondary_uom_qty_done = round(record.move_line_id.qty_done / record.assigned_id.secondary_uom_factor)

    @api.depends('move_line_id.qty_done', 'qty_done_demand', 'assigned_id.secondary_uom_factor') 
    def _compute_secondary_uom_demand_done(self):
        for record in self.filtered(lambda x: x.assigned_id.secondary_uom_factor):
            record.secondary_uom_demand_done = '%s / %s' % (
                record.secondary_uom_qty_done,
                math.ceil(record.move_line_id.move_id.product_uom_qty / record.assigned_id.secondary_uom_factor)
            )