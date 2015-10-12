{
    'name': 'FEOS: Block pop-up Menu Register',

    'category': 'Hidden',
    'author': 'trungthanh.nguyen@feosco.com',
    'version': '0.1',
    'description': """
============================================
 -  Hide PopUp Support Register Odoo
============================================

""",
    'depends': ['web', 'mail'],
    'data': [
        'views/web_adblock.xml',
    ],
    'auto_install': False,
}
