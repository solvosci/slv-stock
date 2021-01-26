# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    exception_eco_partner_ids = fields.Many2many(
        'res.partner', 
        string="Exception ECO Productors"
    )

    exception_eco_partner_count = fields.Integer(
        compute="_compute_exception_eco_partner_count",
        store=True,
        readonly=True,        
    )

    @api.depends("exception_eco_partner_ids")
    def _compute_exception_eco_partner_count(self):
        for record in self:
            record.exception_eco_partner_count = \
            len(record.exception_eco_partner_ids)
