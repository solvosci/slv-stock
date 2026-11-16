# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit="stock.picking"

    package_qty = fields.Integer(
        compute="_compute_package_qty",
        inverse="set_manual_field",
        store=True,
        readonly=False
        )
    packages_weight = fields.Float(
        compute="_compute_packages_weight",
        inverse="set_manual_field",
        store=True,
        readonly=False
        )
    adr_package_qty = fields.Integer(
        compute="_compute_package_qty",
        inverse="_set_adr_packages",
        store=True,
        readonly=False
        )
    adr_packages_weight = fields.Float(
        compute="_compute_packages_weight",
        inverse="_set_adr_packages",
        store=True,
        readonly=False
        )

    @api.depends('move_ids.package_qty')
    def _compute_package_qty(self):
        for picking in self:
            picking.package_qty = sum(picking.move_ids.mapped('package_qty'))
            adr_qty = 0
            for move in picking.move_ids:
                if move.is_dangerous:
                    adr_qty += move.package_qty
            picking.adr_package_qty = adr_qty

    @api.depends('move_ids.packages_weight')
    def _compute_packages_weight(self):
        for picking in self:
            picking.packages_weight = sum(picking.move_ids.mapped('packages_weight'))
            adr_weight = 0.0
            for move in picking.move_ids:
                if move.is_dangerous:
                    adr_weight += move.packages_weight
            picking.adr_packages_weight = adr_weight

    def set_manual_field(self):
        pass

    def _set_adr_packages(self):
        for picking in self:
            if picking.adr_package_qty > picking.package_qty:
                raise ValidationError(_("ADR packages quantity must be lower or equal to total packages quantity."))
            if picking.adr_packages_weight > picking.packages_weight:
                raise ValidationError(_("ADR packages weight must be lower or equal to total packages weight."))
