# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, fields, api, _


class StockPickingAssignedWizard(models.TransientModel):
    _inherit = 'sp.assigned.wizard'

    batch_id = fields.Many2one('stock.picking.batch')
    move_batch_ids = fields.Many2many('stock.move', compute='_compute_move_batch_ids', store=True)

    def get_move_pending(self):
        res = super().get_move_pending()
        if self.batch_id:
            res = [x for x in res if x.picking_id in self.batch_id.picking_ids]
            res = sorted(res, key=lambda x: x.partner_id.wms_code)
        return res

    def get_move_line_done(self):
        res = super().get_move_line_done()
        if self.batch_id:
            res = [x for x in res if x.move_id.picking_id in self.batch_id.picking_ids]
            res = sorted(res, key=lambda x: x.partner_id.wms_code)
        return res

    @api.onchange('batch_id')
    def _onchange_batch_id(self):
        self.product_id = False
        super()._onchange_lot_id()

    @api.depends('batch_id')
    def _compute_move_batch_ids(self):
        if self.batch_id:
            self.move_batch_ids = self.batch_id.move_lines.filtered(lambda x: 
                x.state not in['cancel', 'done'] and 
                x.product_uom_qty > x.quantity_done
            )
        else:
            self.move_batch_ids = False

    def refresh_move_batch_ids(self):
        for record in self.line_ids:
            if record.qty_to_add + record.qty_done >= record.qty_demand:
                self.move_batch_ids = [(3, record.move_id.id)] 

    def button_assigned(self):
        self.refresh_move_batch_ids()
        return super(StockPickingAssignedWizard, self).button_assigned()

    def button_assigned_and_print(self):
        self.refresh_move_batch_ids()
        return super(StockPickingAssignedWizard, self).button_assigned_and_print()

    def button_variable_weight_assigned(self):
        self.refresh_move_batch_ids()
        return super(StockPickingAssignedWizard, self).button_variable_weight_assigned()
