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
    'name': 'MLG ARAP ACCOUNT',
    'version': '1.0',
    'category': 'ARAP',
    'sequence': 1,
    'depends': ['mlg_arap_base','account_accountant','account_cancel','report_aeroo','web_readonly_bypass'],
    'data': [
        'security/account_security.xml',
        'security/ir.model.access.csv',
        'report/danhsach_congno_view.xml',
        'report/chitiet_congno_view.xml',
        'report/form_congno_view.xml',
        'report/phieu_dexuat_thu_view.xml',
        'report/in_dexuat_view.xml',
        'report/doanh_so_thu_view.xml',
        'report/doanh_so_tra_view.xml',
        'report/congno_vuotdinhmuc_view.xml',
        'report/congno_dangcho_view.xml',
        'report/tonghop_congno_view.xml',
        'report/chitiet_congno_mot_doituong_view.xml',
        'report/tonghop_congno_mot_doituong_view.xml',
        'report/doanh_so_phaithu_view.xml',
        'report/doanh_so_phaitra_view.xml',
        'report/congno_dangchothu_view.xml',
        'report/chitiet_congno_tgx_view.xml',
        'report/chitiet_congno_thuho_view.xml',
        'report/chitiet_congno_kyquy_view.xml',
        'wizard/danhsach_congno_view.xml',
        'wizard/chitiet_congno_view.xml',
        'wizard/phieu_dexuat_thu_view.xml',
        'wizard/in_dexuat_view.xml',
        'wizard/doanh_so_thu_view.xml',
        'wizard/doanh_so_tra_view.xml',
        'wizard/congno_vuotdinhmuc_view.xml',
        'wizard/congno_dangcho_view.xml',
        'wizard/tonghop_congno_view.xml',
        'wizard/chitiet_congno_mot_doituong_view.xml',
        'wizard/tonghop_congno_mot_doituong_view.xml',
        'wizard/alert_form_view.xml',
        'wizard/doanh_so_phaithu_view.xml',
        'wizard/doanh_so_phaitra_view.xml',
        'wizard/congno_dangchothu_view.xml',
        'wizard/chitiet_congno_tgx_view.xml',
        'wizard/chitiet_congno_thuho_view.xml',
        'wizard/chitiet_congno_kyquy_view.xml',
        'account_data.xml',
        'master_data_view.xml',
        'ql_baohiem_view.xml',
        'partner_view.xml',
        'account_view.xml',
        'account_move_view.xml',
        'account_invoice_phaithu_view.xml',
        'account_invoice_phaichi_view.xml',
        'account_voucher_view.xml',
        'account_journal_view.xml',
        'thu_ky_quy_view.xml',
        'tra_ky_quy_view.xml',
        'account_sequence.xml',
        'user_view.xml',
        'import_manually_view.xml',
        'congno_dauky_view.xml',
        'schedule_view.xml',
        'report_view.xml',
        'menu.xml',
    ],
    'css' : [
    ],
    'qweb': [
    ],
    'js': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: -*-