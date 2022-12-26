# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields


class FcdShip(models.Model):
    _name = 'fcd.ship'
    _description = 'fcd.ship'

    name = fields.Char()
    license_plate = fields.Char()
    country_id = fields.Many2one('res.country')
    fishing_gear_ids = fields.Many2many('fcd.fishing.gear', 'ship_fishing_gear_rel', 'fcd_ship_id', 'fcd_fishing_gear_id')
