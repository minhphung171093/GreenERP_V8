{
    'name': 'FEOS:  Show Hide Menu Left Bar',
    'version': '1.0',
    'category': 'web',
    'complexity': "easy",
    'description': """
==================
Web Show Hide Menu
==================

    """,
    'author': 'trungthanh.nguyen@feosco.com',
    'website': 'http://feosco.com',
    'depends': ['web'],
    'data': ['views/fold_menu.xml'],
    'auto_install': True,
    'active': False,

    'qweb' : [
        "static/src/xml/*.xml",
    ],
}