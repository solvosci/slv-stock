# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, _
from odoo.exceptions import UserError


class Report(models.Model):
    _inherit = "ir.actions.report"

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        if report_ref == "stock_picking_batch_delivery_carrier_adr.stock_picking_batch_template":
            batches = self.env["stock.picking.batch"].browse(res_ids)
            invalid_batches = batches.filtered(lambda b: not b.carrier_id.partner_id)

            if invalid_batches:
                batch_names = ", ".join(invalid_batches.mapped("name"))
                raise UserError(_(
                    "The following batches have a delivery method with no associated carrier (partner): %s.\n"
                    "Please configure the carrier in the corresponding delivery method.") % batch_names
                )

        return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)
