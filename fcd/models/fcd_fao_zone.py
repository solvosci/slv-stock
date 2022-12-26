# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields


class FaoZone(models.Model):
    _name = 'fcd.fao.zone'
    _description = 'fcd.fao.zone'

    name = fields.Char(compute='_compute_name')
    code = fields.Char()
    description = fields.Char()
    subzone_ids = fields.One2many('fcd.fao.subzone', 'zone_id')
    subzone_ids_count = fields.Integer('fcd.fao.subzone', compute='_compute_subzone_ids_count')
    notes = fields.Text()
    notes_subzone = fields.Text()

    def _compute_name(self):
        for record in self:
            record.name = '%s - %s' % (record.code, record.description)

    def _compute_subzone_ids_count(self):
        for subzone in self:
            subzone.subzone_ids_count = len(subzone.subzone_ids)
