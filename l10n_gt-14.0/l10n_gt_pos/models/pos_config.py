from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    def _default_dte_type(self):
        return self.env["gt.dte.type"].search(
            [
                ("id", "=", 1),
                ("name", "=", "Factura"),
            ],
            limit=1,
        )

    dte_type_id = fields.Many2one(
        comodel_name="gt.dte.type",
        string="Tipo de DTE",
        default=_default_dte_type,
    )
