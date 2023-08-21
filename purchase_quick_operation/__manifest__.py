# -*- coding: utf-8 -*-
{
    "name": "Quick Operations in PO",

    "summary": "Quick Operations in Purchase Order",

    "description": """Allows salesperson to validate receipt, validation of vendor bill, and registering cash payment 
    from PO itself at busy purchase counters.""",

    'author': "Reliution",
    'website': "https://www.reliution.com/",
    'license': 'AGPL-3',
    'category': '',
    'version': '16.0.0.1.0',
    'currency': 'USD',
    'price': '9',
    'sequence': 0,

    "depends": ["purchase_stock"],

    "data": [
        'views/purchase_views.xml',
    ],

    "installable": True,
    "application": True,

    'images': ['static/description/banner.gif'],
}
