# -*- coding: utf-8 -*-
import base64
import tempfile

import xlrd
from odoo import api, fields, models


class ProductLabel(models.TransientModel):
    _name = 'sale.order.from.file'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    barcode_file = fields.Binary(string='Select File', required=True)

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

        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
        })
        # sale_order.onchange_partner_id()
        import_logs = ""

        product_list = {}
        for barcode in barcodes:

            if type(barcode) == float:
                temp = int(barcode)
                barcode = str(temp)

            products = self.env['product.product'].search(
                ['|', ('barcode', '=', barcode), ('default_code', '=', barcode)], limit=1)

            if not products:
                import_logs += "\n %s is not found" % barcode
                continue
            for product in products:
                product_list[product] = product_list.get(product, 0) + 1
        for product_id in product_list:
            so_line = self.env['sale.order.line'].create({
                'product_id': product_id[0].id,
                'product_uom_qty': product_list.get(product_id, 0),
                # 'name': sale_order.order_line.name,
                # 'price_unit': 0,
                'order_id': sale_order.id
            })
            # so_line.product_uom_change()
        sale_order.write({'import_logs': import_logs})


        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'view_ids': self.env.ref('sale.view_order_form').id,
            'target': 'current',
            'res_id': sale_order.id
        }
