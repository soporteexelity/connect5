import uuid

from gt_sat_infile_api.parser import generate_and_parse_query

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

INFILE_PDF_LINK = "https://report.feel.com.gt/ingfacereport/ingfacereport_documento?uuid="


class AccountMove(models.Model):
    _inherit = "account.move"

    infile_status = fields.Selection(
        [
            ("not_sent", "Not sent"),
            ("done", "Sent successfully"),
            ("error", "Sent with errors"),
            ("annulled", "Annulled"),
            ("annulled_error", "Annulled Error"),
        ],
        string="INFILE status",
        copy=False,
        default="not_sent",
    )
    infile_certified_datetime = fields.Datetime(
        string="Certified at",
        copy=False,
        readonly=True,
    )
    infile_xml_uuid = fields.Char(
        string="UUID",
        copy=False,
    )
    infile_pdf_link = fields.Char(
        string="Link to pdf",
        compute="_compute_pdf_link",
        readonly=True,
    )
    infile_uuid = fields.Char(
        string="INFILE UUID",
        copy=False,
    )
    number_invoice_xml = fields.Char(
        string="Numero de Factura",
        copy=False,
    )
    serial_number = fields.Char(
        copy=False,
    )

    def found_xml_file(self):
        if self.dte_type_id.code == "FCAM":
            certificate = self.env["ir.attachment"].search(
                [("name", "=", f"FCAM_{self.name}.xml")], limit=1
            )
        elif self.dte_type_id.code == "FACT":
            certificate = self.env["ir.attachment"].search(
                [("name", "=", f"FACT_{self.name}.xml")], limit=1
            )
        elif self.dte_type_id.code == "FPEQ":
            certificate = self.env["ir.attachment"].search(
                [("name", "=", f"FPEQ_{self.name}.xml")], limit=1
            )
        elif self.dte_type_id.code == "FCAP":
            certificate = self.env["ir.attachment"].search(
                [("name", "=", f"FCAP_{self.name}.xml")], limit=1
            )
        elif self.dte_type_id.code == "NCRE":
            certificate = self.env["ir.attachment"].search(
                [("name", "=", f"NCRE_{self.name}.xml")], limit=1
            )
        return certificate

    def _compute_invoice_number_in_xml(self):
        certificate = self.found_xml_file()
        if not certificate:
            return
        text = str((certificate.raw).decode("utf-8"))
        if "dte:NumeroAutorizacion" in text:
            index = text.index("dte:NumeroAutorizacion")
            number_invoice_xml = str(text[index + 31 : index + 41])
            self.number_invoice_xml = number_invoice_xml
        else:
            self.number_invoice_xml = 0

    def _compute_serial_number(self):
        certificate = self.found_xml_file()
        if not certificate:
            return
        text = str((certificate.raw).decode("utf-8"))
        if "Serie" in text:
            index = text.index("Serie")
            serial_number = str(text[index + 7 : index + 15])
            self.serial_number = serial_number
        else:
            self.serial_number = 0
        
    
    def write_serial_and_invoice_number(self):
        for move in self:
            if move.move_type == 'out_invoice':
                move._compute_invoice_number_in_xml()
                move._compute_serial_number()
            else:
                return

    @api.depends("infile_xml_uuid")
    def _compute_pdf_link(self):
        """Compute the link to the invoice pdf report"""
        for move in self:
            move.infile_pdf_link = f"{INFILE_PDF_LINK}{move.infile_xml_uuid}"

    def _check_can_annullate_sat(self):
        if self.infile_status and self.infile_status not in ("done", "annulled_error", "error"):
            raise ValidationError(
                _(
                    "The XML of annulation for the invoice %(invoice_name)s "
                    "has already been sent to SAT"
                )
                % {
                    "invoice_name": self.name,
                }
            )

    def _check_can_post_sat(self):
        if self.infile_status and self.infile_status not in (
            "not_sent",
            "error",
        ):
            raise ValidationError(
                _("The XML of invoice %(invoice_name)s has already been sent to SAT")
                % {
                    "invoice_name": self.name,
                }
            )

    def send_xml_to_sat(self, annulled=False):
        """Implemented Function to send the XML string to SAT through INFILE"""
        if annulled:
            self._check_can_annullate_sat()
        else:
            self._check_can_post_sat()

        login_handler = self.company_id.generate_login_handler()
        xml_string = self.get_xml_string(annulled)
        if not annulled:
            self.infile_uuid = uuid.uuid1()
        return generate_and_parse_query(
            auth_headers=login_handler,
            identifier=self.infile_uuid,
            xml=xml_string,
        )

    def post_send_xml_to_sat(self, response, annulled=False):
        """Actions to do after sent in the SAT"""
        if not response.get("res"):
            self._log_infile_errors(response, "error")
            
            return
        xml_certified = response["xml"]
        if not annulled:
            self.infile_xml_uuid = response["uuid"]
        fname = self.get_fname_xml(annulled)
        self.generate_attachment_from_xml_string(xml_certified, fname)
        self.infile_status = "annulled" if annulled else "done"

    def action_post(self):
        """Post/Validate the documents"""
        res = super().action_post()
        self.write_serial_and_invoice_number()
        return res

    def _log_infile_errors(self, result, status):
        errors_list = [error["mensaje_error"] for error in result["errors"]]
        self.message_post(subject=_("Error sending XML:"), body="\n".join(errors_list))
        self.infile_status = status

