# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class Report(models.Model):
    _inherit = "ir.actions.report"

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        if report_ref == "stock_picking_batch_delivery_carrier_adr.stock_picking_batch_template":
            self.env["stock.picking.batch"].browse(res_ids)._check_consignment_note_carrier()
        return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)
