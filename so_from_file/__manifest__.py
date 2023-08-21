# -*- coding: utf-8 -*-

{
    'name': 'Sale Order From File',

    'summary': 'Easy Sale Order directly from file with product barcodes',

    'description': """This module will create a sales order directly from an excel file containing list of barcodes 
    in a specific format.""",

    'author': "Reliution",
    'website': "https://www.reliution.com/",
    'license': 'AGPL-3',
    'category': '',
    'version': '16.0.0.1.0',
    'currency': 'USD',
    'price': '19',
    'sequence': 0,

    'depends': ['sale_management'],

    'data': [
        'security/ir.model.access.csv',
        'views/sale_views.xml',
        'wizard/sale_order_wizard_views.xml'
    ],

    'installable': True,
    'auto_install': False,
    'application': True,

    'images': ['static/description/banner.gif'],
}
