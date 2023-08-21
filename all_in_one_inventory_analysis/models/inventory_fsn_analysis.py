# -*- coding: utf-8 -*-
from ast import literal_eval
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

from odoo.exceptions import ValidationError

from odoo.tools import float_compare
import logging

_logger = logging.getLogger(__name__)


class InventoryFsnAnalysis(models.TransientModel):
    _name = "inventory.fsn.analysis"

    start_date = fields.Date("Start Date", required=True)
    end_date = fields.Date("End Date", required=True)
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", required=True)
    location_id = fields.Many2one("stock.location", string="Location", required=True)
    product_category = fields.Many2many("product.category", string="Product Category")
    product_ids = fields.Many2many("product.product", string="Product")
    sm_lines = fields.One2many("inventory.fsn.analysis.line", "sm_id", string="Stock Movements")
    total_opening_stock = fields.Float(string="Opening Stock", readonly=True, compute='_compute_total')
    total_stock_in = fields.Float(string="Total Stock In", readonly=True, compute='_compute_total')
    total_stock_out = fields.Float(string="Total Stock Out", readonly=True, compute='_compute_total')
    total_closing_stock = fields.Float(string="Closing Stock", readonly=True, compute='_compute_total')
    fsn_classification = fields.Selection(selection=[
        ('all', 'All'),
        ('fast_moving', 'Fast Moving'), ('slow_moving', 'Slow Moving'), ('non_moving', 'Non Moving')],
        string='FSN Classification', required=True, default='all')
    fast_moving = fields.Float(string="Fast Moving", required=True)
    slow_moving = fields.Float(string="Slow Moving", required=True)
    non_moving = fields.Float(string="Non Moving", required=True)
    product_domain = fields.Char(stirng="Product Domain")
    is_zero_product = fields.Boolean(string="Zero Movement",
                                     help="If enabled, the system will display those products which have Zero/No "
                                          "movement in inventory")

    def default_action(self):
        company = self.env.company.id
        warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)
        product = self.env['product.product'].search([('type', '=', 'product')], order='qty_available desc', limit=10)
        vals = {
            'start_date': datetime.today() + relativedelta(day=1),
            'end_date': datetime.today(),
            'warehouse_id': warehouse_id.id,
            'location_id': warehouse_id.lot_stock_id.id,
            'product_ids': product,
            'is_zero_product': True,
            'product_domain': '[]'
        }
        movement = self.env['inventory.fsn.analysis'].create(vals)
        movement.create_line()
        action = {
            'name': 'stock movement',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': movement.id,
            'view_id': self.env.ref('all_in_one_inventory_analysis.inventory_fsn_form_view').id,
            'res_model': 'inventory.fsn.analysis',
            'type': 'ir.actions.act_window',
            'target': 'current'
        }
        return action

    @api.model
    def default_get(self, fields):
        res = super(InventoryFsnAnalysis, self).default_get(fields)
        res['start_date'] = datetime.today() + relativedelta(day=1)
        res['end_date'] = datetime.today()
        res['fast_moving'] = 6
        res['slow_moving'] = 3
        res['non_moving'] = 1
        company = self.env.company.id
        warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)
        res['warehouse_id'] = warehouse_id.id
        res['location_id'] = warehouse_id.lot_stock_id.id
        return res

    def name_get(self):
        res = []
        for rec in self:
            name = 'Duration: ' + str(rec.start_date) + ' - ' + str(rec.end_date)
            res.append((rec.id, name))
        return res

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        if self.warehouse_id:
            self.location_id = self.warehouse_id.lot_stock_id

    @api.onchange('product_category')
    def onchange_product_category_id(self):
        if self.product_category:
            return {'domain': {'product_ids': [('categ_id', 'child_of', self.product_category.ids)]}}

    def _compute_total(self):
        for rec in self:
            total_opening_stock = 0
            total_stock_in = 0
            total_stock_out = 0
            total_closing_stock = 0
            if rec.sm_lines:
                for sm in rec.sm_lines:
                    total_opening_stock += sm.opening_stock
                    total_stock_in += sm.stock_in
                    total_stock_out += sm.stock_out
                    total_closing_stock += sm.closing_stock
            rec.total_opening_stock = round(total_opening_stock, 2)
            rec.total_stock_in = round(total_stock_in, 2)
            rec.total_stock_out = round(total_stock_out, 2)
            rec.total_closing_stock = round(total_closing_stock, 2)

    def calculate_stock_in_out(self, sm_lines, location_id, in_qty, out_qty):
        sm_ids = []
        for sm in sm_lines:
            if location_id == sm.location_id:
                out_qty += sm.product_uom_qty
            elif location_id == sm.location_dest_id:
                in_qty += sm.product_uom_qty
            sm_ids.append(sm.id)
        vals = {
            'stock_in': round(in_qty, 2),
            'stock_out': round(out_qty, 2),
            'product_moves': [(6, 0, sm_ids)]
        }
        return vals

    def calculate_opening_stock(self, product, location_id, opening_stock, in_qty, out_qty):
        for rec in self:
            sm_lines = self.env['stock.move'].search(
                ['|', ('location_id', '=', location_id.id), ('location_dest_id', '=', location_id.id),
                 ('date', '<', rec.start_date), ('product_id', '=', product.id), ('state', '=', 'done')], order='date')
            if sm_lines:
                vals = rec.calculate_stock_in_out(sm_lines, location_id, in_qty, out_qty)
                opening_stock = round((opening_stock + vals['stock_in']) - vals['stock_out'], 2)
        return opening_stock

    def calculate_sale(self, product):
        sale = 0.0
        for rec in self:
            pos = self.env['ir.module.module'].search([('name', '=', 'point_of_sale')])
            domain = []
            if not pos or pos.state != 'installed':
                domain = [('date', '>=', rec.start_date), ('date', '<=', rec.end_date), ('product_id', '=', product.id),
                          ('picking_code', '=', 'outgoing'), ('state', '=', 'done'), ('sale_line_id', '!=', False)]
            else:
                domain = [('date', '>=', rec.start_date), ('date', '<=', rec.end_date), ('state', '=', 'done'),
                          ('picking_code', '=', 'outgoing'), ('product_id', '=', product.id),
                          '|', ('picking_id.pos_order_id', '!=', False), ('picking_id.sale_id', '!=', False)]
            stock_movement_lines = self.env['stock.move'].search(domain, order='date')
            if stock_movement_lines:
                for movement in stock_movement_lines:
                    sale += movement.product_uom_qty
        return sale

    def fns_classify(self, turnover_ratio):
        for rec in self:
            fsn = []
            if turnover_ratio >= rec.fast_moving:
                fsn = 'fast_moving'
            elif rec.fast_moving > turnover_ratio >= rec.slow_moving:
                fsn = 'slow_moving'
            elif turnover_ratio < rec.slow_moving:
                fsn = 'non_moving'
            else:
                raise ValidationError("setup valid values in FNS fields!")

            if rec.fsn_classification == fsn:
                return fsn
            elif rec.fsn_classification == 'all':
                return fsn

    def create_line(self):
        for rec in self:
            rec.sm_lines.unlink()
            start_date = rec.start_date
            end_date = rec.end_date
            location_id = rec.location_id
            product_category = rec.product_category
            product_ids = rec.product_ids

            if rec.fast_moving <= rec.slow_moving or rec.fast_moving <= rec.non_moving:
                raise ValidationError("setup valid values in FNS fields!")
            elif rec.slow_moving >= rec.fast_moving or rec.slow_moving <= rec.non_moving:
                raise ValidationError("setup valid values in FNS fields!")
            elif rec.non_moving >= rec.fast_moving or rec.non_moving >= rec.slow_moving:
                raise ValidationError("setup valid values in FNS fields!")

            products = self.env['product.product']
            _logger.info("********Product Domain*********" + str(rec.product_domain))
            if rec.product_domain:
                if rec.product_domain != '[]':
                    products = products.search(literal_eval(rec.product_domain), order='name')
            if not products:
                if not rec.product_ids and not rec.product_category:
                    products = products.search([('type', '=', 'product')], order='name')
                else:
                    products = products.search(
                        ['|', ('id', 'in', product_ids.ids), ('categ_id', 'child_of', product_category.ids),
                         ('type', '=', 'product')], order='name')
            for product in products:
                in_qty = 0.0
                out_qty = 0.0
                opening_stock = 0
                turnover_ratio = 0.0
                average = 0.0
                sm_lines = self.env['stock.move'].search(
                    ['|', ('location_id', '=', location_id.id), ('location_dest_id', '=', location_id.id),
                     ('date', '>=', start_date), ('date', '<=', end_date), ('product_id', '=', product.id),
                     ('state', '=', 'done')], order='date')
                if sm_lines:
                    opening_stock = self.calculate_opening_stock(product, location_id, opening_stock, in_qty, out_qty)
                    vals = rec.calculate_stock_in_out(sm_lines, location_id, in_qty, out_qty)
                    closing_stock = round((opening_stock + vals['stock_in']) - vals['stock_out'], 2)
                    average = round((opening_stock + closing_stock) / 2, 2)
                    sale = round(self.calculate_sale(product), 2)
                    if average != 0:
                        turnover_ratio = round(sale / average, 2)
                    fsn_classification = self.fns_classify(turnover_ratio)
                    if fsn_classification:
                        vals.update({
                            'sm_id': self.id,
                            'product_id': product.id,
                            'product_category': product.categ_id.id,
                            'opening_stock': opening_stock,
                            'stock_in': in_qty,
                            'stock_out': out_qty,
                            'closing_stock': closing_stock,
                            'average_stock': average,
                            'sale': sale,
                            'turnover_ratio': turnover_ratio,
                            'fsn': fsn_classification
                        })
                        self.env['inventory.fsn.analysis.line'].create(vals)
                elif rec.is_zero_product:
                    opening_stock = self.calculate_opening_stock(product, location_id, opening_stock, in_qty, out_qty)
                    vals = rec.calculate_stock_in_out(sm_lines, location_id, in_qty, out_qty)
                    closing_stock = round((opening_stock + vals['stock_in']) - vals['stock_out'], 2)
                    average = round((opening_stock + closing_stock) / 2, 2)
                    sale = round(self.calculate_sale(product), 2)
                    if average != 0:
                        turnover_ratio = round(sale / average, 2)
                    fsn_classification = self.fns_classify(turnover_ratio)
                    if fsn_classification:
                        vals.update({
                            'sm_id': self.id,
                            'product_id': product.id,
                            'product_category': product.categ_id.id,
                            'opening_stock': opening_stock,
                            'stock_in': in_qty,
                            'stock_out': out_qty,
                            'closing_stock': closing_stock,
                            'average_stock': average,
                            'sale': sale,
                            'turnover_ratio': turnover_ratio,
                            'fsn': fsn_classification
                        })
                        self.env['inventory.fsn.analysis.line'].create(vals)


class InventoryFsnLines(models.TransientModel):
    _name = "inventory.fsn.analysis.line"
    _order = 'product_id'

    sm_id = fields.Many2one("inventory.fsn.analysis", string="Stock Move")
    product_id = fields.Many2one("product.product", string="Product")
    product_category = fields.Many2one("product.category", string="Product Category")
    opening_stock = fields.Float(string="Opening Stock")
    stock_in = fields.Float(string="Stock In")
    stock_out = fields.Float(string="Stock Out")
    closing_stock = fields.Float(string="Closing Stock")
    average_stock = fields.Float(string="Average Stock")
    sale = fields.Float(string="Sale")
    turnover_ratio = fields.Float(string="Turnover Ratio")
    fsn = fields.Selection(selection=[
        ('all', 'All'),
        ('fast_moving', 'Fast Moving'), ('slow_moving', 'Slow Moving'), ('non_moving', 'Non Moving')],
        string='FSN Classification')
    product_moves = fields.Many2many("stock.move", string="Product movements")
