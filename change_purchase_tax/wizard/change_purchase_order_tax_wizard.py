# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ChangePurchaseOrderTaxWizard(models.TransientModel):
    _name = 'purchase.order.tax.wizard'

    account_tax_id = fields.Many2many('account.tax', string='Select TAX', required=True)

    def change_tax(self):
        purchase_order = self.env['purchase.order'].browse(self._context.get('active_ids'))
        return purchase_order.order_line.write({'taxes_id': self.account_tax_id})
