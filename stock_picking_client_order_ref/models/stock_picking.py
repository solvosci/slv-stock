# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    client_order_ref = fields.Char(related='sale_id.client_order_ref')
  
 