from odoo import fields, models


class DteType(models.Model):
    _name = "gt.dte.type"
    _description = "DTE Type"

    name = fields.Char()
    code = fields.Char()
    general_move_type = fields.Selection(
        [
            ("invoice", "Invoice"),
            ("receipt", "Receipt"),
            ("refund", "Refund"),
        ]
    )
    frases_ids = fields.Many2many(
        comodel_name="gt.frase",
    )
    active = fields.Boolean(
        default=True,
    )
