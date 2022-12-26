# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields


class FcdFishingGear(models.Model):
    _name = 'fcd.fishing.gear'
    _description = 'fcd.fishing.gear'

    name = fields.Char()
    code = fields.Char()
    ship_ids = fields.Many2many('fcd.ship', 'ship_fishing_gear_rel', 'fcd_fishing_gear_id', 'fcd_ship_id')
    ship_ids_count = fields.Integer('fcd.ship', compute='_compute_ship_count')

    def _compute_ship_count(self):
        for ship in self:
            ship.ship_ids_count = len(ship.ship_ids)
