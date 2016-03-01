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
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
import random
from datetime import date
from dateutil.rrule import rrule, DAILY

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.total_sl_phathanh = 0
        self.total_ve_e = 0
        self.total_sl_tieuthu = 0
        self.total_thanhtien_tieuthu = 0
        self.total_ti_le = 0
        self.total_sl_sosanh_kytruoc = 0
        self.total_sl_tieuthu_truoc = 0
        self.total_sl_phathanh_truoc = 0
        self.total_ti_le_truoc = 0
        self.total_tile_sosanh_kytruoc = 0
        self.total_tang_giam = 0
        self.localcontext.update({
            'convert_date': self.convert_date,
            'get_date': self.get_date,
            'get_ky_ve': self.get_ky_ve,
            'get_loai_ve': self.get_loai_ve,
            'get_menh_gia': self.get_menh_gia,
            'convert_f_amount': self.convert_f_amount,
            'get_lines': self.get_lines,
            'get_in': self.get_in,
            'get_namekv': self.get_namekv,
            'get_ngay_mt': self.get_ngay_mt,
        })
    
    def get_namekv(self):
        wizard_data = self.localcontext['data']['form']
        name = wizard_data['name']
        return name
    
    def get_ngay_mt(self):
        wizard_data = self.localcontext['data']['form']
        ngay = wizard_data['ngay_mo_thuong']
        return ngay
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        
    def convert_f_amount(self, amount):
        if amount:
            a = format(amount,',')
            b = a.split('.')
    #         if len(b)==2 and len(b[1])==1:
    #             a+='0'
            return b[0]
        else:
            return ''
        
    def get_ky_ve(self):
        wizard_data = self.localcontext['data']['form']
        ky_ve_id = wizard_data['ky_ve_id']
        ky_ve = self.pool.get('ky.ve').browse(self.cr,self.uid,ky_ve_id[0])
        return ky_ve.name
    
    def get_loai_ve(self):
        wizard_data = self.localcontext['data']['form']
        loai_ve = wizard_data['loai_ve']
        if loai_ve == 'tt':
            return u'Truyền thống'
        if loai_ve == 'tc':
            return u'Tự chọn'
    
    def get_menh_gia(self):
        wizard_data = self.localcontext['data']['form']
        loai_ve_id = wizard_data['loai_ve_id']
        loai_ve = self.pool.get('loai.ve').browse(self.cr,self.uid,loai_ve_id[0])
        return loai_ve.name
    
    def get_in(self):
        wizard_data = self.localcontext['data']['form']
        ky_ve_id = wizard_data['ky_ve_id']
        sql = '''
            select sl_ve_in from kh_in_ve_tt_line where ky_ve_id = %s 
        '''%(ky_ve_id[0])
        self.cr.execute(sql)
        sl_ve_in = self.cr.fetchone()
        if sl_ve_in:
            sl_ve = sl_ve_in[0]
        else:
            sl_ve = 0
        return sl_ve
    
    def get_date(self):
        res={}
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['ngay_mo_thuong']
        day = date[8:10],
        month = date[5:7],
        year = date[:4],
        res={
            'day' : day,
            'month' : month,
            'year' : year,
            }
        return res
    
    def get_lines(self):
        wizard_data = self.localcontext['data']['form']
        loai_ve_id = wizard_data['loai_ve_id']
        ky_ve_id = wizard_data['ky_ve_id']
        mang = []
        sql = '''
            SELECT id FROM phanphoi_tt_line 
            where phanphoi_tt_id in (select id from phanphoi_truyenthong where ky_ve_id = %s and loai_ve_id = %s)
        '''%(ky_ve_id[0],loai_ve_id[0])
        self.cr.execute(sql)
        dl_ids = [r[0] for r in self.cr.fetchall()]
        total_sl_phathanh = 0
        total_ve_e = 0
        total_sl_tieuthu = 0
        total_sl_tonkho = 0
        total_thanhtien_tieuthu = 0
        ve = 0
        for dl in self.pool.get('phanphoi.tt.line').browse(self.cr,self.uid,dl_ids):
            sql = '''
                select case when sum(sl_ve_in)!=0 then sum(sl_ve_in) else 0 end sl_ve_in from kh_in_ve_tt_line where ky_ve_id = %s 
            '''%(ky_ve_id[0])
            self.cr.execute(sql)
            sl_ve_in = self.cr.dictfetchone()['sl_ve_in']
            sql = '''
                select sove_sau_dc from dieuchinh_line where phanphoi_line_id = %s order by create_date desc limit 1
            '''%(dl.id)
            self.cr.execute(sql)
            co_dc = self.cr.fetchone()
            if co_dc:
                sl_phathanh = co_dc[0]
            else:
                sl_phathanh = dl.sove_kynay
            sql = '''
                select case when sum(ve_e_theo_bangke)!=0 then sum(ve_e_theo_bangke) else 0 end tong_ve_e
                from nhap_ve_e_line where phanphoi_line_id = %s
            '''%(dl.id)
            self.cr.execute(sql)
            ve_e = self.cr.dictfetchone()['tong_ve_e']
            ve = dl.phanphoi_tt_id.loai_ve_id.gia_tri
            
            sl_tieuthu = sl_phathanh-ve_e
            thanhtien_tieuthu = sl_tieuthu*ve
            thanhtien_ve_in = sl_ve_in*ve
        
            total_sl_phathanh += sl_phathanh
            total_sl_tonkho = sl_ve_in - total_sl_phathanh
            total_ve_e += ve_e
            total_sl_tieuthu += sl_tieuthu
            total_thanhtien_tieuthu += thanhtien_tieuthu
        
#         self.total_sl_phathanh += total_sl_phathanh
#         self.total_ve_e += total_ve_e
#         self.total_sl_tieuthu += total_sl_tieuthu
#         self.total_thanhtien_tieuthu += total_thanhtien_tieuthu
        
        mang.append({
                        'stt': u'1',
                        'chi_tieu': u'Số lượng vé in ấn', 
                        'so_luong': sl_ve_in,
                        'gia_tri': thanhtien_ve_in,
                    })
        
        mang.append({
                    'stt': u'2',
                    'chi_tieu': u'Số lượng vé chưa đưa vào lưu thông (vé tồn kho)', 
                    'so_luong': total_sl_tonkho,
                    'gia_tri': total_sl_tonkho*ve,
                         })
        
        mang.append({
                    'stt': u'3',
                    'chi_tieu': u'Số lượng vé đưa vào lưu thông (vé phát hành)', 
                    'so_luong': total_sl_phathanh,
                    'gia_tri': total_sl_phathanh*ve,
                             })
        
        mang.append({
                    'stt': u'4',
                    'chi_tieu': u'Số lượng vé đã phát hành không tiêu thụ hết (vé ế)', 
                    'so_luong': total_ve_e,
                    'gia_tri': total_ve_e*ve,
                             })
        
        mang.append({
                    'stt': u'5',
                    'chi_tieu': u'Số lượng vé tiêu thụ', 
                    'so_luong': total_sl_phathanh-total_ve_e,
                    'gia_tri': (total_sl_phathanh-total_ve_e)*ve,
                             })
                    
        return mang
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

