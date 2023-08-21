# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Inventory FSN Analysis',

    'summary': 'Easy FSN analysis with opening and closing stocks.',

    'description': """Our module helps users identify products movement frequency based on FSN classification and 
        classifies all inventory movements into three categories: Fast moving, Slow moving, Non moving.""",

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
        'views/inventory_fsn_analysis_view.xml',
    ],
    "external_dependencies": {"python": ["xlsxwriter", "xlrd"]},
    "assets": {
        "web.assets_backend": [
            "inventory_fsn_analysis/static/src/js/report/action_manager_report.esm.js",
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'images': ['static/description/banner.gif'],
}
