# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class MoveLineWeight(models.TransientModel):
    _name = 'stock.move.line.weight.wizard'

    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company,
                                 index=True,
                                 required=True)
    date = fields.Datetime('Date', default=fields.Datetime.now, required=True)
    product_id = fields.Many2one(
        'product.product', 'Product',
        ondelete="cascade",
        check_company=True,
        domain="[('type', '=', 'product'), ('company_id', 'in', [company_id, False])]")
    product_uom_id = fields.Many2one('uom.uom', related='product_id.uom_id', readonly=True)

    # Related order line
    order_line_id = fields.Many2one('purchase.order.line')
    # In update mode, old related order line
    old_order_line_id = fields.Many2one('purchase.order.line')
    # In update mode, classification order line
    classification_order_line_id = fields.Many2one('purchase.order.line')

    product_uom_qty = fields.Float('Qty', default=0.0, digits='Product Unit of Measure', required=True)
    move_id = fields.Many2one('stock.move', 'Stock Move')
    move_weight_id = fields.Many2one('stock.move.weight.wizard', 'Stock Move')
    partner_id = fields.Many2one(
        'res.partner',
        related='move_weight_id.picking_id.partner_id')

    @api.onchange('order_line_id')
    def _onchange_order_line_id(self):
        if not self.product_id and self.order_line_id:
            self.product_id = self.order_line_id.product_id

    # def domain_order_line_id(self, picking_id, product_id):
    #     res = {}
    #     if product_id:
    #         purchase = self.env['purchase.order.line']
    #         order_line = purchase.search(['|', ('partner_id', '=', picking_id.partner_id), ('product_id', '=', product_id)]).id
    #         res = {'domain': {'id', 'in', order_line}}
    #     return res
