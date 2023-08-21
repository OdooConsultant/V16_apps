# -*- coding: utf-8 -*-

{
    'name': 'Purchase Orders From File',

    'summary': 'Easy purchase directly from file with product barcodes',

    'description': """This module will create a purchase order directly from an excel file containing list of barcodes 
    in a specific format.""",

    'author': "Reliution",
    'website': "https://www.reliution.com/",
    'license': 'AGPL-3',
    'category': '',
    'version': '16.0.0.1.0',
    'currency': 'USD',
    'price': '19',
    'sequence': 0,

    'depends': ['purchase'],

    'data': [
        'security/ir.model.access.csv',
        'views/purchase.xml',
        'wizard/purchase_orders_wizard.xml'

    ],

    'installable': True,
    'auto_install': False,
    'application': True,

    'images': ['static/description/banner.gif'],
}