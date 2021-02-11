# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    partner_user_id = fields.Many2one(
        comodel_name="res.users",
        compute="_compute_partner_user_id",
        store=True,
        readonly=True,
    )

    @api.depends("partner_id")
    def _compute_partner_user_id(self):
        for picking in self:
            picking.partner_user_id = False
            if picking.partner_id:
                user = self.env["res.users"].search([
                    ("partner_id", "=", picking.partner_id.id)
                ])
                picking.partner_user_id = user or False
