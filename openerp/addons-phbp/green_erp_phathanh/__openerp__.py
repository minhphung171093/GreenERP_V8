# -*- coding: utf-8# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'GreenERP Phát Hành',
    'version': '1.0',
    'category': 'GreenERP',
    'sequence': 1,
    'author': 'nguyentoanit@gmail.com',
    'website' : 'http://incomtech.com/',
    'depends': ['green_erp_base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/baocao_nhanh_kyve_view.xml',
        'wizard/baocao_tieuthu_kyve_view.xml',
        'wizard/baocao_thitruong_kyve_view.xml',
        'wizard/baocao_thuhoi_ve_view.xml',
        'wizard/baocao_tonghop_tieuthu_view.xml',
        'wizard/graph_report_view.xml',
        'wizard/baocao_kehoach_doanhthu_view.xml',
        'wizard/tonghop_nhapxuat_ton_view.xml',
        'report/dieuchinh_kehoach_pp_ve_report_view.xml',
        'report/baocao_nhanh_ky_ve_report_view.xml',
        'report/baocao_tieuthu_ky_ve_report_view.xml',
        'report/baocao_thitruong_ky_ve_report_view.xml',
        'report/baocao_thuhoi_ve_report_view.xml',
        'report/baocao_tonghop_tieuthu_report_view.xml',
        'report/baocao_kehoach_doanhthu_report_view.xml',
        'report/tonghop_nhapxuat_ton_report_view.xml',
        'quanly_phanphoi_view.xml',
        'graph_report_view.xml',
        
        'menu.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: -*-