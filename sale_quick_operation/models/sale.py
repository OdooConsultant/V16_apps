# -*- coding: utf-8 -*-
from odoo import models, fields, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ready_picking_ids = fields.One2many('stock.picking', string='Ready Deliveries', compute="_get_picking_in_ready")
    draft_invoice_ids = fields.One2many('account.move', string='Draft Invoices', compute="_get_draft_unpaid_invoices")
    unpaid_invoice_ids = fields.One2many('account.move', string='Not Paid/Partial Invoices', compute="_get_draft_unpaid_invoices")

    def _get_picking_in_ready(self):
        for order in self:
            order.ready_picking_ids = order.picking_ids.filtered(lambda picking: picking.state == 'assigned')

    def delivery_validate(self):
        self = self.picking_ids.filtered(lambda picking: picking.state == 'assigned')
        return self.button_validate()

    def _get_draft_unpaid_invoices(self):
        for order in self:
            order.draft_invoice_ids = order.invoice_ids.filtered(lambda inv: inv.state == 'draft' and inv.move_type == 'out_invoice')
            order.unpaid_invoice_ids = order.invoice_ids.filtered(lambda inv: inv.state == 'posted' and inv.payment_state != 'paid' and inv.move_type == 'out_invoice')

    def invoice_validate(self):
        self = self.invoice_ids
        self._post(soft=False)
        return False

    def invoice_register_payment(self):
        self = self.invoice_ids
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }