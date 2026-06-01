# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockPickingAssignedWizard(models.TransientModel):
    _name = 'sp.assigned.wizard'
    _description = "sp.assigned.wizard"

    picking_type_id = fields.Many2one('stock.picking.type')
    warehouse_id = fields.Many2one(related='picking_type_id.warehouse_id')
    location_domain_ids = fields.Many2many('stock.location', compute='_compute_location_domain_ids', store=True)
    location_id = fields.Many2one('stock.location', compute='_compute_location_id', store=True, readonly=False)
    product_id = fields.Many2one('product.product')
    lot_id = fields.Many2one('stock.production.lot')
    lot_qty = fields.Float(compute='_compute_lot_qty', store=True)
    qty_actual_in_lines = fields.Float(compute='_compute_qty_actual_in_lines', store=True)
    qty_remaining = fields.Float(compute='_compute_qty_remaining', store=True)
    line_ids = fields.One2many('sp.assigned.line.wizard', 'assigned_id')
    line_variable_ids = fields.One2many('sp.assigned.line.variable.wizard', 'assigned_id')

    variable_weight = fields.Boolean()
    mode_assign = fields.Selection([
        ('autoassigned', _('MODE AUTOASSIGNED')),
        ('variable', _('MODE VARIABLE WEIGHT'))
    ], compute='_compute_mode_assign', store=True)

    def get_move_pending(self):
        move_ids = self.env['stock.move']
        if self.lot_id:
            move_ids = move_ids.search([
                ('product_id', '=', self.product_id.id),
                ('state', 'not in', ['done', 'cancel']),
                ('picking_type_id', '=', self.picking_type_id.id)
            ])
            move_ids = move_ids.filtered(lambda x: x.quantity_done < x.product_uom_qty)
        return move_ids

    def get_move_line_done(self):
        move_line_ids = self.env['stock.move.line']
        if self.lot_id:
            move_line_ids = move_line_ids.search([
                ('product_id', '=', self.product_id.id),
                ('state', 'not in', ['done', 'cancel']),
                ('move_id.picking_type_id', '=', self.picking_type_id.id),
                ('qty_done', '>', 0),
                ('lot_id', '=', self.lot_id.id)
            ])
            move_line_ids = sorted(move_line_ids, key=lambda x: x.partner_id.wms_code)
        return move_line_ids

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.line_ids = False
        self.lot_id = False

    @api.onchange('lot_id', 'variable_weight')
    def _onchange_lot_id(self):
        self.line_ids = False
        self.line_variable_ids = False
        if not self.variable_weight:
            self.write({
                'line_ids': [(0, 0, {
                    'move_id': move.id,
                }) for move in self.get_move_pending()]
            })
            self.assigned_all_lines()
        else:
            self.write({
                'line_variable_ids': [(0, 0, {
                    'move_line_id': move_line_id.id,
                }) for move_line_id in self.get_move_line_done()]
            })

    @api.depends('variable_weight')
    def _compute_mode_assign(self):
        for record in self:
            if record.variable_weight:
                record.mode_assign = 'variable'
            else:
                record.mode_assign = 'autoassigned'

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
        ctx = dict(self.env.context)
        ctx.update({
            'location_id': self.location_id.id,
        })
        for record in self:
            record.qty_remaining = record.lot_id.with_context(ctx).qty_remaining_not_done - sum(record.line_ids.mapped('qty_to_add'))

    @api.depends('picking_type_id') 
    def _compute_location_domain_ids(self):
        for record in self:
            location = record.picking_type_id.warehouse_id.lot_stock_id
            record.location_domain_ids =[(4, location.id)]
            for location_id in record.location_domain_ids:
                child_ids = location_id.child_ids.ids
                if child_ids:
                    record.location_domain_ids = [(4, child_id) for child_id in set(child_ids)] 

    @api.onchange('location_id')
    def _onchange_location_id(self):
        self.lot_id._compute_qty_not_done()

    @api.depends('picking_type_id') 
    def _compute_location_id(self):
        for record in self:
            if record.picking_type_id:
                record.location_id = record.picking_type_id.warehouse_id.lot_stock_id

    def assigned_all_lines(self):
        for line in self.line_ids:
            missing_qty = line.qty_demand - line.qty_done
            if self.lot_qty >= missing_qty:
                line.qty_to_add += missing_qty
                self.lot_qty -= missing_qty
            elif self.lot_qty:
                line.qty_to_add += self.lot_qty
                self.lot_qty -= self.lot_qty
            else:
                pass

    def button_change_mode_variable_weight(self):
        self.variable_weight = True
        self._onchange_lot_id()
        return self.picking_type_id._assigned_open_wizard(self.id)

    def button_change_mode_autoassignation(self):
        self.variable_weight = False
        self._onchange_lot_id()
        return self.picking_type_id._assigned_open_wizard(self.id)

    def _prepare_assign_history_values(self):
        return {
            'date': fields.datetime.now(),
            'warehouse_id': self.warehouse_id.id,
            'product_id': self.product_id.id,
            'lot_id': self.lot_id.id
        }

    def _prepare_assign_history_line_values(self, line, assign_history_id):
        return { 
            'assign_history_id': assign_history_id.id,
            'move_id': line.move_id.id,
            'qty_to_add': line.qty_to_add,
        }

    def _prepare_exist_stock_move_line(self, line_id, assign_line_id):
        line_id.qty_done += assign_line_id.qty_to_add

    def _prepare_stock_move_line_values(self, line_id):
        return {
            'picking_id': line_id.move_id.picking_id.id,
            'move_id': line_id.move_id.id,
            'lot_id': self.lot_id.id,
            'qty_done': line_id.qty_to_add,
            'product_id': line_id.move_id.product_id.id,
            'product_uom_id': line_id.move_id.product_uom.id,
            'location_id': line_id.move_id.location_id.id,
            'location_dest_id': line_id.move_id.location_dest_id.id,
        }

    def assign(self):
        if self.qty_remaining < 0 or not self.product_id or not self.lot_id:
            raise ValidationError(_("The remaining quantity should be positive."))

        assign_history_id = self.env['stock.picking.assign.history'].create(
            self._prepare_assign_history_values()
        )

        for line in self.line_ids.filtered(lambda x: x.qty_to_add):
            self.env['stock.picking.assign.history.line'].create(
                self._prepare_assign_history_line_values(line, assign_history_id)
            )
            move_line_id = line.move_id.move_line_ids.filtered(lambda x: x.product_id == line.move_id.product_id and x.lot_id == self.lot_id)
            if move_line_id:
                self._prepare_exist_stock_move_line(move_line_id[0], line)
                # move_line_id[0].qty_done += line.qty_to_add
                # move_line_id = False
            else:
                self.env['stock.move.line'].create(self._prepare_stock_move_line_values(line))
        self._onchange_lot_id()

        return assign_history_id

    def button_assigned(self):
        self.assign()
        return self.picking_type_id._assigned_open_wizard(self.id)

    def button_assigned_and_print(self):
        assign_history_id = self.assign()
        return assign_history_id.print_distribution_sheets_ticket()

    def button_variable_weight_assigned(self):
        for line in self.line_variable_ids.filtered(lambda x: x.qty_variable_total):
            line.move_line_id.qty_done = line.qty_variable_total
            line.qty_variable_total = 0
            line.move_line_id.recounted = True
            line._compute_qty()

        return self.picking_type_id._assigned_open_wizard(self.id)
