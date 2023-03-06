# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    fcd_document_id = fields.Many2one('fcd.document', related="fcd_document_line_id.fcd_document_id")
    fcd_document_line_id = fields.Many2one('fcd.document.line', string="FCD Document Line")
    fcd_document_line_name = fields.Char(related="fcd_document_line_id.name")
    fcd_document_line_box_count = fields.Integer(related="fcd_document_line_id.box_count")

    qc_inspection_ids = fields.One2many(comodel_name='qc.inspection', related="fcd_document_id.qc_inspection_ids", string='Inspection')
    fcd_document_created_inspections = fields.Integer(related="fcd_document_id.created_inspections")
    fcd_document_done_inspections = fields.Integer(related="fcd_document_id.done_inspections")
    fcd_document_passed_inspections = fields.Integer(related="fcd_document_id.passed_inspections")
    fcd_document_failed_inspections = fields.Integer(related="fcd_document_id.failed_inspections")

    notes_quality = fields.Text()
    notes_line = fields.Text()

    def action_calculate_inspection_context(self):
        self.ensure_one()
        return self.fcd_document_id.action_calculate_inspection_context()

    def action_calculate_inspection_done_context(self):
        self.ensure_one()
        return self.fcd_document_id.action_calculate_inspection_done_context()

    def action_calculate_inspection_passed_context(self):
        self.ensure_one()
        return self.fcd_document_id.action_calculate_inspection_passed_context()

    def action_calculate_inspection_failed_context(self):
        self.ensure_one()
        return self.fcd_document_id.action_calculate_inspection_failed_context()
