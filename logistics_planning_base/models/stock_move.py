# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, models, fields
from odoo.osv import expression


class StockMove(models.Model):
    _inherit = 'stock.move'

    logistics_schedule_id = fields.Many2one('logistics.schedule', copy=False)
    logistics_schedule_disabled = fields.Boolean(copy=False)

    def _prepare_name_get(self):
        return (
            "%s (%.3f %s)"
            %
            (self.picking_id.name, self.product_uom_qty, self.product_uom.name)
        )

    def name_get(self):
        if self.env.context.get("logistics_schedule_view", False):
            result = []
            for rec in self:
                # name = (
                #     "%s (%.3f %s)"
                #     %
                #     (rec.picking_id.name, rec.product_uom_qty, rec.product_uom.name)
                # )
                # result.append((rec.id, name))
                result.append((rec.id, rec._prepare_name_get()))
            return result
        else:
            return super().name_get()

    @api.model
    def _name_search(self, name, args=None, operator="ilike", limit=100, name_get_uid=None):
        """
        If we comes from logistics schedule, we add picking and product search,
        and sorted by picking
        """
        if self.env.context.get("logistics_schedule_view", False) and name:
            args = args or []
            domain = [
                "|",
                ("picking_id.name", operator, name),
                "|",
                ("product_id.default_code", operator, name),
                ("product_id.name", operator, name),
            ]
            rec = self._search(
                expression.AND([domain, args]), limit=limit,
                access_rights_uid=name_get_uid,
            )
            return models.lazy_name_get(
                self.browse(rec).with_user(name_get_uid).sorted(key=lambda x: (x.picking_id.name))
            )
        else:
            return super()._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
    