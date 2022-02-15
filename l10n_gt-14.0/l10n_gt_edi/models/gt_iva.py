from odoo import fields, models


class IvaAffiliation(models.Model):
    _name = "gt.iva"
    _description = "IVA"

    name = fields.Char()
    code = fields.Char()
