# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
from odoo import fields, models


class Vehicle(models.Model):
    _inherit = "vehicle.vehicle"

    transfer_count = fields.Integer(
        compute='_compute_transfer_count',
        string='Transfers')
    carrier_id = fields.Many2one(
        'res.partner',
        string='Carrier',
        domain="[('is_company', '=', True)]",
    )
    license_plate_last_towing = fields.Char(
        string="Last Towing",
        readonly=True
    )

    def _compute_transfer_count(self):
        StockPicking = self.env["stock.picking"]
        for vehicle in self:
            vehicle.transfer_count = len(StockPicking.search([
                ("vehicle_id", "=", vehicle.id)
            ]))

    def action_picking_tree_all(self):
        action = self.env.ref("stock.action_picking_tree_all").read()[0]
        action['context'] = self.env.context
        action['domain'] = [('vehicle_id', 'in', self.ids)]
        return action
