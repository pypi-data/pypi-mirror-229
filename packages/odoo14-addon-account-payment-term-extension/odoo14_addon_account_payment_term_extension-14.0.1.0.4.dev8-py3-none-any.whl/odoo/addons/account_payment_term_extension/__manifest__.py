# Copyright 2013-2016 Camptocamp SA (Yannick Vaucher)
# Copyright 2015-2020 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016-2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Payment Term Extension",
    "version": "14.0.1.0.3",
    "category": "Accounting & Finance",
    "summary": "Adds rounding, months, weeks and multiple payment days "
    "properties on payment term lines",
    "development_status": "Production/Stable",
    "author": "Camptocamp,"
    "Tecnativa,"
    "Agile Business Group, "
    "Odoo Community Association (OCA)",
    "maintainer": "OCA",
    "website": "https://github.com/OCA/account-payment",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": ["security/ir.model.access.csv", "views/account_payment_term.xml"],
    "demo": ["demo/account_demo.xml"],
    "installable": True,
}
