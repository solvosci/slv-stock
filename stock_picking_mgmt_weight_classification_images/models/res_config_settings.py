# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    picking_operations_imagen_max_resolution = fields.Integer(
        related='company_id.picking_operations_imagen_max_resolution',
        string='Max resolution (Px)',
        readonly=False,
        required=True
    )
    picking_operations_imagen_quality = fields.Integer(
        related='company_id.picking_operations_imagen_quality',
        string='Quatily (1 - 100)',
        readonly=False,
        required=True
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    picking_operations_imagen_max_resolution = fields.Integer(
        string='Max resolution (Px)',
        default=900
    )
    picking_operations_imagen_quality = fields.Integer(
        string='Quatily (1 - 100)',
        default=70
    )
