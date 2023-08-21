# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ChangeSaleOrderTaxWizard(models.TransientModel):
    _name = 'sale.order.tax.wizard'

    account_tax_id = fields.Many2many('account.tax', string='Select TAX', required=True)

    def change_tax(self):
        sale_order = self.env['sale.order'].browse(self._context.get('active_ids'))
        return sale_order.order_line.write({'tax_id': self.account_tax_id})
