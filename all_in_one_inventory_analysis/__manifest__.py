# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'All in one Inventory Analysis',

    'summary': 'Easy inventory analysis with FSN analysis, Stock Movement and Turnover Analysis.',

    'description': """This module provides ability to helps users identify products movement frequency based on FSN 
    classification and also track all inventory movements for all warehouses for specific duration. It also shows how 
    many times a company has sold and replaced inventory during a given period by calculating inventory turnover 
    ratio.""",

    'author': "Reliution",
    'website': "https://www.reliution.com/",
    'license': 'AGPL-3',
    'category': '',
    'version': '16.0.0.1.0',
    'currency': 'USD',
    'price': '99',
    'sequence': 0,
    'depends': ['stock', 'base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'report/report.xml',
        'views/inventory_turnover_analysis_view.xml',
        'views/inventory_stock_movement_view.xml',
        'views/inventory_fsn_analysis_view.xml',
    ],
    "external_dependencies": {"python": ["xlsxwriter", "xlrd"]},
    "assets": {
        "web.assets_backend": [
            "all_in_one_inventory_analysis/static/src/js/report/action_manager_report.esm.js",
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'images': ['static/description/banner.gif'],
}
