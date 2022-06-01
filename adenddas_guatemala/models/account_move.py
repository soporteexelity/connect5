from odoo import _, api, fields, models
from gt_sat_api import DTE, Frase, AnulacionDTE
from odoo.exceptions import ValidationError
from gt_sat_api.parsers import dte_to_xml, dte_to_xml_annulled
from pytz import timezone
from decimal import *


class AccountMove(models.Model):
    _inherit = 'account.move' 

    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
    )
    transport = fields.Char(
        string='Transporte',
    )
    modelo = fields.Char()

    

    def generate_dte_xml(self, dte):
        annulled = isinstance(dte, AnulacionDTE)
        xml_str = dte_to_xml_annulled(dte) if annulled else dte_to_xml(dte)
        if not annulled:
            tag_adendda = ("<dte:Adenda>" '\n'
                        "<Agente>%(Agente)s</Agente>" '\n'
                        "<Vencimiento>%(Vencimiento)s</Vencimiento>" '\n'
                        "<NumeroInterno>%(NumeroInterno)s</NumeroInterno>" '\n'
                        "</dte:Adenda>"
            ) % {"Agente": self.invoice_user_id.name, "Vencimiento": self.invoice_date_due, "NumeroInterno": self.name}
            index_final = xml_str.find("</dte:DTE>")
            dte_end = xml_str.find("</dte:SAT>")
            if self.invoice_payment_term_id:
                index_adendda_tag = tag_adendda.find("</dte:Adenda>")
                tag_adendda_payment_term = ("<CondicionesPago>%(CondicionesPago)s</CondicionesPago>" '\n') % {"CondicionesPago": self.invoice_payment_term_id.name}
                tag_adendda = tag_adendda[:index_adendda_tag] + tag_adendda_payment_term + tag_adendda[index_adendda_tag:]
            if self.partner_id.ref:
                index_adendda_tag = tag_adendda.find("</dte:Adenda>")
                tag_adendda_codigo_cliente = ("<CodigoCliente>%(CodigoCliente)s</CodigoCliente>" '\n') % {"CodigoCliente": self.partner_id.ref}
                tag_adendda = tag_adendda[:index_adendda_tag] + tag_adendda_codigo_cliente + tag_adendda[index_adendda_tag:]
            if self.sale_order_id:
                index_adendda_tag = tag_adendda.find("</dte:Adenda>")
                tag_adendda_sale_order = ("<NoOCCliente>%(NoOcCliente)s</NoOCCliente>" '\n'
                                        "<FechaPedido>%(FechaPedido)s</FechaPedido>" '\n'
                                        "<NoPedido>%(NoPedido)s</NoPedido>" '\n'
                ) % {"NoOcCliente": self.sale_order_id.name, "FechaPedido": self.sale_order_id.date_order, "NoPedido": self.sale_order_id.name}
                tag_adendda = tag_adendda[:index_adendda_tag] + tag_adendda_sale_order + tag_adendda[index_adendda_tag:]
            if self.transport:
                index_adendda_tag = tag_adendda.find("</dte:Adenda>")
                tag_adendda_transporte = ("<Transporte>%(Transporte)s</Transporte>" '\n') % {"Transporte": self.transport}
                tag_adendda = tag_adendda[:index_adendda_tag] + tag_adendda_transporte + tag_adendda[index_adendda_tag:]
            
            if self.tax_totals_json:
                if "TotalMontoImpuesto" in xml_str:
                    index_total_monto_impuesto = xml_str.index("TotalMontoImpuesto")
                    index2 = xml_str.index("</dte:TotalImpuestos>")
                    total_monto_impuesto = ("%(ImpuestoTotal)s")  % {"ImpuestoTotal": Decimal(self.amount_tax_signed).quantize(Decimal("0.01"), rounding = "ROUND_HALF_UP")}
                    if self.move_type in ["in_refund", "out_refund"]:
                        total_monto_impuesto = ("%(ImpuestoTotal)s")  % {"ImpuestoTotal": -(Decimal(self.amount_tax_signed).quantize(Decimal("0.01"), rounding = "ROUND_HALF_UP"))}
                    xml_str = xml_str[:index_total_monto_impuesto+20] + total_monto_impuesto + xml_str[index2-14:]
            xml_str = xml_str[:index_final + 10] + tag_adendda + xml_str[dte_end:]
            fname = self.get_fname_xml(annulled)
            self.generate_attachment_from_xml_string(xml_str, fname)
        else:
            fname = self.get_fname_xml(annulled)
            self.generate_attachment_from_xml_string(xml_str, fname)