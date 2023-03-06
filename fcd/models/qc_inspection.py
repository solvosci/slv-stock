# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields, api


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    fcd_document_id = fields.Many2one(comodel_name="fcd.document", compute="_compute_fcd_document_id", store=True)

    @api.model
    def create(self, vals):
        record = super(QcInspection, self).create(vals)
        if self.env.context.get('fcd'):
            record.inspection_lines =  record._prepare_inspection_lines(record.test)
        return record

    def object_selection_values(self):
        result = super().object_selection_values()
        result.extend(
            [
                ("fcd.document", "FCD Document"),
            ]
        )
        return result

    @api.depends("object_id")
    def _compute_fcd_document_id(self):
        for inspection in self:
            if inspection.object_id and inspection.object_id._name == "fcd.document":
                inspection.fcd_document_id = inspection.object_id
            else:
                inspection.fcd_document_id = False
