# -*- coding: utf-8 -*-
from odoo import models, fields, api , _


class StockLot(models.Model):
	_inherit = 'stock.lot'

	@api.model
	def create(self, vals):
		res = super(StockLot, self).create(vals)
		if res.product_id.sequence_id:
			code = res.product_id.sequence_id.code
			if code:
				res.name = res.product_id.sequence_id.next_by_code(code)
		return res
