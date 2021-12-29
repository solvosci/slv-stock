# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrderType(models.Model):
    _inherit = "purchase.order.type"

    isext_no_po_count = fields.Integer(
        string="Nothing to Bill (recv. pend)",
        compute="_compute_po_isext_counts",
    )
    isext_ti_po_count = fields.Integer(
        string="Waiting Bills", compute="_compute_po_isext_counts"
    )
    isext_tic_po_count = fields.Integer(
        string="Waiting Bills (classif.)", compute="_compute_po_isext_counts"
    )

    @api.depends(
        "purchase_order_ids",
        "purchase_order_ids.state",
        "purchase_order_ids.invoice_status_ext",
    )
    def _compute_po_isext_counts(self):
        po_states = ("purchase", "done")
        po_model = self.env["purchase.order"]
        fetch_data = po_model.read_group(
            [("order_type", "in", self.ids), ("state", "in", po_states)],
            ["order_type", "invoice_status_ext"],
            ["order_type", "invoice_status_ext"],
            lazy=False,
        )
        result = [
            [
                data["order_type"][0],
                data["invoice_status_ext"],
                data["__count"],
            ]
            for data in fetch_data
        ]
        for order_type in self:
            order_type.isext_no_po_count = sum(
                [
                    r[2]
                    for r in result
                    if r[0] == order_type.id and r[1] == "no"
                ]
            )
            order_type.isext_ti_po_count = sum(
                [
                    r[2]
                    for r in result
                    if r[0] == order_type.id and r[1] == "to invoice"
                ]
            )
            order_type.isext_tic_po_count = sum(
                [
                    r[2]
                    for r in result
                    if r[0] == order_type.id and r[1] == "to invoice classif"
                ]
            )
