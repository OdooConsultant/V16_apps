# -*- coding: utf-8 -*-
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class InventoryStockMovement(models.TransientModel):
    _name = "inventory.stock.movement"
    _rec_name = 'id'

    start_date = fields.Date("Start Date", required=True)
    end_date = fields.Date("End Date", required=True)
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", required=True)
    location_id = fields.Many2one("stock.location", string="Location", required=True)
    product_category = fields.Many2many("product.category", string="Product Category")
    product_ids = fields.Many2many("product.product", string="Product")
    sm_lines = fields.One2many("inventory.stock.movement.line", "sm_id", string="Stock Movements")
    total_opening_stock = fields.Float(string="Total Opening", readonly=True, compute='_compute_total')
    total_stock_in = fields.Float(string="Total In", readonly=True, compute='_compute_total')
    total_stock_out = fields.Float(string="Total Out", readonly=True, compute='_compute_total')
    total_closing_stock = fields.Float(string="Total Closing", readonly=True, compute='_compute_total')
    is_zero_product = fields.Boolean(string="Is zero Movement",
                                     help="If enabled, the system will display those products which have Zero/No "
                                          "movement in inventory.")

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
            'is_zero_product': True
        }
        movement = self.env['inventory.stock.movement'].create(vals)
        movement.create_line()
        action = {
            'name': 'stock movement',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': movement.id,
            'view_id': self.env.ref('inventory_stock_movement.inventory_stock_movement_form_view').id,
            'res_model': 'inventory.stock.movement',
            'type': 'ir.actions.act_window',
            'target': 'current'
        }
        return action

    def name_get(self):
        res = []
        for rec in self:
            name = 'Duration: ' + str(rec.start_date) + ' - ' + str(rec.end_date)
            res.append((rec.id, name))
        return res

    @api.model
    def default_get(self, fields):
        res = super(InventoryStockMovement, self).default_get(fields)
        res['start_date'] = datetime.today() + relativedelta(day=1)
        res['end_date'] = datetime.today()
        company = self.env.company.id
        warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)
        res['warehouse_id'] = warehouse_id.id
        res['location_id'] = warehouse_id.lot_stock_id.id
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
                 ('date', '<', self.start_date), ('product_id', '=', product.id), ('state', '=', 'done')], order='date')
            if sm_lines:
                vals = rec.calculate_stock_in_out(sm_lines, location_id, in_qty, out_qty)
                opening_stock = round((opening_stock + vals['stock_in']) - vals['stock_out'], 2)
        return opening_stock

    def create_line(self):
        for rec in self:
            rec.sm_lines.unlink()
            start_date = rec.start_date
            end_date = rec.end_date
            location_id = rec.location_id
            product_category = rec.product_category
            product_ids = rec.product_ids
            if not rec.product_ids and not rec.product_category:
                products = self.env['product.product'].search([('type', '=', 'product')], order='name')
            else:
                products = self.env['product.product'].search(
                    ['|', ('id', 'in', product_ids.ids), ('categ_id', 'in', product_category.ids),
                     ('type', '=', 'product')], order='name')
            for product in products:
                in_qty = 0
                out_qty = 0
                opening_stock = 0
                sm_lines = self.env['stock.move'].search(
                    ['|', ('location_id', '=', location_id.id), ('location_dest_id', '=', location_id.id),
                     ('date', '>=', start_date), ('date', '<=', end_date), ('product_id', '=', product.id),
                     ('state', '=', 'done')], order='date')
                if sm_lines:
                    opening_stock = rec.calculate_opening_stock(product, location_id, opening_stock, in_qty, out_qty)
                    vals = rec.calculate_stock_in_out(sm_lines, location_id, in_qty, out_qty)
                    closing_stock = round((opening_stock + vals['stock_in']) - vals['stock_out'], 2)
                    vals.update({
                        'sm_id': rec.id,
                        'product_id': product.id,
                        'product_category': product.categ_id.id,
                        'opening_stock': opening_stock,
                        'closing_stock': closing_stock,
                    })
                    self.env['inventory.stock.movement.line'].create(vals)
                elif rec.is_zero_product:
                    opening_stock = rec.calculate_opening_stock(product, location_id, opening_stock, in_qty, out_qty)
                    vals = rec.calculate_stock_in_out(sm_lines, location_id, in_qty, out_qty)
                    closing_stock = round((opening_stock + vals['stock_in']) - vals['stock_out'], 2)
                    vals.update({
                        'sm_id': rec.id,
                        'product_id': product.id,
                        'product_category': product.categ_id.id,
                        'opening_stock': opening_stock,
                        'closing_stock': closing_stock,
                    })
                    self.env['inventory.stock.movement.line'].create(vals)


class InventoryStockMovementLines(models.TransientModel):
    _name = "inventory.stock.movement.line"
    _order = 'product_id'

    sm_id = fields.Many2one("inventory.stock.movement", string="Stock Move")
    product_id = fields.Many2one("product.product", string="Product")
    product_category = fields.Many2one("product.category", string="Product Category")
    opening_stock = fields.Float(string="Opening Stock")
    stock_in = fields.Float(string="Stock In")
    stock_out = fields.Float(string="Stock Out")
    closing_stock = fields.Float(string="Closing Stock")
    product_moves = fields.Many2many("stock.move", string="Product movements")
