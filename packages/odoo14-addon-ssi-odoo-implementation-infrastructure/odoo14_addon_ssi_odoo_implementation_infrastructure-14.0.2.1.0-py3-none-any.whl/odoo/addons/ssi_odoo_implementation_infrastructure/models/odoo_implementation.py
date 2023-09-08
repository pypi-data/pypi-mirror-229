# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class OdooImplementation(models.Model):
    _name = "odoo_implementation"
    _inherit = [
        "odoo_implementation",
    ]

    server_id = fields.Many2one(
        string="Server",
        comodel_name="server",
    )
