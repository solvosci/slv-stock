# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    classification_pot_id = fields.Many2one(
        comodel_name="purchase.order.type",
        string="Default Purchase Order Type for classification process",
        help="When a picking of this type generates a new purchase order "
        "during classification process, this purchase type will be selected, "
        "if related partner doesn't assign anyone",
        compute="_compute_classification_pot_id",
        store=True,
        readonly=False,
    )

    @api.depends("scale")
    def _compute_classification_pot_id(self):
        for record in self.filtered(lambda x: not x.scale):
            record.classification_pot_id = False
