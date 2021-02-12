# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)
from odoo import fields, models, _
from datetime import datetime
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):

        if self.picking_type_id.auto_create_lot:
            for line in self.move_line_ids.filtered(
                lambda x: (
                    not x.lot_id
                    and not x.lot_name
                    and x.product_id.tracking != "none"
                    and x.product_id.auto_create_lot
                )
            ):
                # lot_name = Id.Product + Partner.Ref + Date + 1/0(ECO)
                # Code Product = 
                # Stock_move_line.product_id --> Product_product.default_code
                if line.product_id.default_code:
                    product_code = line.product_id.default_code
                else:
                    msg = _("Error when trying to autolot: Cannot "
                            "find the internal reference of product"
                            " %s") % line.product_id.name
                    raise UserError(msg)

                # If exist: 
                # PartnerRef = stock_picking.partner_id --> res_partner.ref
                if self.partner_id and self.partner_id.ref:
                    parter_code = self.partner_id.ref
                elif self.partner_id:
                    raise UserError(_("Error when trying to autolot: "
                                      "Cannot find the internal "
                                      "reference of partner."))
                else:
                    raise UserError(_("Error when trying to autolot: "
                                      "Cannot find the partner."))

                # Current date format YYYYMMDD
                str_date = datetime.today().strftime('%Y%m%d')

                # Search value of ExceptionEcoProduct
                eco_partner_ids = line.product_id.exception_eco_partner_ids.ids
                str_eco = "0" if self.partner_id.id in eco_partner_ids else "1"

                lot_name = "%s%s%s%s" % (product_code, parter_code,
                                         str_date, str_eco)

                # Search if exists this lot
                production_lot = self.env["stock.production.lot"].search([
                    ("name", "=", lot_name)
                ])
                if not production_lot:
                    production_lot = self.env["stock.production.lot"].create({
                        'name': lot_name,
                        'product_id': line.product_id.id,
                        'company_id': line.company_id.id,
                    })
                line.lot_id = production_lot.id

        return super().button_validate()
