# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    _sql_constraints = [('unique_default_code','unique(default_code)',"Internal Reference must be unique !")]

    product_uid = fields.Char("Product UID", required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        if vals.get('product_uid', _('New')) == _('New'):
            vals['product_uid'] = self.env['ir.sequence'].next_by_code('product.template') or _('New')
        return super(ProductTemplate, self).create(vals)

class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    code = fields.Char("Code", required=True)

class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    in_product_ref = fields.Boolean(string="IN Product Reference")

class ProductProduct(models.Model):
    _inherit = "product.product"

    _sql_constraints = [('unique_default_code','unique(default_code)',"Internal Reference must be unique !")]
    
    def generate_int_ref(self):
        for rec in self:
            attribute_value = ''
            code = ''
            if rec.product_template_attribute_value_ids:
                for value in rec.product_template_attribute_value_ids:
                    if rec.product_tmpl_id.product_uid and value.attribute_id.in_product_ref == True:
                        attribute_value += '-' + value.product_attribute_value_id.code
                code += rec.product_uid + attribute_value
            else:
                if rec.product_tmpl_id.product_uid and rec.product_template_attribute_value_ids.attribute_id.in_product_ref == True:
                    attribute_value += '-' + rec.product_template_attribute_value_ids.product_attribute_value_id.code
                code += rec.product_uid + attribute_value
            return code

    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        flag = False
        for att_value in res.product_template_attribute_value_ids:
            flag = att_value.attribute_id.in_product_ref
            if not flag:
                break
        if flag:
            code = res.generate_int_ref()
            res.default_code = code
            if vals and vals.get('product_tmpl_id') and len(res.product_tmpl_id.product_variant_ids) != 1:
                # res.default_code = code
                res.product_tmpl_id.default_code = res.product_uid
        # elif vals and vals.get('product_tmpl_id') and len(res.product_tmpl_id.product_variant_ids) == 1:
        #     res.default_code = code
        #     res.product_tmpl_id.default_code = code
        # else:
        #     res.default_code = code
        return res

    def write(self, vals):
        for rec in self:
            super(ProductProduct, self).write(vals)
            flag = False
            for att_value in rec.product_template_attribute_value_ids:
                flag = att_value.attribute_id.in_product_ref
                if not flag:
                    break
            if flag:
                code = rec.generate_int_ref()
                if vals and vals.get('product_template_attribute_value_ids'):
                    rec.write({'default_code': code})
                    if len(rec.product_tmpl_id.product_variant_ids) != 1:
                        rec.product_tmpl_id.write({'default_code': rec.product_uid})
        return True
