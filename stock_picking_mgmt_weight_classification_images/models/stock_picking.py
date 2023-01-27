# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    dms_file_ids = fields.One2many(
        comodel_name='dms.file',
        inverse_name='classification_picking_id',
        string='Classification Images'
    )
