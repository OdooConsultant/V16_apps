# -*- coding: utf-8 -*-

{
    'name': 'Customer Statement Monthly',

    'summary': 'Track monthly customer statements',

    'description': """This app that will fetch all invoices as well as credit notes of a specific customer and calculate 
    the total debit and credit with the opening and closing balances for required month.""",

    'author': "Reliution",
    'website': "https://www.reliution.com/",
    'license': 'AGPL-3',
    'category': 'Accounting/Accounting',
    'version': '16.0.0.1.0',
    'currency': 'USD',
    'price': '49',
    'sequence': 0,

    'depends': ['base', 'account', 'utm'],

    'data': [
        'data/customer_statement_scheduler.xml',
        'security/ir.model.access.csv',
        'security/statement_security.xml',
        'views/customer_statement.xml',
        'report/customer_statement_report.xml',
    ],

    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

    'images': ['static/description/banner.gif'],
}
