# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields


class FcdDocumentLine(models.Model):
    _name = 'fcd.document.line'
    _description = 'fcd.document.line'

    name = fields.Char()
    fcd_document_id = fields.Many2one('fcd.document')
    lot_id = fields.Many2one('stock.production.lot')
    box_count = fields.Integer()
    notes_cost = fields.Text()
