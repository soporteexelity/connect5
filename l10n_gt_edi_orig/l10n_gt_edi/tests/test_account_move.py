from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestAccountMove(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env["res.company"].create(
            {
                "name": "Test Company",
                "street": "Street",
                "city": "City",
                "state_id": cls.env.ref("base.state_gt_gua").id,
                "zip": "01001",
                "country_id": cls.env.ref("base.gt").id,
                "vat": "9847847",
                "company_registry": "Test Company S.A.",
                "currency_id": cls.env.ref("base.GTQ").id,
                "iva_affiliation_id": cls.env.ref("l10n_gt_edi.gt_iva_affil_gen").id,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "street": "Street",
                "city": "City",
                "state_id": cls.env.ref("base.state_gt_gua").id,
                "zip": "01001",
                "country_id": cls.env.ref("base.gt").id,
                "vat": "76365204",
            }
        )
        cls.invoice = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "dte_type_id": cls.env.ref("l10n_gt_edi.gt_dte_type_fact").id,
                "line_ids": [
                    (
                        0,
                        None,
                        {
                            "name": "Test Product",
                            "product_id": cls.env.ref("product.product_product_4").id,
                            "quantity": 1,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )

    def test_account_move_create_dte(self):
        self.invoice.generate_dte()
        # TODO test dte generation  # pylint: disable=fixme

    def test_prevent_send_twice(self):
        self.invoice.action_post()
        with self.assertRaises(UserError), self.cr.savepoint():
            self.invoice.action_post()

    def test_missing_fields_in_dte_generation(self):
        raise NotImplementedError()

    def test_setted_user_timezone(self):
        raise NotImplementedError()

    def test_get_dte_emisor(self):
        raise NotImplementedError()

    def test_get_dte_receptor(self):
        raise NotImplementedError()

    def test_get_dte_items(self):
        raise NotImplementedError()

    def test_get_dte_complements(self):
        raise NotImplementedError()

    def test_get_xml(self):
        raise NotImplementedError()

    def test_re_create_xml(self):
        raise NotImplementedError()

    def test_cancel_dte(self):
        raise NotImplementedError()
