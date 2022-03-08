from odoo import fields, models


class Frase(models.Model):
    _name = "gt.frase"
    _description = "Frase"

    type = fields.Integer()
    name = fields.Char(
        string="Type",
    )
    code = fields.Integer()
    setting = fields.Char(
        string="Scenary",
    )
