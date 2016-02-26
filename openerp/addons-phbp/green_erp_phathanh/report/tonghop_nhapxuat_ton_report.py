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
        a = format(amount,',')
        b = a.split('.')
        if len(b)==2 and b[1]!='0':
            so = a
        else:
            so = b[0]
        return so
        
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
        total_sl_5k = 0
        total_sl_10k = 0
        total_sl_20k = 0
        total_sl_50k = 0
        total_thanh_tien = 0
        nhap_mang = []
        mang = []
        sql = '''
            SELECT id FROM nhap_ve order by id
        '''
        self.cr.execute(sql)
        nhap_ids = [r[0] for r in self.cr.fetchall()] 
        for seq,nhap in enumerate(self.pool.get('nhap.ve').browse(self.cr,self.uid,nhap_ids)): 
            sl_5k = 0
            sl_10k = 0
            sl_20k = 0
            sl_50k = 0
            thanh_tien = 0
            for nhap_line in nhap.nhap_ve_line:
                if nhap_line.loai_ve_id.gia_tri==5000:
                    sl_5k = nhap_line.so_luong
                if nhap_line.loai_ve_id.gia_tri==10000:
                    sl_10k = nhap_line.so_luong
                if nhap_line.loai_ve_id.gia_tri==20000:
                    sl_20k = nhap_line.so_luong
                if nhap_line.loai_ve_id.gia_tri==50000:
                    sl_50k = nhap_line.so_luong
            thanh_tien = (sl_5k*5000)+(sl_10k*10000)+(sl_20k*20000)+(sl_50k*50000)
                    
            total_sl_5k += sl_5k
            total_sl_10k += sl_10k
            total_sl_20k += sl_20k
            total_sl_50k += sl_50k
            total_thanh_tien += thanh_tien
                
            nhap_mang.append({
                              'stt': seq+1,
                              'noi_dung':nhap.name,
                              'dvt': u'Vé',
                              '5k': sl_5k,
                              '10k': sl_10k,
                              '20k': sl_20k,
                              '50k': sl_50k,
                              'thanh_tien': thanh_tien,
                              'test': seq+1,
                              'test1': '',
                              })
            
        mang.append({
                    'stt': u'I',
                    'noi_dung': u'Nhập kho đầu kỳ',
                    'dvt': u'Vé',
                    '5k': total_sl_5k,
                    '10k': total_sl_10k,
                    '20k': total_sl_20k,
                    '50k': total_sl_50k,
                    'thanh_tien': total_thanh_tien,
                    'test': '',
                    'test1': '',
                    })
        for line in nhap_mang:
            mang.append({
                    'stt': line['stt'],
                    'noi_dung': line['noi_dung'],
                    'dvt': line['dvt'],
                    '5k': line['5k'],
                    '10k': line['10k'],
                    '20k': line['20k'],
                    '50k': line['50k'],
                    'thanh_tien': line['thanh_tien'],
                    'test': line['test'],
                    'test1': '',
                    })
        
#         Xuất kho
        xuat_mang = []
        total_sl_xuat_5k = 0
        total_sl_xuat_10k = 0
        total_sl_xuat_20k = 0
        total_sl_xuat_50k = 0
        total_thanh_tien_xuat = 0
        sql = '''
            select substr(to_char(name,'YYYY-MM-DD'), 1, 7) as month_year 
            from xuat_ve group by substr(to_char(name,'YYYY-MM-DD'), 1, 7)
        '''
        self.cr.execute(sql)
#         xuat_ids = [r[0] for r in self.cr.fetchall()] 
        for seq_xuat,m_y in enumerate(self.cr.dictfetchall()):
            month_year = m_y['month_year']
            month = month_year[5:]
            year = month_year[:4]
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_xuat_5k
                from xuat_ve_line where loai_ve_id in (select id from loai_ve where gia_tri=5000)
                and xuat_ve_id in (select id from xuat_ve where EXTRACT(month from name)=%s and EXTRACT(year from name)=%s)
            '''%(month,year)
            self.cr.execute(sql)
            sl_xuat_5k = self.cr.dictfetchone()['sl_xuat_5k']
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_xuat_10k
                from xuat_ve_line where loai_ve_id in (select id from loai_ve where gia_tri=10000)
                and xuat_ve_id in (select id from xuat_ve where EXTRACT(month from name)=%s and EXTRACT(year from name)=%s)
            '''%(month,year)
            self.cr.execute(sql)
            sl_xuat_10k = self.cr.dictfetchone()['sl_xuat_10k']
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_xuat_20k
                from xuat_ve_line where loai_ve_id in (select id from loai_ve where gia_tri=20000)
                and xuat_ve_id in (select id from xuat_ve where EXTRACT(month from name)=%s and EXTRACT(year from name)=%s)
            '''%(month,year)
            self.cr.execute(sql)
            sl_xuat_20k = self.cr.dictfetchone()['sl_xuat_20k']
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_xuat_50k
                from xuat_ve_line where loai_ve_id in (select id from loai_ve where gia_tri=50000)
                and xuat_ve_id in (select id from xuat_ve where EXTRACT(month from name)=%s and EXTRACT(year from name)=%s)
            '''%(month,year)
            self.cr.execute(sql)
            sl_xuat_50k = self.cr.dictfetchone()['sl_xuat_50k']
            thanh_tien_xuat = (sl_xuat_5k*5000)+(sl_xuat_10k*10000)+(sl_xuat_20k*20000)+(sl_xuat_50k*50000)
            xuat_mang.append({
                              'stt': seq_xuat+1,
                              'noi_dung':u'Xuất kho tháng '+str(month)+'/'+str(year),
                              'dvt': u'Vé',
                              '5k': sl_xuat_5k,
                              '10k': sl_xuat_10k,
                              '20k': sl_xuat_20k,
                              '50k': sl_xuat_50k,
                              'thanh_tien': thanh_tien_xuat,
                              'test': seq_xuat+1,
                              'test1': '',
                              })
            
            total_sl_xuat_5k += sl_xuat_5k
            total_sl_xuat_10k += sl_xuat_10k
            total_sl_xuat_20k += sl_xuat_20k
            total_sl_xuat_50k += sl_xuat_50k
            total_thanh_tien_xuat += thanh_tien_xuat
            
        mang.append({
                'stt': u'II',
                'noi_dung': u'Xuất kho',
                'dvt': u'Vé',
                '5k': total_sl_xuat_5k,
                '10k': total_sl_xuat_10k,
                '20k': total_sl_xuat_20k,
                '50k': total_sl_xuat_50k,
                'thanh_tien': total_thanh_tien_xuat,
                'test': '',
                'test1': '',
                })
        for line in xuat_mang:
            mang.append({
                    'stt': line['stt'],
                    'noi_dung': line['noi_dung'],
                    'dvt': line['dvt'],
                    '5k': line['5k'],
                    '10k': line['10k'],
                    '20k': line['20k'],
                    '50k': line['50k'],
                    'thanh_tien': line['thanh_tien'],
                    'test': line['test'],
                    'test1': '',
                    })
        ton_5k = total_sl_5k-total_sl_xuat_5k or 0
        ton_10k = total_sl_10k-total_sl_xuat_10k or 0
        ton_20k = total_sl_20k-total_sl_xuat_20k or 0
        ton_50k = total_sl_50k-total_sl_xuat_50k or 0
        ton_thanh_tien = total_thanh_tien-total_thanh_tien_xuat or 0
        mang.append({
                'stt': u'III',
                'noi_dung': u'Tồn kho cuối kỳ',
                'dvt': u'Vé',
                '5k': ton_5k,
                '10k': ton_10k,
                '20k': ton_20k,
                '50k': ton_50k,
                'thanh_tien': ton_thanh_tien,
                'test': '',
                'test1': '',
                })
        tile_tieuthu_5k = float(total_sl_5k) and float(total_sl_xuat_5k)*100/float(total_sl_5k) or 0
        tile_tieuthu_10k = float(total_sl_10k) and float(total_sl_xuat_10k)*100/float(total_sl_10k) or 0
        tile_tieuthu_20k = float(total_sl_20k) and float(total_sl_xuat_20k)*100/float(total_sl_20k) or 0
        tile_tieuthu_50k = float(total_sl_50k) and float(total_sl_xuat_50k)*100/float(total_sl_50k) or 0
        tile_tieuthu_thanhtien = float(total_thanh_tien) and float(total_thanh_tien_xuat)*100/float(total_thanh_tien) or 0
        mang.append({
                'stt': u'IV',
                'noi_dung': u'Tỷ lệ tiêu thụ so vé in ấn',
                'dvt': u'%',
                '5k': round(tile_tieuthu_5k,1),
                '10k': round(tile_tieuthu_10k,1),
                '20k': round(tile_tieuthu_20k,1),
                '50k': round(tile_tieuthu_50k,1),
                'thanh_tien': round(tile_tieuthu_thanhtien,1),
                'test1': u'%',
                'test': '',
                })
        
        tile_tonkho_5k = float(total_sl_5k) and float(ton_5k)*100/float(total_sl_5k) or 0
        tile_tonkho_10k = float(total_sl_10k) and float(ton_10k)*100/float(total_sl_10k) or 0
        tile_tonkho_20k = float(total_sl_20k) and float(ton_20k)*100/float(total_sl_20k) or 0
        tile_tonkho_50k = float(total_sl_50k) and float(ton_50k)*100/float(total_sl_50k) or 0
        tile_tonkho_thanhtien = float(total_thanh_tien) and float(ton_thanh_tien)*100/float(total_thanh_tien) or 0
        mang.append({
                'stt': u'V',
                'noi_dung': u'Tỷ lệ tồn kho so vé in ấn',
                'dvt': u'%',
                '5k': round(tile_tonkho_5k,1),
                '10k': round(tile_tonkho_10k,1),
                '20k': round(tile_tonkho_20k,1),
                '50k': round(tile_tonkho_50k,1),
                'thanh_tien': round(tile_tonkho_thanhtien,1),
                'test1': u'%',
                'test': '',
                })
        return mang
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

