# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, fields, models


class LogisticsSchedule(models.Model):
    _inherit = "logistics.schedule"

    supply_condition_id = fields.Many2one(
        comodel_name="supply.condition",
        readonly=True,
        copy=False,
    )

    @api.onchange("stock_move_id")
    def _onchange_stock_move_id(self):
        super()._onchange_stock_move_id()
        upd_values = {}
        self_sudo = self.sudo()
        if not self.stock_move_id:
            # TODO clean some values?
            pass
        elif self_sudo.sale_order_line_id:
            upd_values.update({
                "license_plate_1": self_sudo.picking_id.vehicle_id.name,
                "license_plate_2": (
                    self.picking_id.towing_license_plate
                    if self.transport_type == "ground"
                    else self.picking_id.container_number
                ),
            })
        elif self_sudo.purchase_order_line_id:
            ticket = self_sudo.env["stock.move"].search([
                ("classification_purchase_order_id", "=", self_sudo.stock_move_id.purchase_line_id.order_id.id)
            ])
            if ticket:
                upd_values.update({
                    "license_plate_1": ticket.picking_vehicle_id.name,
                    "license_plate_2": ticket.picking_towing_license_plate,
                })
            else:
                # TODO raise exception?? Go to normal path?
                pass

        if upd_values:
            self.write(upd_values)
