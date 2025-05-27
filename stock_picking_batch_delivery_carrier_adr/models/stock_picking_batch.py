# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.exceptions import UserError
from odoo import models, fields, api, _


class StockPickingBatch(models.Model):
    _inherit="stock.picking.batch"

    package_qty = fields.Integer(
        compute="_compute_package_qty",
        store=True
        )
    packages_weight = fields.Float(
        compute="_compute_packages_weight",
        store=True
        )
    adr_package_qty = fields.Integer(
        compute="_compute_package_qty",
        store=True
        )
    adr_packages_weight = fields.Float(
        compute="_compute_packages_weight",
        store=True
        )

    @api.depends('picking_ids','picking_ids.package_qty', 'picking_ids.adr_package_qty')
    def _compute_package_qty(self):
        for batch in self:
            total_qty = 0
            adr_qty = 0
            for picking in batch.picking_ids:
                total_qty += picking.package_qty
                if picking.adr_package_qty > 0:
                    adr_qty += picking.adr_package_qty
            batch.package_qty = total_qty
            batch.adr_package_qty = adr_qty

    @api.depends('picking_ids','picking_ids.packages_weight', 'picking_ids.adr_packages_weight')
    def _compute_packages_weight(self):
        for batch in self:
            total_weight = 0.0
            adr_weight = 0.0
            for picking in batch.picking_ids:
                total_weight += picking.packages_weight
                if picking.adr_packages_weight > 0.0:
                    adr_weight += picking.adr_packages_weight
            batch.packages_weight = total_weight
            batch.adr_packages_weight = adr_weight

    def action_consignment_note_report_pdf(self):
        return self.env.ref('stock_picking_batch_delivery_carrier_adr.action_consignment_note_report_pdf').report_action(self)
