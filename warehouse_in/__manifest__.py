# -*- coding: utf-8 -*-
{
    'name': 'Warehouse In',

    'summary': 'Easy Warehouse In operation directly from excel file with product barcodes',

    'description': """This module will perform a Warehouse In operation directly from an excel file containing list of 
    barcodes in a specific format.""",

    'author': "Reliution",
    'website': "https://www.reliution.com/",
    'license': 'AGPL-3',
    'category': '',
    'version': '16.0.0.1.0',
    'currency': 'USD',
    'price': '9',
    'sequence': 0,

    'depends': ['product', 'stock'],

    'data': [
        'security/ir.model.access.csv',
        'views/inventory.xml',
        'wizard/warehouse_in.xml',

    ],

    'installable': True,
    'auto_install': False,
    'application': True,

    'images': ['static/description/banner.gif'],
}