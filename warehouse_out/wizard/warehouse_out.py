# -*- coding: utf-8 -*-
import base64
import tempfile

import xlrd
from odoo import api, fields, models , _


class WarehouseOut(models.TransientModel):
    _name = 'warehouse.out'

    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', required=True)
    barcode_file = fields.Binary('Select File', required=True)

    @api.model
    def default_get(self, fields):
        res = super(WarehouseOut, self).default_get(fields)
        srd = self.env['stock.picking.type'].search([('sequence_code', '=', 'OUT')])
        res['picking_type_id'] = srd
        return res

    def read_file(self):
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        fp.write(base64.decodebytes(self.barcode_file))
        fp.seek(0)
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)
        barcodes = []
        for row_no in range(sheet.nrows):
            barcodes.append(sheet.row_values(row_no)[0])
        fp.close()

        product_list = {}
        for barcode in barcodes:

            if type(barcode) == float:
                temp = int(barcode)
                barcode = str(temp)

            products = self.env['product.product'].search(
                ['|', ('barcode', '=', barcode), ('default_code', '=', barcode)])
            for product in products:
                product_list[product] = product_list.get(product, 0) + 1

        warehouse_out = self.env['stock.picking'].create({
            'picking_type_id': self.picking_type_id.id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
        })
        warehouse_out._onchange_picking_type()

        for product_id in product_list:
            new_move = self.env['stock.move'].create({
                'name': _('New Move:'),
                'product_id': product_id.id,
                'product_uom_qty': product_list.get(product_id, 0),
                'product_uom': product_id.uom_id.id,
                'picking_id': warehouse_out.id,
                'location_id': warehouse_out.location_id.id,
                'location_dest_id': warehouse_out.location_dest_id.id,
            })
            new_move._onchange_product_id()

        warehouse_out.action_confirm()

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'view_ids': self.env.ref('stock.view_stock_quant_tree_inventory_editable').id,
            'target': 'current',
            'res_id': warehouse_out.id
        }
