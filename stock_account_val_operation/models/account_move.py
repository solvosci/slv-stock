# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models, fields, api, _
from odoo.tools import float_is_zero


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    val_operation = fields.Selection(selection=[
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
        ('in_return', 'In Return'),
        ('out_return', 'Out Return'),
        ('inv_adjust', 'Inventory Adjustment'),
        ('scrap', 'Scrap'),
        ('price_update', 'Price Update'),
        ], compute="_compute_val_operation",
        store=True
    )
    val_operation_origin = fields.Char(
        compute="_compute_val_operation",
        store=True
    )
    val_operation_origin_invisible = fields.Boolean(
        compute="_compute_val_operation_origin_invisible",
    )

    def _get_val_operation_origin_target(self):
        move = self.move_id.stock_move_id
        if not move:
            return False, False
        if self.val_operation == 'scrap':
            res_id = len(move.scrap_ids) == 1 and move.scrap_ids.id
            return res_id, 'stock.scrap'
        else:
            return move.picking_id.id, 'stock.picking'

    def action_val_operation_origin(self):
        self.ensure_one()
        res_id, res_model = self._get_val_operation_origin_target()
        if not res_id or not res_model:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Valuation Operation Origin'),
            'view_mode': 'form',
            'res_model': res_model,
            'target': 'new',
            'res_id': res_id,
        }

    @api.depends('move_id.stock_move_id','move_id.stock_valuation_layer_ids')
    def _compute_val_operation(self):
        # Case #1: every account move genereted from a stock move
        lines_with_move = self.filtered(lambda l: l.move_id.stock_move_id)
        for line in lines_with_move:
            move = line.move_id.stock_move_id
            src_usage = move.location_id.usage
            dst_usage = move.location_dest_id.usage
            if move.scrapped:
                val_operation = 'scrap'
            elif src_usage == 'inventory' or dst_usage == 'inventory':
                val_operation = 'inv_adjust'
            elif move.origin_returned_move_id:
                if dst_usage == 'internal':
                    val_operation = 'out_return'
                else:
                    val_operation = 'in_return'
            elif dst_usage == 'internal' and src_usage != 'internal':
                val_operation = 'incoming'
            elif src_usage == 'internal' and dst_usage != 'internal':
                val_operation = 'outgoing'
            val_operation_origin = (
                move.picking_id.name
                or move.reference
                or move.origin
            )
            line.val_operation = val_operation
            line.val_operation_origin = val_operation_origin
        # Case #2: price update move lines
        pd = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        lines_with_svl = self.filtered(lambda l: not l.move_id.stock_move_id and l.move_id.stock_valuation_layer_ids and float_is_zero(l.move_id.stock_valuation_layer_ids.quantity, precision_digits=pd))
        lines_with_svl.val_operation = 'price_update'
        lines_with_svl.val_operation_origin = lines_with_svl.product_id.default_code
        # Case #3: those account moves that actually don't belong to valuation changes
        (self - lines_with_move - lines_with_svl).update({
            'val_operation': False,
            'val_operation_origin': False,
        })

    @api.depends('val_operation')
    def _compute_val_operation_origin_invisible(self):
        lines_invisible = self.filtered(lambda x: not bool(x.val_operation) or x.val_operation in ('inv_adjust', 'price_update'))
        lines_invisible.val_operation_origin_invisible = True
        (self - lines_invisible).val_operation_origin_invisible = False
