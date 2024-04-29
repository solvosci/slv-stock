# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    aux_picking_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Ticket partner (auxiliar)",
        help="""
        Technical field used as workaround when is required to prefill
        picking_parter_id with default_ from an action.
        This happens when we want to create a new ticket from a
        logistic schedule as draft record
        """,
    )
    aux_picking_vehicle_id = fields.Many2one(
        comodel_name="vehicle.vehicle",
        string="Ticket vehicle (auxiliar)",
        help="""
        Technical field used as workaround when is required to prefill
        picking_vehicle_id with default_ from an action.
        This happens when we want to create a new ticket from a
        logistic schedule as draft record
        """,
    )

    @api.onchange("aux_picking_vehicle_id")
    def _onchange_aux_picking_vehicle_id(self):
        if self.aux_picking_vehicle_id:
            self.picking_vehicle_id = self.aux_picking_vehicle_id

    @api.onchange("aux_picking_partner_id")
    def _onchange_aux_picking_partner_id(self):
        if self.aux_picking_partner_id:
            self.picking_partner_id = self.aux_picking_partner_id

    def _prepare_name_get(self):
        name = super()._prepare_name_get()
        self_sudo = self.sudo()
        if self.net_weight > 0.0:
            # Tickets => we overwrite default behavior
            name = "%s (%.3f %s)" % (
                self.picking_id.name, self.net_weight, self.product_uom.name
            )
        if self_sudo.picking_vehicle_id:
            # All cases when there's a license plate
            name = "%s [%s]" % (name, self_sudo.picking_vehicle_id.name)
        return name

    @api.model
    def create(self, values):
        res = super().create(values)
        if res.logistics_schedule_id:
            ls = res.logistics_schedule_id.sudo()
            ls.stock_move_id = res.id
            ls._onchange_stock_move_id()
        return res
