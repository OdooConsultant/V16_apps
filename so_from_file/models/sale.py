# -*- coding: utf-8 -*-
from odoo import models, fields


class Purchase(models.Model):
    _inherit = 'sale.order'

    import_logs = fields.Text()
