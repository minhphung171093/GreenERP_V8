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
        self.localcontext.update({
            'convert_date': self.convert_date,
            'get_date': self.get_date,
            'get_ky_ve': self.get_ky_ve,
            'get_loai_ve': self.get_loai_ve,
            'convert_f_amount': self.convert_f_amount,
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
        sql ='''
                SELECT ten,name,id FROM tinh_tp 
                order by name
            '''
        self.cr.execute(sql)
        for tinh in self.cr.dictfetchall():
            line_ids=[]
            total_ph = 0
            total_ve = 0
            total_sl_tieuthu = 0
            total_thanhtien_tieuthu = 0
            total_doanhthu_tieuthu = 0
            total_tanggiam = 0
            sql ='''
                SELECT id FROM phanphoi_tt_line where daily_id in (select id from dai_ly where tinh_tp_id = %s) 
                and phanphoi_tt_id in (select id from phanphoi_truyenthong where ky_ve_id = %s and loai_ve_id = %s)
            '''%(tinh['id'],ky_ve_id[0],loai_ve_id[0])
            self.cr.execute(sql)
            dl_ids = [r[0] for r in cr.fetchall()]
            if dl_ids:
                for seq,dl in enumerate(self.pool.get('phanphoi.tt.line').browse(self.cr,self.uid,dl_ids)):
                    sql = '''
                        select sove_sau_dc from dieuchinh_line where phanphoi_line_id = %s
                    '''%(dl.id)
                    self.cr.execute(sql)
                    co_dc = cr.fetchone()
                    if co_dc:
                        sl_phathanh = co_dc[0]
                    else:
                        sl_phathanh = dl.sove_kynay
                    line_ids.append({
                                        'stt': seq+1,
                                        'ten_dl': dl.ten_dl or '',
                                        'ma_dl': dl.daily_id.name or '',
                                        'sl_phathanh': sl_phathanh,
                                        })
                
                
            
            
            
            
        return loai_ve.name
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

