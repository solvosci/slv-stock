# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import _, fields, models
from odoo.exceptions import ValidationError


class StockMoveLineAddSnWizard(models.TransientModel):
    _name = "stock.move.line.add.sn.wizard"
    _description = "Stock Move Line - Add S/N Wizard"

    stock_move_id = fields.Many2one(
        comodel_name="stock.move",
        required=True,
    )
    product_id = fields.Many2one(
        related="stock_move_id.product_id",
    )
    location_id = fields.Many2one(
        related="stock_move_id.location_id",
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
            domain = [
                ("product_id", "=", self.product_id.id),
                ("location_id", "=", self.location_id.id),
                ("quantity", ">", 0.0),
            ]
            lot_ids = self.stock_move_id.move_line_ids.lot_id
            if lot_ids:
                domain.append(("lot_id", "not in", lot_ids.ids))
            rec.new_lot_available_ids = self.env["stock.quant"].search(domain).lot_id

    def action_confirm(self):
        self.ensure_one()
        # (1) Check if S/N can be used and if
        lot_sml_id = self.env["stock.move.line"]._get_reserved_for_sn(self.new_lot_id)
        lot_doc_id = lot_sml_id and lot_sml_id._get_document()
        if lot_doc_id and lot_doc_id.sn_locked:
            raise ValidationError(
                _("The S/N %s is currently locked by %s")
                % (self.new_lot_id.name, lot_doc_id.name)
            )
        # (2) Release lot (if used)
        if lot_sml_id:
            lot_sml_id.unlink()
            # TODO document warning

        # (3) Add move line and update move (if needed)
        sml_state = (
            "assigned" if (
                self.stock_move_id.product_uom_qty <=
                (sum(self.stock_move_id.move_line_ids.mapped("product_uom_qty")) + 1.0)
            )
            else "partially_available"
        )
        new_sml_id = self.env["stock.move.line"].create(
            self._prepare_sml_values(sml_state)
        )
        if self.stock_move_id.state != sml_state:
            self.stock_move_id.state = sml_state
        # (4) Reserve??
        self.env["stock.quant"]._update_reserved_quantity(
            self.product_id, self.location_id,
            1.0, lot_id=self.new_lot_id,
            package_id=False, owner_id=False, strict=False
        )

        # (5) Document warning
        if lot_doc_id:
            lot_doc_id.message_post(
                body=_("WARNING! The S/N %s for %s has been stolen by %s")
                % (
                    self.new_lot_id.name,
                    self.stock_move_id.product_id.display_name,
                    new_sml_id._get_document().name,
                ),
                subtype_id=self.env.ref("mail.mt_note").id,
                author_id=self.env.user.partner_id.id, 
            )

    def _prepare_sml_values(self, sml_state):
        """
        If a sml comes from another document (e.g. a production order),
        override this
        """
        values = {
            "move_id": self.stock_move_id.id,
            "product_id": self.product_id.id,
            "product_uom_qty": 1.0,
            "product_uom_id": self.stock_move_id.product_uom.id,
            "qty_done": 0.0,
            "location_id": self.location_id.id,
            "location_dest_id": self.stock_move_id.location_dest_id.id,
            "lot_id": self.new_lot_id.id,
            # TODO partially_available
            # "state": "assigned",
            "state": sml_state,
        }
        if self.stock_move_id.picking_id:
            values["picking_id"] = self.stock_move_id.picking_id.id
        return values
