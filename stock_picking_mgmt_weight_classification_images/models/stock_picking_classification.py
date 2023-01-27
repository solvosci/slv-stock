# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields


class StockPickingClassification(models.Model):
    _inherit = 'stock.picking.classification'

    dms_file_ids = fields.One2many(
        related='picking_id.dms_file_ids',
        string="Classification Images"
    )
