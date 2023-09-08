# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Odoo Implementation - Infrastructure Integration",
    "version": "14.0.2.1.0",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": [
        "ssi_odoo_implementation",
        "ssi_infrastructure_server",
    ],
    "data": [
        "views/odoo_implementation_views.xml",
    ],
    "demo": [],
}
