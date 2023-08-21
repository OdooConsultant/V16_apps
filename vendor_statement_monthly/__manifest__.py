{
	'name': 'Vendor Statement Monthly',

	'summary': 'Track monthly vendor statements',

	'description': """This app that will fetch all bills as well as refunds of a specific vendor and calculate 
	the total debit and credit with the opening and closing balances for required month.""",

	'author': "Reliution",
	'website': "https://www.reliution.com/",
	'license': 'AGPL-3',
	'category': 'Accounting/Accounting',
	'version': '16.0.0.1.0',
	'currency': 'USD',
	'price': '49',
	'sequence': 0,

	'depends': ['account', 'base', 'utm'],

	'data': ['data/vendor_statement_scheduler.xml',
			 'security/ir.model.access.csv',
			 'views/vendor_statement.xml',
			 'report/vendor_statement_report.xml'],

	'application': 'True',
	'installable': True,

	'images': ['static/description/banner.gif'],
}
