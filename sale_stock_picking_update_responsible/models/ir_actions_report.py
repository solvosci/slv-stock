# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        res = super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)
        if report_ref == 'stock.report_picking' and res_ids and self.env.user.has_group('sale_stock_picking_update_responsible.group_sale_stock_picking_preparer'):
                pickings = self.env['stock.picking'].browse(res_ids).exists()
                pickings.filtered(lambda x: not x.user_id and x.state not in ['done','cancel'] and x.sale_id).write({'user_id': self.env.user})
        return res
