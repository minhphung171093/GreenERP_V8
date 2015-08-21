# -*- coding: utf-8 -*-
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
    'name': 'Quản Lý Hồ Sơ Đầu Tư',
    'version': '1.0',
    'category': 'Dự Án Đầu Tư',
    'sequence': 14,
    'author': 'nguyentoanit@gmail.com',
    'website' : 'http://www.incomtech.com.vn',
    'depends': ['ql_vanban','properties','base','vsis_base','report_aeroo','report_aeroo_ooo','skhdt_base'],
    'data': [
        'security/hoso_security.xml',
        'security/ir.model.access.csv',
        'giay_chung_nhan_ho_so_view.xml',
        'thu_hoi_ho_so_view.xml',
        'report/ql_ho_so_report_view.xml',
        'properties_data.xml',
        'report/tinh_hinh_cap_giay_chung_nhan_report_view.xml',
        'report/giay_chung_nhan_dau_tu_report_view.xml',
        'report/to_trinh_chung_nhan_dau_tu_report_view.xml',
        'wizard/tinh_hinh_cap_giay_chung_nhan_report_view.xml',
        'gcndt_sequence.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
