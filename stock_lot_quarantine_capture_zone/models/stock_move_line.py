# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    capture_zone_id = fields.Many2one(
        "intecmar.capture.zone",
        string="Capture Zone",
        help="Capture Zone this line was received from.",
    )
    product_subject_to_zone_control = fields.Boolean(
        compute="_compute_product_subject_to_zone_control",
        help="Technical field controlling capture_zone_id's visibility.",
    )
    product_intecmar_categ_ids = fields.Many2many(
        "intecmar.capture.product.type",
        compute="_compute_product_intecmar_categ_ids",
        help="Technical field feeding capture_zone_id's domain.",
    )

    @api.depends("product_id.intecmar_categ")
    def _compute_product_subject_to_zone_control(self):
        for line in self:
            line.product_subject_to_zone_control = bool(
                line.product_id.intecmar_categ
            )

    @api.depends("product_id.intecmar_categ")
    def _compute_product_intecmar_categ_ids(self):
        for line in self:
            line.product_intecmar_categ_ids = line.product_id.intecmar_categ
