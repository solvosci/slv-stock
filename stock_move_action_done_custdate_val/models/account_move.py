# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models

import pytz


class AccountMove(models.Model):
    _inherit = "account.move"

    def date_update_from_datetime(self, new_datetime):
        tz = pytz.timezone(self.env.user.tz) or pytz.utc
        new_datetime_mod = fields.Date.to_string(pytz.utc.localize(
            fields.Datetime.from_string(new_datetime)
        ).astimezone(tz))
        self.write({"date": new_datetime_mod})
