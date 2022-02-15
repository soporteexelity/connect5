from odoo import fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    journal_id = fields.Many2one(
        comodel_name="account.journal",
    )

    def get_account_move_infile_xml_uuid(self):
        return self.account_move.infile_xml_uuid

    def _prepare_invoice_vals(self):
        invoice_vals = super()._prepare_invoice_vals()
        invoice_vals["dte_type_id"] = (self.session_id.config_id.dte_type_id.id,)
        invoice_vals["journal_id"] = (
            self.journal_id.id or self.session_id.config_id.invoice_journal_id.id,
        )
        return invoice_vals
