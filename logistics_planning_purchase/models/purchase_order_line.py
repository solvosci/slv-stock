# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, fields, models

from odoo.addons.logistics_planning_base.models.logistics_schedule import (
    PRICE_UNIT_TYPES,
)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    logistics_schedule_ids = fields.One2many(
        comodel_name="logistics.schedule",
        inverse_name="purchase_order_line_id",
        string="Logistics Schedules",
        copy=False,
    )
    logistics_price_unit_type = fields.Selection(
        selection=PRICE_UNIT_TYPES,
        default=PRICE_UNIT_TYPES[1][0],
    )
    logistics_price_unit = fields.Float(digits="Product Price")
    logistics_schedule_skip = fields.Boolean(
        related="order_id.logistics_schedule_skip",
    )
    logistics_schedule_init = fields.Integer(
        string="Initial required schedules",
        copy=False,
    )
    ls_schedule_allowed = fields.Boolean(
        compute="_compute_ls_schedule_allowed",
        help="""
        Technical field that determines if logistics schedules
        are allowed for this line
        """,
    )

    def _compute_ls_schedule_allowed(self):
        for line in self:
            line.ls_schedule_allowed = (
                not line.logistics_schedule_skip
                and not line.display_type
                and line.product_id.type in ["product", "consu"]
                and line.state in ["draft", "sent", "to approve", "purchase"]
            )

    def _prepare_logistics_schedule(self):
        self.ensure_one()
        return {
            "type": "input",
            "origin": self.order_id.name,
            "company_id": self.company_id.id,
            "destination_partner_id": self.order_id.picking_type_id.warehouse_id.id,
            "partner_id": self.partner_id.id,
            "product_id": self.product_id.id,
            "product_uom": self.product_uom.id,
            # TODO confirm this field
            "scheduled_load_date": self.date_planned,
            "logistics_price_unit_type": self.logistics_price_unit_type,
            "logistics_price_unit": self.logistics_price_unit,
            "transport_type": self.order_id.ls_transport_type,
            "purchase_order_line_id": self.id,
        }

    def action_logistics_schedule_add(self):
        self.ensure_one()
        Wizard = self.env["logistics.schedule.purchase.add.wizard"]
        new = Wizard.create({
            "purchase_line_id": self.id,
            "ls_count": len(self.sudo().logistics_schedule_ids),
            "logistics_price_unit_type": self.logistics_price_unit_type,
            "currency_id": self.currency_id.id,
        })
        return {
            "name": _("Add schedule(s)"),
            "res_model": Wizard._name,
            "view_mode": "form",
            "view_type": "form",
            "res_id": new.id,
            "target": "new",
            "type": "ir.actions.act_window",
        }
    
    def write(self, values):
        """
        We add here those purchase line values that should be hardlinked
        to logistics schedules
        """
        ret = super().write(values)
        if "date_planned" in values:
            self.sudo().logistics_schedule_ids.filtered(
                lambda x: x.state not in ["done", "cancel"]
            ).write({"scheduled_load_date": values["date_planned"]})
        return ret
