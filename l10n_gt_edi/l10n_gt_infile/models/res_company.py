from gt_sat_infile_api.login import LoginHandler

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class Company(models.Model):
    _inherit = "res.company"

    infile_user_sign = fields.Char(string="Alias Firma")
    infile_sign_key = fields.Char(string="Token Firma")
    infile_user_api = fields.Char(string="Usuario")
    infile_api_key = fields.Char(string="Llave")

    def generate_login_handler(self):
        if not all(
            [
                self.infile_user_sign,
                self.infile_sign_key,
                self.infile_user_api,
                self.infile_api_key,
            ]
        ):
            raise ValidationError(
                _("Login INFILE credentials not filled for the company '%s'") % self.name
            )
        return LoginHandler(
            user_sign=self.infile_user_sign,
            sign_key=self.infile_sign_key,
            user_api=self.infile_user_api,
            api_key=self.infile_api_key,
        )
