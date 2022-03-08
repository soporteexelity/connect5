{
    "name": "L10N GT EDI",
    "version": "14.0.0.1.0",
    "author": "HomebrewSoft",
    "website": "https://homebrewsoft.dev",
    "license": "OPL-1",
    "depends": [
        "account",
        "sale",
        "l10n_gt",
    ],
    "external_dependencies": {
        "python": [
            "gt_sat_api",
        ],
    },
    "data": [
        # security
        "security/ir.model.access.csv",
        "security/res_groups.xml",
        # data
        "data/dte_types.xml",
        "data/frases.xml",
        "data/iva_affiliations.xml",
        "data/server_actions.xml",
        # reports
        # views
        "views/account_journal.xml",
        "views/account_move.xml",
        "views/account_tax.xml",
        "views/gt_dte_type.xml",
        "views/gt_frases.xml",
        "views/res_company.xml",
        "views/sale_order.xml",
    ],
}
