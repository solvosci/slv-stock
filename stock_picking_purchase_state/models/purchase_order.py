# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "stock.picking.state.mixin"]
    
    # Selection duplicated due to a bug in odoo with mixins and translations
    # Read more: https://github.com/odoo/odoo/issues/33672
    picking_status = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ])
