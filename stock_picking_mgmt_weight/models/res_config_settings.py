# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    picking_operations_scale_id = fields.Many2one(
        comodel_name='scale.scale',
        related='company_id.picking_operations_scale_id',
        string='IN / OUT Picking Operations for Scale',
        readonly=False,
        required=True
    )
    picking_operations_camera_id = fields.Many2one(
        comodel_name='camera.camera',
        related='company_id.picking_operations_camera_id',
        string='Cameras for Scale',
        readonly=False,
        required=True
    )
    # picking_operations_asm_id = fields.Many2one(
    #     comodel_name='asm.asm',
    #     related='company_id.picking_operations_asm_id',
    #     string='ASM for Scale',
    #     readonly=False,
    #     required=True
    # )


class ResCompany(models.Model):
    _inherit = 'res.company'

    picking_operations_scale_id = fields.Many2one(
        comodel_name='scale.scale',
        string='IN / OUT Picking Operations for Scale'
    )
    picking_operations_camera_id = fields.Many2one(
        comodel_name='camera.camera',
        string='Cameras for Scale'
    )
    # picking_operations_asm_id = fields.Many2one(
    #     comodel_name='asm.asm',
    #     string='ASM for Scale'
    # )
