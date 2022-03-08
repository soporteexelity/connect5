from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_default_journal(self):
        return self.env["account.move"]._search_default_journal(  # pylint: disable=protected-access
            ["sale"]
        )

    journal_id = fields.Many2one(
        comodel_name="account.journal",
        domain="[('type', '=', 'sale')]",
        default=_get_default_journal,
    )

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        journal = (
            self.env["account.move"]  # pylint: disable=protected-access
            .with_context(default_move_type="out_invoice")
            ._get_default_journal()  # pylint: disable=protected-access
        )
        invoice_vals["journal_id"] = (self.journal_id.id or journal.id,)
        return invoice_vals
