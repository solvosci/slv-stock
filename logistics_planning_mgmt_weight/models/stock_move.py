# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_name_get(self):
        name = super()._prepare_name_get()
        self_sudo = self.sudo()
        sm = self_sudo.browse()
        if self_sudo.picking_vehicle_id:
            # For outputs
            sm |= self
        elif self_sudo.purchase_line_id.related_real_order_line_id:
            # Ticket inputs
            sm |= self_sudo.env["stock.move"].search([
                ("classification_purchase_order_id", "=", self_sudo.purchase_line_id.order_id.id)
            ])
        if sm:
            name = "%s [%s]" % (name, sm.picking_vehicle_id.name)
        return name
