# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    logistics_schedule_default_journal_id = fields.Many2one(
        comodel_name='account.journal',
        related='company_id.logistics_schedule_default_journal_id',
        string='Default Journal in Logistics Schedule',
        readonly=False,
        required=True
    )

    ls_default_inv_i_g_product_id = fields.Many2one(
        related="company_id.ls_default_inv_i_g_product_id",
        readonly=False,
        required=True,
    )
    ls_default_inv_i_og_product_id = fields.Many2one(
        related="company_id.ls_default_inv_i_og_product_id",
        readonly=False,
        required=True,
    )
    ls_default_inv_o_g_product_id = fields.Many2one(
        related="company_id.ls_default_inv_o_g_product_id",
        readonly=False,
        required=True,
    )
    ls_default_inv_o_og_product_id = fields.Many2one(
        related="company_id.ls_default_inv_o_og_product_id",
        readonly=False,
        required=True,
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def _default_logistics_schedule_default_journal_id(self):
        return self.env["account.journal"].search([("type", "=", "purchase")], limit=1)

    logistics_schedule_default_journal_id = fields.Many2one(
        comodel_name='account.journal',
        domain="[('type', '=', 'purchase')]",
        default=_default_logistics_schedule_default_journal_id,
        string='Default Journal in Logistics Schedule',
    )

    ls_default_inv_i_g_product_id = fields.Many2one(
        comodel_name="product.product",
        domain="[('type', '=', 'service')]",
        string="Default product in invoices for ground inputs",
    )
    ls_default_inv_i_og_product_id = fields.Many2one(
        comodel_name="product.product",
        domain="[('type', '=', 'service')]",
        string="Default product in invoices for ocean-going inputs",
    )
    ls_default_inv_o_g_product_id = fields.Many2one(
        comodel_name="product.product",
        domain="[('type', '=', 'service')]",
        string="Default product in invoices for ground outputs",
    )
    ls_default_inv_o_og_product_id = fields.Many2one(
        comodel_name="product.product",
        domain="[('type', '=', 'service')]",
        string="Default product in invoices for ocean-going outputs",
    )
