# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields


class FcdDocument(models.Model):
    _name ='fcd.document'
    _description = 'fcd.document'

    name = fields.Char(required=True)
    fcd_document_line_ids = fields.One2many(comodel_name='fcd.document.line', inverse_name='fcd_document_id')
    scientific_name = fields.Char(related='product_id.scientific_name')
    fao = fields.Char()
    fao_zone_id = fields.Many2one('fcd.fao.zone')
    subzone_id = fields.Many2one('fcd.fao.subzone')
    specific_lot = fields.Char()
    internal_lot_id = fields.Many2one('stock.production.lot')
    packaging_date = fields.Date()
    expiration_date = fields.Date()
    fishing_gear_id = fields.Many2one('fcd.fishing.gear') 
    production_method_id = fields.Many2one('fcd.production.method')
    presentation_id = fields.Many2one('fcd.presentation', related='product_id.fcd_presentation_id')
    ship_id = fields.Many2one('fcd.ship')
    ship_license_plate = fields.Char(related='ship_id.license_plate')
    country_id = fields.Many2one('res.country', related='ship_id.country_id', string='Origin')
    tide_start_date = fields.Date()
    tide_end_date = fields.Date()
    packing = fields.Char()
    sanity_reg = fields.Char()

    product_id = fields.Many2one('product.product')
    partner_id = fields.Many2one('res.partner', string="Supplier")
    commercial_margin = fields.Char()

    qc_inspection_ids = fields.One2many('qc.inspection', 'fcd_document_id', string='Inspection')
    created_inspections = fields.Integer(compute="_compute_count_inspections", string="Total")
    done_inspections = fields.Integer(compute="_compute_count_inspections", string="Done inspections")
    passed_inspections = fields.Integer(compute="_compute_count_inspections", string="OK")
    failed_inspections = fields.Integer(compute="_compute_count_inspections", string="Failed")

    notes = fields.Text()
    notes_fishing = fields.Text()
    notes_quality = fields.Text()

    def _compute_count_inspections(self):
        for record in self:
           record.created_inspections = len(record.qc_inspection_ids)
           record.done_inspections = len(record.qc_inspection_ids.filtered(lambda x: x.state in ['success', 'failed']))
           record.passed_inspections = len(record.qc_inspection_ids.filtered(lambda x: x.state == 'success'))
           record.failed_inspections = len(record.qc_inspection_ids.filtered(lambda x: x.state == 'failed'))
