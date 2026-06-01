# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, fields, _


class StockPickingAssignHistory(models.Model):
    _name = "stock.picking.assign.history"
    _description = "stock.picking.assign.history"

    name = fields.Char(compute='_compute_name')
    warehouse_id = fields.Many2one('stock.warehouse')
    product_id = fields.Many2one('product.product')
    lot_id = fields.Many2one('stock.production.lot')
    partner_id = fields.Many2one('res.partner', compute='_compute_partner_id')
    date = fields.Datetime()

    line_ids = fields.One2many('stock.picking.assign.history.line', 'assign_history_id')

    def _compute_name(self):
        for record in self:
            record.name = '%s - %s' % (record.date, record.product_id.name)

    def _compute_partner_id(self):
        for record in self:
            if record.lot_id.purchase_order_ids:
                record.partner_id = record.lot_id.purchase_order_ids[0].partner_id
            else:
                record.partner_id = False

    def print_distribution_sheets_ticket(self):
        self.ensure_one()
        paper_format = self.env.ref("stock_picking_assigned.distribution_sheets_ticket")
        items = self.line_ids
        paper_format.page_height = 48 + (len(items) * 8)
        return self.env.ref("stock_picking_assigned.action_distribution_sheets_ticket_pdf").report_action(self)


class StockPickingAssignHistoryLine(models.Model):
    _name = "stock.picking.assign.history.line"
    _description = "stock.picking.assign.history.line"

    assign_history_id = fields.Many2one('stock.picking.assign.history')
    move_id = fields.Many2one('stock.move')
    partner_id = fields.Many2one('res.partner', related='move_id.picking_id.partner_id')
    wms_partner_code = fields.Integer(related='partner_id.wms_code')
    qty_to_add = fields.Float()
    qty_demand = fields.Float(related="move_id.product_uom_qty")
    qty_done = fields.Float(related="move_id.quantity_done")
