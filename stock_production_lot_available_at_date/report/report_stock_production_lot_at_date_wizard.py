# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, fields, models, tools


class ReportStockProductionLotAtDateWizard(models.TransientModel):
    _name = "report.stock.production.lot.date.wizard"
    _description = "Stock Production Lot At Date Wizard"

    name = fields.Char(compute='_compute_name')
    date = fields.Date()
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Filter by product",
    )

    def _compute_name(self):
        for record in self:
            record.name = _('%s') % (record.date)

    def open_lot_at_date_report(self):
        res = self.env["report.stock.production.lot.date"]._from_data_create(self.date, self.product_id)

        action = {
            "name": _("Stock Production Lots At %s") % str(self.date),
            "res_model": "report.stock.production.lot.date",
            "view_mode": "tree",
            "target": "current",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", res.ids)],
            "context": {},
        }

        if not self.product_id:
            action["context"]["search_default_group_by_product_id"] = True
        else:
            action["name"] = _("Stock Production Lots %s At %s") % (self.product_id.name, str(self.date))
            action["views"] = [
                [
                    self.env.ref("stock_production_lot_available_at_date.report_stock_production_lot_date_view_tree_without_product").id,
                    "tree",
                ]
            ]

        return action
