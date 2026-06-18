# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockBarcodesOption(models.Model):
    _inherit = "stock.barcodes.option"

    ansi_datamatrix_mh10 = fields.Selection([
        ('Q', 'Quantity (Q)'),
        ('1P', 'Product Code (1P)'),
        ('1T', 'Lot Code (9D,10D,1T)'),
    ], string="ANSI MH10", help="Configure this field to enable processing of the corresponding AI in ANSI MH10 Datamatrix barcodes.")
