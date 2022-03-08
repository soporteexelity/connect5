from odoo import models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    def _prepare_default_reversal(self, move):
        values = super()._prepare_default_reversal(move)
        if move.emision_datetime and move.infile_xml_uuid:
            values["origin_date"] = move.emision_datetime.date()
            values["origin_uuid"] = move.infile_xml_uuid
            values["dte_type_id"] = self.env.ref("l10n_gt_edi.gt_dte_type_ncre").id
        return values
