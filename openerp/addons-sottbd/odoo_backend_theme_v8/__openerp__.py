{
    # Theme information
    'name' : 'Odoo Backend Theme v8',
    'category' : 'Theme/Backend',
    'version' : '1.0',
    'summary': 'Backend, Clean, Modern, Odoo, Theme',
    'description': """
Odoo Backend Theme v8
=================
    """,


    # Dependencies
    'depends': [
        'web'
    ],
    'external_dependencies': {},

    # Views
    'data': [
	   'views/backend.xml',
       'views/ir_menu_view.xml'
    ],

    # Author
    'author' : 'minhphung171093@gmail.com',
    'website' : 'http://incomtech.com.vn',
    'auto_install': True,
}
