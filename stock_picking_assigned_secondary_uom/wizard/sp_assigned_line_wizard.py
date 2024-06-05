# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, fields, api
import math



class StockPickingAssignedLineWizard(models.TransientModel):
    _inherit = "sp.assigned.line.wizard"

    secondary_uom_qty_done = fields.Integer(compute='_compute_secondary_uom_qty_done', store=True)
    secondary_uom_qty_to_add = fields.Integer()
    qty_to_add = fields.Float(compute='_compute_qty_to_add', store=True)
    secondary_uom_demand_done = fields.Char(compute='_compute_secondary_uom_demand_done', store=True)

    @api.depends('secondary_uom_qty_to_add', 'assigned_id.secondary_uom_factor') 
    def _compute_qty_to_add(self):
        for record in self.filtered(lambda x: x.assigned_id.secondary_uom_factor):
            record.qty_to_add = record.secondary_uom_qty_to_add * record.assigned_id.secondary_uom_factor

    # @api.depends('qty_to_add') 
    # def _compute_secondary_uom_qty_to_add(self):
    #     for record in self.filtered(lambda x: x.assigned_id.secondary_uom_factor):
    #         record.secondary_uom_qty_to_add = round(record.qty_to_add / record.assigned_id.secondary_uom_factor)

    @api.depends('move_id.quantity_done', 'assigned_id.secondary_uom_factor') 
    def _compute_secondary_uom_qty_done(self):
        for record in self.filtered(lambda x: x.assigned_id.secondary_uom_factor):
            record.secondary_uom_qty_done = round(record.move_id.quantity_done / record.assigned_id.secondary_uom_factor)

    @api.depends('move_id.quantity_done', 'assigned_id.secondary_uom_factor') 
    def _compute_secondary_uom_demand_done(self):
        for record in self.filtered(lambda x: x.assigned_id.secondary_uom_factor):
            record.secondary_uom_demand_done = '%s / %s' % (
                record.secondary_uom_qty_done, 
                math.ceil(record.move_id.product_uom_qty / record.assigned_id.secondary_uom_factor)
            )
