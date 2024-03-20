# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockPickingAssignedWizard(models.TransientModel):
    _name = 'sp.assigned.wizard'

    picking_type_id = fields.Many2one('stock.picking.type')
    product_id = fields.Many2one('product.product')
    lot_id = fields.Many2one('stock.production.lot')
    lot_qty = fields.Float(compute='_compute_lot_qty', store=True)
    qty_actual_in_lines = fields.Float(compute='_compute_qty_actual_in_lines', store=True)
    qty_remaining = fields.Float(compute='_compute_qty_remaining', store=True)
    line_ids = fields.One2many('sp.assigned.line.wizard', 'assigned_id')

    def get_move_pending(self):
        move_ids = self.env['stock.move'].search([
            ('product_id', '=', self.product_id.id),
            ('state', 'not in', ['done', 'cancel']),
            ('picking_type_id', '=', self.picking_type_id.id)
        ])

        return move_ids.filtered(lambda x: x.quantity_done < x.product_uom_qty)

    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        self.line_ids.unlink()
        self.write({
            'line_ids': [(0, 0, {
                'move_id': move.id,
            }) for move in self.get_move_pending()]
        })
        self.assigned_all_lines()

    @api.depends('lot_id', 'lot_id.qty_remaining_not_done')
    def _compute_lot_qty(self):
        for record in self:
            record.lot_qty = record.lot_id.qty_remaining_not_done

    @api.depends('line_ids.move_id.quantity_done')
    def _compute_qty_actual_in_lines(self):
        for record in self:
            record.qty_actual_in_lines = sum(record.line_ids.move_id.mapped('quantity_done'))

    @api.depends('line_ids', 'lot_id.qty_remaining_not_done', 'line_ids.qty_to_add')
    def _compute_qty_remaining(self):
        for record in self:
            record.qty_remaining = record.lot_id.qty_remaining_not_done - sum(record.line_ids.mapped('qty_to_add'))

    def assigned_all_lines(self):
        for line in self.line_ids:
            missing_qty = line.qty_demand  - line.qty_done
            if self.lot_qty >= missing_qty:
                line.qty_to_add += missing_qty
                self.lot_qty -= missing_qty
            elif self.lot_qty:
                line.qty_to_add += self.lot_qty
                self.lot_qty -= self.lot_qty
            else:
                pass

    def button_assigned_and_validate(self):
        if self.qty_remaining < 0:
            raise ValidationError(_("The remaining quantity should be positive."))
        for line in self.line_ids.filtered(lambda x: x.qty_to_add):
            self.env['stock.move.line'].create({
                'move_id': line.move_id.id,
                'lot_id': self.lot_id.id,
                'qty_done': line.qty_to_add,
                'product_id': line.move_id.product_id.id,
                'product_uom_id': line.move_id.product_uom.id,
                'location_id': line.move_id.location_id.id,
                'location_dest_id': line.move_id.location_dest_id.id,
            })

        # for picking_id in self.line_ids.filtered(lambda x: x.qty_to_add).mapped('picking_id'):
        #     picking_id.action_confirm()
        #     picking_id.action_assign()
        #     picking_id._action_done()
