from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    use_in_sat = fields.Boolean(
        string="Send invoices to SAT",
        default=False,
    )
