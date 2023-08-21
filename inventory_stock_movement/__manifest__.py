# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Inventory Stock Movement',

    'summary': 'Easy analysis and stock tracking with opening and closing quantities.',

    'description': """This module provides the ability to track all inventory movements for all warehouses for specific
                        duration.""",

    'author': "Reliution",
    'website': "https://www.reliution.com/",
    'license': 'AGPL-3',
    'category': '',
    'version': '16.0.0.1.0',
    'currency': 'USD',
    'price': '49',
    'sequence': 0,

    'depends': ['stock', 'base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'report/report.xml',
        'views/inventory_stock_movement_view.xml',
    ],
    "external_dependencies": {"python": ["xlsxwriter", "xlrd"]},
    "assets": {
        "web.assets_backend": [
            "inventory_stock_movement/static/src/js/report/action_manager_report.esm.js",
        ],
    },

    'installable': True,
    'auto_install': False,
    'application': True,
    'images': ['static/description/banner.gif'],
}
