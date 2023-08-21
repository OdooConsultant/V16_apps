# -*- coding: utf-8 -*-
{
    'name': 'Manufacturing Lot No.',

    'summary': 'Easy generation of internal reference for a product variant',

    'description': """This module will allow you to create custom Lot/Serial Number for all Product SKUs, which will 
    provide easy traceability.""",

    'author': "Reliution",
    'website': "https://www.reliution.com/",
    'license': 'AGPL-3',
    'category': '',
    'version': '16.0.0.1.0',
    'currency': 'USD',
    'price': '29',
    'sequence': 0,

    'depends': ['base', 'product', 'mrp'],

    'data': [
        'views/product_sequence_view.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,

    'images': ['static/description/banner.gif'],
}

