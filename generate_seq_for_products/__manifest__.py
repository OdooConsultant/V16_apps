# -*- coding: utf-8 -*-
{
    "name": "Generate Product Sequence",

    'summary': 'Auto Generate unique SKU/Internal Reference from attributes',

    "description": """Auto Generate unique SKU/Internal Reference from attributes.""",

    'author': "Reliution",
    'website': "https://www.reliution.com/",
    'license': 'AGPL-3',
    'category': '',
    'version': '16.0.0.1.0',
    'currency': 'USD',
    'price': '29',
    'sequence': 0,

    "depends": ["base", "product"],

    "data": [
        'views/product_template_views.xml',
        'views/ir_sequence_data.xml',
    ],

    "installable": True,
    "application": True,

    'images': ['static/description/banner.gif'],
}
