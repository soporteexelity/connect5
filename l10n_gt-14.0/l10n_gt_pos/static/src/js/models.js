odoo.define("pos_ticket_invoice_customer", function (require) {
    'use strict';
    const models = require('point_of_sale.models');
    var rpc = require('web.rpc');


    var posModelSuper = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        // @Override
        push_and_invoice_order: async function (order) {
            var order_id = await posModelSuper.push_and_invoice_order.apply(this, [order]);

            await rpc.query({
                model: 'pos.order',
                method: 'get_account_move_infile_xml_uuid',
                args: [order_id],
            }).then(function (uuid) {
                order.infile_xml_uuid = uuid;
                console.log(uuid)
            });

            return order_id;
        },
    });
});
