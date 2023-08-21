# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    sequence_id = fields.Many2one('ir.sequence', string="Sequence")

    @api.model
    def create(self, vals):
        if ('sequence_id' not in vals or not vals.get('sequence_id')) and vals.get('default_code'):
            vals['sequence_id'] = self.env['ir.sequence'].create({
                'name': vals['name'],
                'prefix': vals['default_code'] + '/', 'padding': 4,
                'code': vals['default_code'],
                'company_id': vals.get('company_id') or self.env.company.id,
            }).id
        return super(ProductProduct, self).create(vals)
