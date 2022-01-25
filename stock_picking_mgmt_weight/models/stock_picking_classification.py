# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields


class StockPickingClassification(models.Model):
    _name = 'stock.picking.classification'

    order_line_id = fields.Many2one('purchase.order.line')
    picking_id = fields.Many2one('stock.picking')
    product_id = fields.Many2one('product.product')
    product_qty = fields.Float(digits='Product Unit of Measure')
    clasification_date = fields.Datetime()
    user_id = fields.Many2one(comodel_name="res.users")
    # TODO emulate wizard selection
    weight_selection = fields.Char()
