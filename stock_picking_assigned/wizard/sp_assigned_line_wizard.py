# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, fields, api


class StockPickingAssignedLineWizard(models.TransientModel):
    _name = "sp.assigned.line.wizard"

    assigned_id = fields.Many2one('sp.assigned.wizard')

    picking_id = fields.Many2one('stock.picking', related='move_id.picking_id')
    partner_id = fields.Many2one('res.partner', related='move_id.picking_id.partner_id')
    move_id = fields.Many2one('stock.move')
    qty_to_add = fields.Float()
    qty_demand = fields.Float(compute='_compute_qty', store=True)
    qty_done = fields.Float(compute='_compute_qty', store=True)
    qty_done_demand = fields.Char(compute='_compute_qty', store=True)

    @api.depends('move_id', 'move_id.quantity_done', 'move_id.product_uom_qty')
    def _compute_qty(self):
        for record in self:
            record.qty_done = record.move_id.quantity_done
            record.qty_demand = record.move_id.product_uom_qty
            record.qty_done_demand = '%s / %s' % (record.qty_done, record.qty_demand)
