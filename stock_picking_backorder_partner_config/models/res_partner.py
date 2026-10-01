# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields

PARTIAL_POLICY_SELECTION = [
        ('by_default', 'By default'),
        ('ask', 'Ask'),
        ('always', 'Always create'),
        ('never', 'Never create'),
    ]

class ResPartner(models.Model):
    _inherit = "res.partner"

    create_partial_reception = fields.Selection(
        PARTIAL_POLICY_SELECTION,
        'Policy for the creation of partial receptions', required=True, default='always',
        help="When validating a transfer:\n"
             " * By default: it is used as indicated in the type of operation\n"
             " * Ask: users are asked to choose if they want to make a backorder for remaining products\n"
             " * Always create: a backorder is automatically created for the remaining products\n"
             " * Never create: remaining products are cancelled")

    create_partial_delivery = fields.Selection(
        PARTIAL_POLICY_SELECTION,
        'Policy for the creation of partial delivery', required=True, default='always',
        help="When validating a transfer:\n"
             " * By default: it is used as indicated in the type of operation\n"
             " * Ask: users are asked to choose if they want to make a backorder for remaining products\n"
             " * Always create: a backorder is automatically created for the remaining products\n"
             " * Never create: remaining products are cancelled")
