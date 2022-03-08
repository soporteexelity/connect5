from odoo import fields, models


class Tax(models.Model):
    _inherit = "account.tax"

    codigo_unidad_gravable = fields.Integer()
    code_name = fields.Char(
        string="Tax Name (INFILE)",
    )
