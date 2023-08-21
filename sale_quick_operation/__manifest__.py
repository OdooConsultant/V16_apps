# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Quick Operations in SO",

    "summary": "Quick Operations in Sales Order",

    "description": """Allow salesperson to validate deliveries, validation of invoice, 
                and registering cash payment from SO itself at busy sales counters.""",

    'author': "Reliution",
    'website': "https://www.reliution.com/",
    'license': 'AGPL-3',
    'category': '',
    'version': '16.0.0.1.0',
    'currency': 'USD',
    'price': '9',
    'sequence': 0,

    "depends": ["sale_stock"],

    "data": [
        'views/sale_views.xml',
    ],

    "installable": True,
    "application": True,
    "auto_install": False,

    'images': ['static/description/banner.gif'],
}
