from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    iva_affiliation_id = fields.Many2one(
        comodel_name="gt.iva",
    )
    codigo_establecimiento = fields.Integer()
    default_dte_type_id = fields.Many2one(
        comodel_name="gt.dte.type",
    )
