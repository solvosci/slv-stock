# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import _, fields, models
from odoo.exceptions import ValidationError


class StockMoveLineSnWizard(models.TransientModel):
    _name = "stock.move.line.exchange.sn.wizard"
    _description = "Stock Move Line - Exchange S/N Wizard"

    stock_move_line_id = fields.Many2one(
        comodel_name="stock.move.line",
        required=True,
    )
    product_id = fields.Many2one(
        related="stock_move_line_id.product_id",
    )
    location_id = fields.Many2one(
        related="stock_move_line_id.location_id",
    )
    old_lot_id = fields.Many2one(
        related="stock_move_line_id.lot_id",
        string="Old S/N",
    )
    new_lot_id = fields.Many2one(
        comodel_name="stock.production.lot",
        string="New S/N",
    )
    new_lot_available_ids = fields.Many2many(
        comodel_name="stock.production.lot",
        compute="_compute_new_lot_available_ids",
        string="Available S/Ns",
    )

    def _compute_new_lot_available_ids(self):
        for rec in self:
            lot_ids = self.env["stock.quant"].search([
                ("product_id", "=", self.product_id.id),
                ("location_id", "=", self.location_id.id),
                ("quantity", ">", 0.0),
            ]).lot_id
            lot_ids -= self.stock_move_line_id.move_id.move_line_ids.lot_id
            rec.new_lot_available_ids = lot_ids

    def action_confirm(self):
        # Steps to be completed:
        # (1) Check if new S/N is already in use
        # (1.1) If locked => raise error
        # (1.2) If not locked => unassign it in old move, edit warning
        # (2) Directly replace it here

        # So we need to obtanin current sml, if exists
        old_lot_id = self.old_lot_id
        new_lot_sml_id = self.stock_move_line_id._get_reserved_for_sn(self.new_lot_id)
        new_lot_doc_id = new_lot_sml_id and new_lot_sml_id._get_document()
        if new_lot_doc_id and new_lot_doc_id.sn_locked:
            raise ValidationError(
                _("The S/N %s is currently locked by %s")
                % (self.new_lot_id.name, new_lot_doc_id.name)
            )
        elif new_lot_doc_id:
            # New lot released in origin
            self._update_sml_sn(new_lot_sml_id, False)
            # New lot assigned here
            self._update_sml_sn(self.stock_move_line_id, self.new_lot_id)
            # Old lot reservation update
            # self._update_reserved_quantity(old_lot_id, -1.0)
            # New lot former document warning
            new_lot_doc_id.message_post(
                body=_("WARNING! The S/N %s for %s has been stolen by %s")
                % (
                    self.new_lot_id.name,
                    self.stock_move_line_id.product_id.display_name,
                    self.stock_move_line_id._get_document().name,
                ),
                subtype_id=self.env.ref("mail.mt_note").id,
                author_id=self.env.user.partner_id.id, 
            )
        else:
            # TODO release old lot here & assign new lot here
            # New lot assigned here
            self._update_sml_sn(self.stock_move_line_id, self.new_lot_id)
            # Old lot reservation update
            # self._update_reserved_quantity(old_lot_id, -1.0)
            # New lot reservation update
            # self._update_reserved_quantity(self.new_lot_id, 1.0)

    def _get_reserved_sml_for_sn(self, lot_id):
        # If should be one or none, because is a S/N
        return self.stock_move_line_id.search([
            ("lot_id", "=", lot_id.id),
            ("state", "not in", ["done", "cancel"]),
            ("product_uom_qty", ">", 0.0),
        ])
    
    def _update_sml_sn(self, sml_id, lot_id):
        if lot_id:
            quant_update = not bool(sml_id.product_uom_qty)
            sml_ids_qty_reserved = sum(sml_id.move_id.move_line_ids.mapped("product_uom_qty"))
            if quant_update:
                sml_ids_qty_reserved += 1.0
            values = {
                "lot_id": lot_id.id,
                "product_uom_qty": 1.0,
                "qty_done": 0.0,
                "state": (
                    "assigned" if sml_id.move_id.product_uom_qty <= sml_ids_qty_reserved
                    else "partially_available"
                ),
            }
            # if not lot_id:
            #     values["state"] = "confirmed"
            sml_id.write(values)
            if quant_update:
                # TODO use stock move _update_reserved_quantity instead??
                self.env["stock.quant"]._update_reserved_quantity(
                    sml_id.product_id, sml_id.location_id,
                    1.0, lot_id=lot_id,
                    package_id=False, owner_id=False, strict=False
                )
        else:
            sml_id.unlink()

    def _update_reserved_quantity(self, lot_id, qty):
        # TODO seems to be unnecessary
        pass
        # self.env["stock.quant"]._update_reserved_quantity(
        #     self.product_id, self.stock_move_line_id.location_id,
        #     qty, lot_id=lot_id,
        #     package_id=False, owner_id=False, strict=False
        # )
