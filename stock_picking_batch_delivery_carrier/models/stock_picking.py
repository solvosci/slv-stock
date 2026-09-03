# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.constrains('carrier_id')
    def _check_carrier_id(self):
        for picking in self.filtered(lambda p: p.batch_id and p.carrier_id != p.batch_id.carrier_id):
            raise UserError(
                _("The carrier of the picking must match the carrier of the batch.\nBatch Carrier: %s,\nPicking Carrier: %s") %
                (picking.batch_id.carrier_id.name, picking.carrier_id.name)
            )
