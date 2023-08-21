# -*- coding: utf-8 -*-
from odoo import models, fields, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    ready_picking_ids = fields.One2many('stock.picking', string='Ready Deliveries', compute="_get_picking_in_ready")
    draft_invoice_ids = fields.One2many('account.move', string='Draft Invoices', compute="_get_draft_unpaid_invoices")
    unpaid_invoice_ids = fields.One2many('account.move', string='Not Paid/Partial Invoices', compute="_get_draft_unpaid_invoices")

    def _get_picking_in_ready(self):
        for order in self:
            order.ready_picking_ids = order.picking_ids.filtered(lambda picking: picking.state == 'assigned')

    def receipt_validate(self):
        self = self.picking_ids.filtered(lambda picking: picking.state == 'assigned')
        return self.button_validate()

    def _get_draft_unpaid_invoices(self):
        for order in self:
            order.draft_invoice_ids = order.invoice_ids.filtered(lambda inv: inv.state == 'draft' and inv.move_type == 'in_invoice')
            order.unpaid_invoice_ids = order.invoice_ids.filtered(lambda inv: inv.state == 'posted' and inv.payment_state != 'paid' and inv.move_type == 'in_invoice')

    def invoice_validate(self):
        self = self.invoice_ids
        for i in self:
            if not i.invoice_date:
                if i.is_purchase_document(include_receipts=True):
                    i.invoice_date = fields.Date.context_today(self)
                    # i.with_context(check_move_validity=False)._onchange_invoice_date()
        # self._post(soft=False)
        return self.action_post()

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

    def action_create_invoice(self):
        super(PurchaseOrder, self).action_create_invoice()
        return {'target': 'main'}

    def _post(self):
        self = self.invoice_ids
        for i in self:
            if not i.invoice_date:
                if i.is_purchase_document(include_receipts=True):
                    i.invoice_date = fields.Date.context_today(self)
                    i.with_context(check_move_validity=False)._onchange_invoice_date()
        return super(PurchaseOrder, self)._post()
