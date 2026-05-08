# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields


class ProductLabelTemplate(models.Model):
    _name = "product.label.template"
    _description = "product.label.template"

    name = fields.Char()
    qweb_template = fields.Many2one("ir.ui.view", domain=[("type", "=", "qweb")])
    active = fields.Boolean(default=True)
