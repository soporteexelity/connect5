from odoo import _, api, fields, models
from decimal import *

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line' 

    modelo = fields.Char(
        compute="_compute_product_model",
    )
    monto_gravable = fields.Float(
        compute="_compute_monto_gravable",
    )
    impuesto = fields.Float(
        compute="_compute_impuesto",
    )

    @api.depends("price_subtotal")
    def _compute_monto_gravable(self):
        for line in self:
            line.monto_gravable = float(Decimal(line.price_subtotal).quantize(Decimal("0.01"), rounding = "ROUND_HALF_UP"))


    @api.depends("monto_gravable", "price_unit", "quantity")
    def _compute_impuesto(self):
        for line in self:
            total = float(Decimal(line.price_unit).quantize(Decimal("0.01"), rounding = "ROUND_HALF_UP")) * line.quantity
            impuesto = total - line.monto_gravable
            line.impuesto = float(Decimal(impuesto).quantize(Decimal("0.01"), rounding = "ROUND_HALF_UP"))

    def _compute_product_model(self):
        for line in self:
            index_default_code = line.name.find("]")
            description = line.name[index_default_code + 1:] 
            line.modelo = description + " @ " + line.product_id.default_code
