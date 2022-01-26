# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero

from datetime import date, datetime
import os
import base64


class StockMoveBackend(models.Model):
    # This section only applies to backend basic modifications
    _inherit = 'stock.move'

    theoretical_qty = fields.Float(
        string='Theoretical quantity demanded',
        digits='Product Unit of Measure')

    tare = fields.Float(string='Tare', digits='Product Unit of Measure')
    date_tare = fields.Datetime(string='Tare date')
    exclude_tare = fields.Boolean(default=False)

    gross_weight = fields.Float(
        string='Gross',
        digits='Product Unit of Measure')
    date_gross_weight = fields.Datetime(string='Gross weight date')

    bool_theoretical_qty = fields.Boolean()
    bool_net_weight = fields.Boolean()

    net_weight = fields.Float(
        string='Net',
        digits='Product Unit of Measure',
        compute="_compute_net_weight",
        store=True,
        readonly=True,
    )

    weight_selected = fields.Float(
        digits='Product Unit of Measure')
    weight_classified = fields.Float(
        digits='Product Unit of Measure')

    @api.depends("tare", "exclude_tare", "gross_weight")
    def _compute_net_weight(self):
        for record in self:
            if record.gross_weight and (record.tare or record.exclude_tare):
                record.net_weight = record.gross_weight - (
                    record.tare if not record.exclude_tare else 0.0
                )
            else:
                record.net_weight = 0.0

    @api.onchange('exclude_tare')
    def _onchange_exclude_tare(self):
        if self.exclude_tare:
            self.tare = 0

    @api.onchange('tare')
    def _onchange_tare(self):
        if not self.exclude_tare and self.tare > 0.0:
            self.date_tare = fields.Datetime.now()
            # TODO pending image capture implementation and determine when is saved
            # self.capture_image_weight()
        else:
            self.date_tare = False

    @api.onchange('gross_weight')
    def _onchange_gross_weight(self):
        if self.gross_weight > 0.0:
            self.date_gross_weight = fields.Datetime.now()
            # TODO pending image capture implementation and determine when is saved
            # self.capture_image_weight()
        else:
            self.date_gross_weight = False

    def get_convert_weight_kg(self, weight_value):
        self.ensure_one()
        uom_kg = self.env.ref("uom.product_uom_kgm")
        return self.product_uom._compute_quantity(weight_value, uom_kg)


class StockMovFrontend(models.Model):
    # This section only applies to frontend additions (custom move views)
    _inherit = "stock.move"

    type_code = fields.Selection(related="picking_type_id.code")
    type_mandatory_towing = fields.Boolean(related="picking_type_id.mandatory_towing")
    picking_state = fields.Selection(related="picking_id.state")
    picking_vehicle_id = fields.Many2one(
        comodel_name="vehicle.vehicle",
        related="picking_id.vehicle_id",
        readonly=False,
        stored=True,
    )
    picking_towing_license_plate = fields.Char(
        related="picking_id.towing_license_plate",
        readonly=False
    )

    classification_picking_id = fields.Many2one(
        comodel_name="stock.picking",
        related="picking_id.classification_picking_id",
    )

    camera = fields.Binary(readonly=True, attachment=False)
    # asm = fields.Char(readonly=True)
    weight_image = fields.Image(readonly=True)
    weight_image_mini = fields.Image(
        "Variant Image Mini",
        related="weight_image",
        max_width=92,
        max_height=92,
        store=True,
    )
    current_weight = fields.Integer(
        readonly=True,
    )

    capture_gross_enabled = fields.Boolean(
        compute="_compute_capture_gross_enabled",
        store=True,
    )
    capture_tare_enabled = fields.Boolean(
        compute="_compute_capture_tare_enabled",
        store=True,
    )
    picking_note = fields.Text(
        related='picking_id.note',
        readonly=False,
    )
    classification_purchase_order_id = fields.Many2one(
        comodel_name="purchase.order",
        related="picking_id.classification_purchase_order_id",
        string="Classification Order",
    )
    classification_po_internal_note = fields.Text(
        related="picking_id.classification_purchase_order_id.internal_note",
        string="Classification Note",
    )
    # TODO remove
    origin_purchase_order_id = fields.Many2one(
        comodel_name="purchase.order",
        related="picking_id.classification_purchase_order_id.related_order_id",
        string="Origin Order",
        store=True,
    )
    origin_purchase_order_ids = fields.Many2many(
        comodel_name="purchase.order",
        related="picking_id.classification_purchase_order_id.related_order_ids",
        string="Origin Orders",
    )

    @api.model
    def create(self, values):
        if self.env.context.get("weight_mgmt", False):
            # TODO first create picking with the suitable picking type
            new_picking = self.env["stock.picking"].new({
                "partner_id": values["picking_partner_id"],
                "vehicle_id": values.get("picking_vehicle_id", False),
                "picking_type_id": values["picking_type_id"],
                "towing_license_plate": values["picking_towing_license_plate"]
            })
            new_picking.onchange_picking_type()
            picking = self.env["stock.picking"].create(
                new_picking._convert_to_write(new_picking._cache)
            )
            values.update({
                "picking_id": picking.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
            })
            picking.vehicle_id.sudo().write({
                "license_plate_last_towing": values["picking_towing_license_plate"]
            })
            # TODO custom name
        return super().create(values)

    @api.depends("product_id", "picking_type_id", "tare", "gross_weight", "type_code")
    def _compute_capture_gross_enabled(self):
        for rec in self:
            rec.capture_gross_enabled = (
                rec.picking_type_id
            ) and (
                rec.product_id
            ) and (
                rec.gross_weight == 0.0
            ) and (
                (
                    rec.type_code == "incoming"
                ) or (
                    rec.type_code == "outgoing" and rec.tare > 0.0
                )
            )

    @api.depends(
        "product_id", "picking_type_id", "tare", "gross_weight",
        "exclude_tare", "type_code"
    )
    def _compute_capture_tare_enabled(self):
        for rec in self:
            rec.capture_tare_enabled = (
                rec.picking_type_id
            ) and (
                rec.product_id
            ) and (
                rec.tare == 0.0
            ) and (
                (
                    rec.type_code == "incoming" and not rec.exclude_tare and rec.gross_weight > 0.0
                ) or (
                    rec.type_code == "outgoing"
                )
            )

    @api.constrains("tare", "gross_weight")
    def _check_weight_max(self):
        weight_max = self.env.company.picking_operations_weight_max
        for record in self:
            if not float_is_zero(
                weight_max,
                precision_rounding=record.product_id.uom_id.rounding
            ):
                if record.tare > weight_max:
                    raise ValidationError(
                        _("Tare too high (max. value=%.2f)") % weight_max
                    )
                if record.gross_weight > weight_max:
                    raise ValidationError(
                        _("Gross weight too high (max. value=%.2f)") % weight_max
                    )

    def capture_image_weight(self):
        # TODO
        # * camera.get_image() protection from camera not responding issue
        # * Absolute path for parent_folder (form res_config_settings)
        # * Relative path not translatable (or remove it)
        camera = self.env.company.picking_operations_camera_id
        camera.get_image()
        if self.picking_vehicle_id.license_plate:
            if not self.weight_image:
                self.weight_image = camera.last_image
                capute_date = fields.Datetime.now().strftime('%Y/%m/%d/')
                capute_datetime = fields.Datetime.now().strftime('%H%M%S')
                parent_folder = (_("/weight_images/%s")) % (capute_date)
                try:
                    os.makedirs(parent_folder)
                except OSError:
                    # In the case that the folders already exist
                    pass
                path_image = ("%s%s-%s.jpg") % \
                    (parent_folder, self.picking_vehicle_id.license_plate, capute_datetime)
                with open(path_image, "wb") as fh:
                    fh.write(base64.decodebytes(self.weight_image))
        else:
            raise ValidationError(
                _("It is necessary to assign a vehicle to perform this operation.")
            )

    def capture_weight(self):
        scale = self.env.company.picking_operations_scale_id
        if scale:
            weight = scale.get_last_weight()
            return scale.uom_id._compute_quantity(weight, self.product_uom)
        else:
            raise ValidationError(
                _("It is necessary to assign a scale to perform this operation.")
            )

    def capture_tare(self):
        self.tare = self.capture_weight()
        self._onchange_tare()

    def capture_gross(self):
        self.gross_weight = self.capture_weight()
        self._onchange_gross_weight()

    def _move_weight_open_wizard(self, move_id):
        return {
            'name': _('Move Weight'),
            'res_model': 'stock.move.weight.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': move_id,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def move_weight(self):
        # TODO merge with stock.picking.move_weight()
        self.ensure_one()
        Wizard = self.env['stock.move.weight.wizard']

        new = Wizard.create({
            'move_id': self.id,
            'net_weight': self.net_weight,
            'theoretical_qty': self.theoretical_qty,
            'picking_id': self.picking_id.id,
            'company_id': self.picking_id.company_id.id
        })

        return self._move_weight_open_wizard(new.id)

    def action_view_classification(self):
        self.ensure_one()
        Wizard = self.env['stock.move.weight.wizard']

        weight_selection = (
            self.picking_id.picking_classification_ids.mapped("weight_selection")[0]
            or
            False
        )

        new = Wizard.create({
            'move_id': self.id,
            'picking_id': self.picking_id.id,
            'product_id': self.product_id.id,
            'weight_selection': weight_selection,
            'theoretical_qty': self.theoretical_qty,
            'net_weight': self.net_weight,
            'company_id': self.company_id.id,
            'vehicle_id': self.picking_vehicle_id.id
        })

        return {
            'name': _('Move Weight'),
            'res_model': 'stock.move.weight.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref(
                "stock_picking_mgmt_weight.view_stock_move_weight_wizard_inherit_readonly_form_weight"
            ).id,
            'res_id': new.id,
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {'stock_move_line_weight': True}
        }
