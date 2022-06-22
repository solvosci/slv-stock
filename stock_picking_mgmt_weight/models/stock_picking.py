# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, api, _
from datetime import date, datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    type_code = fields.Selection(related="picking_type_id.code")
    type_scale = fields.Boolean(related="picking_type_id.scale")

    vehicle_id = fields.Many2one(
        'vehicle.vehicle',
        string='Vehicle',
        ondelete="restrict",
    )
    # TODO related, computed, a regular field?
    # carrier_vehicle_id = fields.Many2one(related="vehicle_id.carrier_id")
    carrier_vehicle_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_carrier_vehicle_id",
        store=True,
        readonly=False,
        domain="[('is_company', '=', True)]",
        ondelete="restrict",
    )
    towing_license_plate = fields.Char()
    container_number = fields.Char(
        help="A text representing container no. for an outgoing operation",
    )
    container_tare = fields.Float(
        digits="Product Unit of Measure",
        help="For an outgoing operation, the related container tare",
    )
    container_gross_weight = fields.Float(
        digits="Product Unit of Measure",
        compute="_compute_container_weights",
    )
    container_vgm_weight = fields.Float(
        digits="Product Unit of Measure",
        compute="_compute_container_weights",
    )
    container_safety = fields.Char(
        help="A text representing container safety data"
        " for an outgoing operation",
    )
    operator_id = fields.Many2one(
        string="Operator",
        comodel_name="res.partner",
        domain="[('is_company', '=', True)]",
        ondelete="restrict",
    )
    driver_id = fields.Many2one(
        string="Driver",
        comodel_name="res.partner",
        domain="[('is_company', '=', False)]",
        ondelete="restrict",
    )

    picking_classification_ids = fields.One2many(
        comodel_name='stock.picking.classification',
        inverse_name='picking_id'
    )
    classification_picking_id = fields.Many2one(
        'stock.picking',
        string='Classification picking',
        readonly=True,
        help="For a scale picking, this field points to the picking generated"
        " by classification process",
    )
    related_picking_id = fields.Many2one(
        'stock.picking',
        string='Scale related picking',
        readonly=True,
        help="For a certain picking, this field points to original scale"
        " picking, if exists",
    )
    classification_purchase_order_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Classification Order",
        readonly=True,
    )
    origin_purchase_order_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Origin Order",
        related="classification_purchase_order_id.related_order_id"
    )

    @api.depends("vehicle_id")
    def _compute_carrier_vehicle_id(self):
        for picking in self:
            picking.carrier_vehicle_id = (
                picking.vehicle_id
                and picking.vehicle_id.carrier_id
                or False
            )

    def _compute_container_weights(self):
        for picking in self:
            gross_weight = sum(
                picking.move_ids_without_package.mapped("quantity_done")
            )
            picking.container_gross_weight = gross_weight
            picking.container_vgm_weight = (
                gross_weight + picking.container_tare
            )

    def move_weight(self):
        # TODO merge with stock.move.move_weight()
        self.ensure_one()
        Wizard = self.env['stock.move.weight.wizard']

        move_id = self.move_ids_without_package

        new = Wizard.create({
            'move_id': move_id.id,
            'net_weight': move_id.net_weight,
            'theoretical_qty': move_id.theoretical_qty,
            'picking_id': self.id,
            'company_id': self.company_id.id
        })

        return {
            'name': _('Move Weight'),
            'res_model': 'stock.move.weight.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': new.id,
            'target': 'new',
            'type': 'ir.actions.act_window'
        }

    def get_datetime_now(self):
        return fields.Datetime.now()
