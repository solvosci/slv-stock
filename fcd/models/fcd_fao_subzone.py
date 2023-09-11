# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields, api


class FaoSubZone(models.Model):
    _name = 'fcd.fao.subzone'
    _description = 'fcd.fao.subzone'

    name = fields.Char(compute='_compute_name', store=True)
    subzone_code = fields.Char()
    division_name = fields.Char()
    subzone = fields.Char()
    division = fields.Char()
    zone_id = fields.Many2one('fcd.fao.zone')
    zone_id_count = fields.Integer('fcd.fao.zone', compute='_compute_zone_id_count')
    zone_code = fields.Char()
    zone_name = fields.Char()

    @api.depends('zone_code', 'zone_name', 'subzone', 'division', 'division_name')
    def _compute_name(self):
        for record in self:
            if record.division:
                record.name = '%s.%s.%s %s/%s' % (record.zone_code, record.subzone, record.division, record.zone_name, record.division_name)
            elif not record.subzone:
                record.name = '%s %s' % (record.zone_code, record.zone_name)
            elif not record.division: 
                record.name = '%s.%s %s' % (record.zone_code, record.subzone, record.zone_name)
            else:
                record.name = False

    def _compute_zone_id_count(self):
        for fao in self:
            fao.zone_id_count = len(fao.zone_id)
