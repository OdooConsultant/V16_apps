# -*- coding: utf-8 -*-
from odoo import models, fields


class Purchase(models.Model):
    _inherit = 'purchase.order'

    import_logs = fields.Text()