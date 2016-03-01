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
            'convert_f_amount': self.convert_f_amount,
            'get_lines': self.get_lines,
            'get_in': self.get_in,
            'get_ton': self.get_ton,
        })
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        
    def convert_f_amount(self, amount):
        a = format(amount,',')
        b = a.split('.')
#         if len(b)==2 and len(b[1])==1:
#             a+='0'
        return b[0]
        
    def get_ky_ve(self):
        wizard_data = self.localcontext['data']['form']
        ky_ve_id = wizard_data['ky_ve_id']
        ky_ve = self.pool.get('ky.ve').browse(self.cr,self.uid,ky_ve_id[0])
        return ky_ve.name
    
    def get_loai_ve(self):
        wizard_data = self.localcontext['data']['form']
        loai_ve_id = wizard_data['loai_ve_id']
        loai_ve = self.pool.get('loai.ve').browse(self.cr,self.uid,loai_ve_id[0])
        return loai_ve.name
    
    def get_in(self):
        wizard_data = self.localcontext['data']['form']
        ky_ve_id = wizard_data['ky_ve_id']
        sql = '''
            select case when sum(sl_ve_in)!=0 then sum(sl_ve_in) else 0 end sl_ve_in from kh_in_ve_tt_line where ky_ve_id = %s 
        '''%(ky_ve_id[0])
        self.cr.execute(sql)
        sl_ve_in = self.cr.dictfetchone()['sl_ve_in']
        return sl_ve_in
    
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
        sql ='''
                SELECT ten,name,id FROM tinh_tp 
                order by name
            '''
        self.cr.execute(sql)
        for tinh in self.cr.dictfetchall():
            line_ids=[]
            total_sl_phathanh = 0
            total_ve_e = 0
            total_sl_tieuthu = 0
            total_thanhtien_tieuthu = 0
            total_ti_le = 0
            total_sl_sosanh_kytruoc = 0
            total_sl_tieuthu_truoc = 0
            total_sl_phathanh_truoc = 0
            total_ti_le_truoc = 0
            total_tile_sosanh_kytruoc = 0
            total_tang_giam = 0
            sql ='''
                SELECT id FROM phanphoi_tt_line where daily_id in (select id from dai_ly where tinh_tp_id = %s) 
                and phanphoi_tt_id in (select id from phanphoi_truyenthong where ky_ve_id = %s and loai_ve_id = %s)
            '''%(tinh['id'],ky_ve_id[0],loai_ve_id[0])
            self.cr.execute(sql)
            dl_ids = [r[0] for r in self.cr.fetchall()]
            if dl_ids:
                for seq,dl in enumerate(self.pool.get('phanphoi.tt.line').browse(self.cr,self.uid,dl_ids)):
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
                    if dl.phanphoi_line_kytruoc_id:
                        sql = '''
                            select case when sum(ve_e_theo_bangke)!=0 then sum(ve_e_theo_bangke) else 0 end tong_ve_e_truoc
                            from nhap_ve_e_line where phanphoi_line_id = %s
                        '''%(dl.phanphoi_line_kytruoc_id.id)
                        self.cr.execute(sql)
                        ve_e_truoc = self.cr.dictfetchone()['tong_ve_e_truoc']
                    else:
                        ve_e_truoc = 0
                        
                    ve = dl.phanphoi_tt_id.loai_ve_id.gia_tri
                    
                    sl_tieuthu = sl_phathanh-ve_e
                    thanhtien_tieuthu = sl_tieuthu*ve
                    ti_le = float(sl_phathanh) and float(sl_tieuthu)*100/float(sl_phathanh) or 0
                    sl_tieuthu_truoc = dl.sove_kytruoc-ve_e_truoc
                    sl_phathanh_truoc = dl.sove_kytruoc
                    sl_sosanh_kytruoc = (sl_tieuthu)-(sl_tieuthu_truoc)
                    ti_le_truoc = float(sl_phathanh_truoc) and float(sl_tieuthu_truoc)*100/float(sl_phathanh_truoc) or 0 
                    doanhthu_kytruoc = (sl_tieuthu_truoc)*ve
                    tang_giam = thanhtien_tieuthu-doanhthu_kytruoc
                    line_ids.append({
                                        'stt': seq+1,
                                        'ten_dl': dl.ten_daily or '',
                                        'ma_dl': dl.daily_id.name or '',
                                        'sl_phathanh': sl_phathanh,
                                        'sl_ve_e': ve_e,
                                        'sl_tieuthu': sl_tieuthu,
                                        'thanhtien_tieuthu': thanhtien_tieuthu,
                                        'ti_le': ti_le,
                                        'sl_sosanh_kytruoc': sl_sosanh_kytruoc,
                                        'tile_sosanh_kytruoc': round(ti_le-ti_le_truoc,1),
                                        'tang_giam': tang_giam,
                                        })
                
                    total_sl_phathanh += sl_phathanh
                    total_ve_e += ve_e
                    total_sl_tieuthu += sl_tieuthu
                    total_thanhtien_tieuthu += thanhtien_tieuthu
                    total_ti_le = float(total_sl_phathanh) and float(total_sl_tieuthu)*100/float(total_sl_phathanh) or 0
                    total_sl_sosanh_kytruoc += sl_sosanh_kytruoc
                    total_sl_tieuthu_truoc += sl_tieuthu_truoc
                    total_sl_phathanh_truoc += sl_phathanh_truoc
                    total_ti_le_truoc = float(total_sl_phathanh_truoc) and float(total_sl_tieuthu_truoc)*100/float(total_sl_phathanh_truoc) or 0
                    total_tile_sosanh_kytruoc = total_ti_le - total_ti_le_truoc
                    total_tang_giam += tang_giam
                
                self.total_sl_phathanh += total_sl_phathanh
                self.total_ve_e += total_ve_e
                self.total_sl_tieuthu += total_sl_tieuthu
                self.total_thanhtien_tieuthu += total_thanhtien_tieuthu
                self.total_ti_le = float(self.total_sl_phathanh) and float(self.total_sl_tieuthu)*100/float(self.total_sl_phathanh) or 0
                self.total_sl_sosanh_kytruoc += total_sl_sosanh_kytruoc
                self.total_sl_tieuthu_truoc += total_sl_tieuthu_truoc
                self.total_sl_phathanh_truoc += total_sl_phathanh_truoc
                self.total_ti_le_truoc = float(self.total_sl_phathanh_truoc) and float(self.total_sl_tieuthu_truoc)*100/float(self.total_sl_phathanh_truoc) or 0
                self.total_tile_sosanh_kytruoc = self.total_ti_le-self.total_ti_le_truoc
                self.total_tang_giam += total_tang_giam
                
                mang.append({
                                'stt': '',
                                'ten_dl': tinh['ten'], 
                                'ma_dl': '',
                                'sl_phathanh': total_sl_phathanh,
                                'sl_ve_e': total_ve_e,
                                'sl_tieuthu': total_sl_tieuthu,
                                'thanhtien_tieuthu': total_thanhtien_tieuthu,
                                'ti_le': round(total_ti_le,1),
                                'sl_sosanh_kytruoc': total_sl_sosanh_kytruoc,
                                'tile_sosanh_kytruoc': round(total_tile_sosanh_kytruoc,1),
                                'tang_giam': total_tang_giam,
                            })
                
                for line in line_ids:
                    mang.append({
                                'stt': line['stt'],
                                'ten_dl': line['ten_dl'], 
                                'ma_dl': line['ma_dl'],
                                'sl_phathanh': line['sl_phathanh'],
                                'sl_ve_e': line['sl_ve_e'],
                                'sl_tieuthu': line['sl_tieuthu'],
                                'thanhtien_tieuthu': line['thanhtien_tieuthu'],
                                'ti_le': round(line['ti_le'],1),
                                'sl_sosanh_kytruoc': line['sl_sosanh_kytruoc'],
                                'tile_sosanh_kytruoc': round(line['tile_sosanh_kytruoc'],1),
                                'tang_giam': line['tang_giam'],
                                     })
        mang.append({
                        'stt': '',
                        'ten_dl': u'TỔNG', 
                        'ma_dl': '',
                        'sl_phathanh': self.total_sl_phathanh,
                        'sl_ve_e': self.total_ve_e,
                        'sl_tieuthu': self.total_sl_tieuthu,
                        'thanhtien_tieuthu': self.total_thanhtien_tieuthu,
                        'ti_le': round(self.total_ti_le,1),
                        'sl_sosanh_kytruoc': self.total_sl_sosanh_kytruoc,
                        'tile_sosanh_kytruoc': round(self.total_tile_sosanh_kytruoc,1),
                        'tang_giam': self.total_tang_giam,
                             })
                    
        return mang
    
    def get_ton(self):
        wizard_data = self.localcontext['data']['form']
        loai_ve_id = wizard_data['loai_ve_id']
        ky_ve_id = wizard_data['ky_ve_id']
        ton = 0
        total_phathanh = 0
        sql = '''
            select sove_sau_dc, phanphoi_line_id
            from dieuchinh_line where dieuchinh_id in (select id from dieuchinh_phanphoi_ve where ky_ve_id = %s and loai_ve_id = %s order by create_date desc limit 1)
            
        '''%(ky_ve_id[0],loai_ve_id[0])
        self.cr.execute(sql)
        dieuchinh_ids = self.cr.fetchall()
        sove_sau_dc_ids = [r[0] for r in dieuchinh_ids]
        phanphoi_ids = [r[1] for r in dieuchinh_ids]
        if phanphoi_ids:
            for co_dc in sove_sau_dc_ids:
                total_phathanh += co_dc
            phanphoi_ids = str(phanphoi_ids).replace('[', '(')
            phanphoi_ids = str(phanphoi_ids).replace(']', ')')
            sql = '''
                select case when sum(sove_kynay)!=0 then sum(sove_kynay) else 0 end sove_kynay
                from phanphoi_tt_line where phanphoi_tt_id in (select id from phanphoi_truyenthong where ky_ve_id = %s and loai_ve_id = %s)
                and id not in %s
            '''%(ky_ve_id[0],loai_ve_id[0],phanphoi_ids)
            self.cr.execute(sql)
            ko_dc = self.cr.dictfetchone()['sove_kynay']
            total_phathanh += ko_dc
        ton = self.get_in()-total_phathanh
        return ton
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

