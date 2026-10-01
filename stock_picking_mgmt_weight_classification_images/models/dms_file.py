# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


class DmsFile(models.Model):
    _inherit = "dms.file"

    classification_picking_id = fields.Many2one(
        comodel_name='stock.picking'
    )
