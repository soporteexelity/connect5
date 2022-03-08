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
        readonly=True,
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
        readonly=True,
    )
    infile_pdf_link = fields.Char(
        string="Link to pdf",
        compute="_compute_pdf_link",
        readonly=True,
    )
    infile_uuid = fields.Char(
        string="INFILE UUID",
        readonly=True,
        copy=False,
    )

    @api.depends("infile_xml_uuid")
    def _compute_pdf_link(self):
        """Compute the link to the invoice pdf report"""
        for move in self:
            move.infile_pdf_link = f"{INFILE_PDF_LINK}{move.infile_xml_uuid}"

    def _check_can_annullate_sat(self):
        if self.infile_status and self.infile_status not in ("done", "annulled_error"):
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
        self.infile_xml_uuid = response["uuid"]
        fname = self.get_fname_xml(annulled)
        self.generate_attachment_from_xml_string(xml_certified, fname)
        self.infile_status = "annulled" if annulled else "done"

    def _log_infile_errors(self, result, status):
        errors_list = [error["mensaje_error"] for error in result["errors"]]
        self.message_post(subject=_("Error sending XML:"), body="\n".join(errors_list))
        self.infile_status = status
