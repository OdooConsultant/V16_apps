# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Inventory Turnover Analysis',

    'summary': 'Easy turnover analysis with opening and closing stocks.',

    'description': """Inventory turnover is a ratio showing how many times a company has sold and replaced
                            inventory during a given period. Calculating inventory turnover can help businesses make
                            better purchasing decisions. """,

    'author': "Reliution",
    'website': "https://www.reliution.com/",
    'license': 'AGPL-3',
    'category': '',
    'version': '16.0.0.1.0',
    'currency': 'USD',
    'price': '49',
    'sequence': 0,

    'depends': ['stock', 'base', 'web', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'report/report.xml',
        'views/inventory_turnover_analysis_view.xml',
    ],
    "external_dependencies": {"python": ["xlsxwriter", "xlrd"]},
    "assets": {
        "web.assets_backend": [
            "inventory_turnover_analysis/static/src/js/report/action_manager_report.esm.js",
        ],
    },

    'installable': True,
    'auto_install': False,
    'application': True,
    'images': ['static/description/banner.gif'],
}
