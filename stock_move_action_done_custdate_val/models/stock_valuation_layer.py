# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    def create_date_update(self, new_date):
        if self:
            sql = """
            UPDATE %s
            SET create_date='%s'
            WHERE id in %s
            """
            if len(self) > 1:
                ids_str = str(tuple(self.ids))
            else:
                ids_str = "(%d)" % self.id
            create_date = new_date
            self.env.cr.execute(sql % (self._table, create_date, ids_str))
