# -*- coding: utf-8 -*-
{
    'name': 'Change Purchase TAX',

    'summary': 'Easy change of taxes on purchase order form',

    'description': """This module will allow you to change taxes at one go for all your products listed in that purchase
     order form.""",

    'author': "Reliution",
    'website': "https://www.reliution.com/",
    'license': 'AGPL-3',
    'category': '',
    'version': '16.0.0.1.0',
    'currency': 'USD',
    'price': '39',
    'sequence': 0,

    'depends': ['purchase'],

    'data': [
        'security/ir.model.access.csv',
        'views/purchase_views.xml',
        'wizard/change_purchase_order_tax_wizard_views.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,

    'images': ['static/description/banner.gif'],
}
