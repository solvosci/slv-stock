# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import api, models


class GS1Barcode(models.Model):
    _inherit = "gs1_barcode"

    @api.model
    def decode(self, barcode_string):
        res = super().decode(barcode_string)
        if res.get('310'):
            res['37'] = res.get('310')
        return res
