# -*- encoding: utf-8 -*-
##############################################################################
#
#
##############################################################################
{
    'name': 'Quản Lý Dự Án Đầu Tư',
    'version': '1',
    'category': 'Dự Án Đầu Tư',
    'description': """
""",
    'author': 'nguyentoanit@gmail.com',
    'website' : 'http://www.incomtech.com.vn',
    'depends': ['ql_ho_so','hr','report_aeroo','report_aeroo_ooo','skhdt_base'],
    'data': [
            'security/duan_dautu_security.xml',
            'security/ir.model.access.csv',
            'properties_data.xml',
            'duan_dautu.xml',
            'nguon_von_view.xml',
            'wizard/xem_cay_nguon_von_view.xml',
            'baocao_giamsat_view.xml',
            'baocao_dauthau_view.xml',
            'wizard/ke_hoach_dau_tu_report_view.xml',
            'report/ke_hoach_dau_tu_report_view.xml',
            'wizard/ke_hoach_dau_tu_theonam_report_view.xml',
            'report/ke_hoach_dau_tu_theonam_report_view.xml',
            'report/baocao_giamsat_report_view.xml',
            'wizard/baocao_dauthau_report_view.xml',
            'report/baocao_dauthau_report_view.xml',
            'report/print_baocao_giamsat_report_view.xml',
            'report/print_baocao_dauthau_report_view.xml',
            'menu.xml',
             
        ],
    'demo': [],
    'images': [
        ],
    'css' : [
    ],
    'application': True,
    'installable': True,
    'active': False,
}

