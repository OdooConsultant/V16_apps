# -*- coding: utf-8 -*-
{
    'name': 'Change Sales TAX',

    'summary': 'Easy change of taxes on sale order form',

    'description': """This module will allow you to change taxes at one go for all your products listed in that sale
     order form.""",

    'author': "Reliution",
    'website': "https://www.reliution.com/",
    'license': 'AGPL-3',
    'category': '',
    'version': '16.0.0.1.0',
    'currency': 'USD',
    'price': '39',
    'sequence': 0,

    'depends': ['sale'],

    'data': [
        'security/ir.model.access.csv',
        'views/sale_views.xml',
        'wizard/change_sale_order_tax_wizard_views.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,

    'images': ['static/description/banner.gif'],
}
