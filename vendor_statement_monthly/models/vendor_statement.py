from odoo import fields, models, api, _
from datetime import datetime, date
from odoo.exceptions import ValidationError
import calendar


class VendorStatement(models.Model):
    _name = 'vendor.statement'
    _description = 'monthly vendor statement'
    _order = 'from_date desc,name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(string='Name', default=lambda self: _('New'), compute='_compute_name', store=True)
    month_list = [
        ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
    ]
    month = fields.Selection(month_list, string='Month', required=True,
                             default=month_list[int(datetime.now().strftime('%m')) - 1][0])
    year = fields.Integer(required=True, default=datetime.now().strftime('%Y'))
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    opening_balance = fields.Float(string='Opening Balance',compute='_compute_opening_balance')
    total_debit = fields.Float(string='Total Debit',compute='_compute_total_debit')
    total_credit = fields.Float(string='Total Credit',compute='_compute_total_credit')
    closing_balance = fields.Float(string='Closing Balance', compute='_compute_closing_balance')
    statement_lines = fields.One2many('vendor.statement.line', 'statement_id', string='Statements')
    note = fields.Text('Terms and conditions')

    @api.model
    def create(self, vals):
        m = vals.get('month')
        y = vals.get('year')
        p = vals.get('partner_id')
        mvc_id = self.env['vendor.statement'].search(
            [('month', '=', m), ('year', '=', y), ('partner_id', '=', p)])
        if mvc_id:
            raise ValidationError("The record already exists.")
        else:
            return super(VendorStatement, self).create(vals)

    @api.depends('month', 'year')
    def _compute_name(self):
        self = self.sudo()
        count = 1
        name = ''
        for rec in self:
            if rec.month in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                name = 'MVS/' + str(rec.year) + '/0' + str(rec.month) + '/' + format(count, '04d')
            else:
                name = 'MVS/' + str(rec.year) + '/' + str(rec.month) + '/' + format(count, '04d')
            name = self.check_name(name, count)
            rec.name = name
            return rec

    def check_name(self, name, count):
        self = self.sudo()
        for rec in self:
            statements = self.env['vendor.statement'].search([('name', '=', name)])
            if statements:
                for statement in statements:
                    count += 1
                if rec.month in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    name = 'MVS/' + str(rec.year) + '/0' + str(rec.month) + '/' + format(count, '04d')
                else:
                    name = 'MVS/' + str(rec.year) + '/' + str(rec.month) + '/' + format(count, '04d')
                name = self.check_name(name, count)
                return name
            else:
                return name

    @api.onchange('month', 'year')
    def onchange_month(self):
        self = self.sudo()
        if self.month:
            month_date = date(self.year, int(self.month), 1)
            self.from_date = month_date.replace(day=1)
            self.to_date = month_date.replace(day=calendar.monthrange(month_date.year, month_date.month)[1])

    @api.depends('month', 'year')
    def _compute_opening_balance(self):
        self = self.sudo()
        for rec in self:
            opening_balance = 0
            bill_ids = self.env['account.move'].search(
                [('invoice_date', '<', rec.from_date), ('state', '=', 'posted'),
                 ('partner_id', '=', rec.partner_id.id), ('move_type', '=', 'in_invoice')], order='invoice_date')
            bill_total = 0
            for bill in bill_ids:
                bill_total = bill_total + bill.amount_total
            refund_ids = self.env['account.move'].search(
                [('invoice_date', '<', rec.from_date), ('state', '=', 'posted'),
                 ('partner_id', '=', rec.partner_id.id), ('move_type', '=', 'in_refund')], order='invoice_date')
            refund_total = 0
            for refund in refund_ids:
                refund_total = refund_total + refund.amount_total
            payment_ids = self.env['account.payment'].search(
                [('date', '<', rec.from_date), ('state', '=', 'posted'),
                 ('partner_id', '=', rec.partner_id.id), ('partner_type', '=', 'supplier')], order='date')
            receive_payment_total = 0
            send_payment_total = 0
            for payment in payment_ids:
                if payment.payment_type == 'outbound':
                    for move in payment.move_id.line_ids:
                        if move.account_id.user_type_id.type == 'payable':
                            send_payment_total = send_payment_total + move.debit
                else:
                    for move in payment.move_id.line_ids:
                        if move.account_id.user_type_id.type == 'payable':
                            receive_payment_total = receive_payment_total + move.credit
            opening_balance = (refund_total + send_payment_total) - (bill_total + receive_payment_total)
            rec.opening_balance = opening_balance
            return rec

    def create_line(self):
        self = self.sudo()
        for rec in self:
            rec.statement_lines.unlink()
            from_date = rec.from_date
            to_date = rec.to_date
            vendor = rec.partner_id
            bill_ids = self.env['account.move'].search(
                [('invoice_date', '>=', from_date), ('invoice_date', '<=', to_date), ('partner_id', '=', vendor.id),
                 ('state', '=', 'posted'), ('move_type', '=', 'in_invoice')], order='invoice_date')
            for bill in bill_ids:
                statement = self.env['vendor.statement.line'].create({
                    'statement_id': rec.id,
                    'partner_id': vendor.id,
                    'date': bill.invoice_date,
                    'name': bill.name,
                    'debit': 0,
                    'credit': bill.amount_total,
                    'move_id': bill.id
                })

            refund_ids = self.env['account.move'].search(
                [('invoice_date', '>=', from_date), ('invoice_date', '<=', to_date), ('partner_id', '=', vendor.id),
                 ('state', '=', 'posted'), ('move_type', '=', 'in_refund')], order='invoice_date')
            for refund in refund_ids:
                statement = self.env['vendor.statement.line'].create({
                    'statement_id': rec.id,
                    'partner_id': vendor.id,
                    'date': refund.invoice_date,
                    'name': refund.name,
                    'debit': refund.amount_total,
                    'credit': 0,
                    'move_id': refund.id
                })

            payment_ids = self.env['account.payment'].search(
                [('date', '>=', from_date), ('date', '<=', to_date), ('state', '=', 'posted'),
                 ('partner_id', '=', vendor.id), ('partner_type', '=', 'supplier')], order='date')
            for payment in payment_ids:
                for line in payment.move_id.line_ids:
                    if line.credit != 0.0:
                        statement = self.env['vendor.statement.line'].create({
                            'statement_id': rec.id,
                            'partner_id': vendor.id,
                            'date': payment.date,
                            'name': payment.name,
                            'debit': line.credit,
                            'credit': 0,
                            'payment_id': payment.id
                        })
            return rec

    @api.depends('opening_balance', 'statement_lines')
    def _compute_closing_balance(self):
        self = self.sudo()
        for rec in self:
            closing_balance = rec.opening_balance
            if rec.statement_lines:
                debit = 0
                credit = 0
                for statement in rec.statement_lines:
                    debit += statement.debit
                    credit += statement.credit
                closing_balance = closing_balance + debit - credit
                rec.closing_balance = closing_balance
            else:
                rec.closing_balance = rec.opening_balance
            return rec

    @api.depends('statement_lines')
    def _compute_total_debit(self):
        self = self.sudo()
        for rec in self:
            total_debit = 0
            if rec.statement_lines:
                for statement in rec.statement_lines:
                    total_debit += statement.debit
                rec.total_debit = total_debit
            else:
                rec.total_debit = total_debit
            return rec

    @api.depends('statement_lines')
    def _compute_total_credit(self):
        self = self.sudo()
        for rec in self:
            total_credit = 0
            if rec.statement_lines:
                for statement in rec.statement_lines:
                    total_credit += statement.credit
                rec.total_credit = total_credit
            else:
                rec.total_credit = total_credit
            return rec

    @api.model
    def run_scheduler_onetime(self):
        self = self.sudo()
        start_year = self.env['account.move'].search([], order="invoice_date asc", limit=1)
        year = []
        for i in range(int(start_year.invoice_date.strftime('%Y')), int(datetime.now().strftime('%Y')) + 1):
            year.append(i)
        inv_partner = self.env['account.move'].search(
            [('state', '=', 'posted'), ('move_type', 'in', ['in_invoice', 'in_refund'])]).mapped(
            'partner_id.id')
        if inv_partner:
            partner_id = self.env['res.partner'].search([('id', 'in', inv_partner)])
            if partner_id:
                for partner in partner_id:
                    inv_date = self.env['account.move'].search(
                        [('state', '=', 'posted'), ('partner_id', '=', partner.id), ('move_type', 'in',
                                                                                     ['in_invoice', 'in_refund'])])
                    if inv_date:
                        for inv in inv_date:
                            m = str(inv.invoice_date.month)
                            y = str(inv.invoice_date.year)
                            msv_id = self.env['vendor.statement'].search(
                                [('month', '=', m), ('year', '=', y), ('partner_id', '=', partner.id)])
                            if msv_id:
                                msv_id.create_line()
                            else:
                                new_msv = self.env['vendor.statement'].create({
                                    'partner_id': partner.id,
                                    'month': m,
                                    'year': y,
                                })
                                new_msv.onchange_month()
                                new_msv.create_line()

    @api.model
    def run_scheduler_daily(self):
        self = self.sudo()
        today = date.today()
        inv_partner = self.env['account.move'].search(
            [('state', '=', 'posted'), ('invoice_date', '=', today),
             ('move_type', 'in', ['in_invoice', 'in_refund'])]).mapped('partner_id.id')
        if inv_partner:
            partner_id = self.env['res.partner'].search([('id', 'in', inv_partner)])
            if partner_id:
                for partner in partner_id:
                    msv_id = self.env['vendor.statement'].search(
                        [('from_date', '<=', today), ('to_date', '>=', today), ('partner_id', '=', partner.id)])
                    if msv_id:
                        msv_id.create_line()
                    else:
                        new_msv = self.env['vendor.statement'].create({
                            'partner_id': partner.id,
                        })
                        new_msv.onchange_month()
                        new_msv.create_line()



class VendorStatementLine(models.Model):
    _name = 'vendor.statement.line'
    _description = 'vendor statement lines'
    _order = 'date'

    statement_id = fields.Many2one('vendor.statement', string='Statement')
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    date = fields.Date(string='Date')
    name = fields.Char(string='Name')
    debit = fields.Float(string='Debit')
    credit = fields.Float(string='Credit')
    move_id = fields.Many2one('account.move', string='Invoice')
    payment_id = fields.Many2one('account.payment', string='Payment')