# Copyright 2016 Chafique DELLI @ Akretion
# Copyright 2016-Today: GRAP (http://www.grap.coop)
# Copyright Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Invoice - Supplier Info Update",
    "summary": "In the supplier invoice, automatically updates all products "
    "whose unit price on the line is different from "
    "the supplier price",
    "version": "16.0.1.0.1",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Akretion, GRAP, Odoo Community Association (OCA)",
    "maintainers": ["legalsylvain"],
    "license": "AGPL-3",
    "installable": True,
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_invoice_view.xml",
        "wizard/wizard_update_invoice_supplierinfo.xml",
    ],
}
