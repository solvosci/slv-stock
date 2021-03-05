# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)
from odoo import fields, models, _
from datetime import datetime
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def create_lot_product_supplier_date_eco(self):
        # lot_name = Id.Product + Partner.Ref + Date + 1/0(ECO)
        # Code Product =
        # Stock_move_line.product_id --> Product_product.default_code
        if self.product_id.default_code:
            product_code = self.product_id.default_code
        else:
            msg = _("Error when trying to autolot: Cannot "
                    "find the internal reference of product"
                    " %s") % self.product_id.name
            raise UserError(msg)

        # If exist:
        # PartnerRef = stock_picking.partner_id --> res_partner.ref
        partner_id = self.picking_id.partner_id
        if partner_id and partner_id.ref:
            parter_code = partner_id.ref
        elif partner_id:
            raise UserError(_("Error when trying to autolot: "
                              "Cannot find the internal "
                              "reference of partner."))
        else:
            raise UserError(_("Error when trying to autolot: "
                              "Cannot find the partner."))

        # Current date format YYYYMMDD
        str_date = datetime.today().strftime('%Y%m%d')

        # Search value of ExceptionEcoProduct
        eco_partner_ids = self.product_id.exception_eco_partner_ids.ids
        str_eco = "0" if partner_id.id in eco_partner_ids else "1"

        lot_name = "%s%s%s%s" % (product_code, parter_code, str_date, str_eco)

        # Search if exists this lot
        production_lot = self.env["stock.production.lot"].search([
            ("name", "=", lot_name)
        ])
        if not production_lot:
            production_lot = self.env["stock.production.lot"].create({
                'name': lot_name,
                'product_id': self.product_id.id,
                'company_id': self.company_id.id or self.env.company.id,
            })
        return production_lot

