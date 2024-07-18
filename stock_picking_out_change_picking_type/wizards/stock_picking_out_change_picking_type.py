# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ReturnPicking(models.TransientModel):
    _inherit = "stock.picking.out.change.picking.type.wizard"
    _description = "Stock Picking Out Change Picking Type Wizard"
    _check_company_auto = True

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_model = self.env.context["active_model"]
        active_ids = self.env.context["active_ids"] or []
        picking = self.env[active_model].browse(active_ids)
        res.update({"picking_id": picking.id})
        return res
    
    picking_id = fields.Many2one(
        comodel_name="stock.picking",
        required=True,
        readonly=True,
    )
    company_id = fields.Many2one(
        related="picking_id.company_id",
        required=True,
        store=True,
    )
    old_picking_type_id = fields.Many2one(
        string="Current Operation Type",
        related="picking_id.picking_type_id",
    )
    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        check_company=True,
        domain=[("code", "=", "outgoing")],
        string="New Operation Type",
    )
    location_id = fields.Many2one(
        string="New Source Location",
        related="picking_type_id.default_location_src_id",
    )
    location_dest_id = fields.Many2one(
        string="New Destination Location",
        related="picking_type_id.default_location_dest_id",
    )

    def change_picking_type(self):
        self.ensure_one()
        if (
            not self.picking_type_id
            or self.picking_type_id == self.old_picking_type_id
        ):
            return
        if not self.picking_id.change_picking_type_enabled:
            raise ValidationError(_(
                "Cannot change Operation Type for %s because is"
                " not allowed due to its current state"
            ) % self.picking_id.name)
        
        self.picking_id.write({
            "picking_type_id": self.picking_type_id.id,
            "location_id": self.location_id.id,
            "location_dest_id": self.location_dest_id.id,
        })

        wiz_change = self.env["stock.move.change.source.location.wizard"].with_context(
            active_ids=self.picking_id.ids, active_model="stock.picking"
        ).create({
            "new_location_id": self.picking_id.location_id.id,
            "moves_to_change": "all",
        })
        ret = wiz_change.action_apply()
        msg = _("Operation Type moved from %s to %s") % (
            self.old_picking_type_id.display_name, self.picking_type_id.display_name
        )
        self.picking_id.message_post(body=msg)

        return ret
