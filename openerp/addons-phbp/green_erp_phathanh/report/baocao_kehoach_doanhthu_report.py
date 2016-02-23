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
        self.total_kehoach_namtruoc = 0
        self.total_thuchien_namtruoc = 0
        self.total_kehoach_namnay = 0
        self.total_tyle = 0
        self.total_phan_dau = 0
        self.total_tyle_phandau = 0
        self.localcontext.update({
            'convert_date': self.convert_date,
            'get_date': self.get_date,
            'get_ky_ve': self.get_ky_ve,
            'get_loai_ve': self.get_loai_ve,
            'convert_f_amount': self.convert_f_amount,
            'get_lines': self.get_lines,
            'get_year': self.get_year,
        })
        
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
        loai_ve_id = wizard_data['loai_ve_id']
        loai_ve = self.pool.get('loai.ve').browse(self.cr,self.uid,loai_ve_id[0])
        return loai_ve.name
    
    def get_year(self):
        wizard_data = self.localcontext['data']['form']
        year = wizard_data['year']
        return year
    
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
        year = wizard_data['year']
        mang = []
        sql ='''
                select doanh_thu from loai_hinh group by doanh_thu 
                order by doanh_thu desc
            '''
        self.cr.execute(sql)
        for dt in self.cr.dictfetchall():
            line_ids = []
            total_kehoach_namtruoc = 0
            total_thuchien_namtruoc = 0
            total_kehoach_namnay = 0
            total_tyle = 0
            total_phan_dau = 0
            total_tyle_phandau = 0
            sql = '''
                    select chi_tieu_id, kehoach_namtruoc, thuchien_namtruoc, kehoach_namnay, phan_dau 
                    from dt_theo_loaihinh_line where chi_tieu_id in (select id from loai_hinh_line where is_ty_le = 't')
                    and doanh_thu_id in (select id from doanhthu_theo_loaihinh
                    where loai_hinh_id in (select id from loai_hinh where doanh_thu = '%s') and year = %s)
                '''%(dt['doanh_thu'], year)
            self.cr.execute(sql)
            for seq,lh_line in enumerate(self.cr.dictfetchall()):
                kehoach_namtruoc = lh_line['kehoach_namtruoc'] or 0
                thuchien_namtruoc = lh_line['thuchien_namtruoc'] or 0
                kehoach_namnay = lh_line['kehoach_namnay'] or 0
                phan_dau = lh_line['phan_dau'] or 0
                tyle = float(lh_line['thuchien_namtruoc']) and float(lh_line['kehoach_namnay'])*100/float(lh_line['thuchien_namtruoc']) or 0
                tyle_phandau = float(lh_line['thuchien_namtruoc']) and float(lh_line['phan_dau'])*100/float(lh_line['thuchien_namtruoc']) or 0
                line_ids.append({
                                        'stt': seq+1,
                                        'chi_tieu': self.pool.get('loai.hinh.line').browse(self.cr,self.uid,lh_line['chi_tieu_id']).name,
                                        'kehoach_namtruoc': kehoach_namtruoc,
                                        'thuchien_namtruoc': thuchien_namtruoc,
                                        'kehoach_namnay': kehoach_namnay,
                                        'tyle': int(round(tyle,0)),
                                        'phan_dau': phan_dau,
                                        'tyle_phandau': int(round(tyle_phandau,0)),
                                        'test': seq+1,
                                        })
                total_kehoach_namtruoc += kehoach_namtruoc
                total_thuchien_namtruoc += thuchien_namtruoc
                total_kehoach_namnay += kehoach_namnay
                total_tyle = float(total_thuchien_namtruoc) and float(total_kehoach_namnay)*100/float(total_thuchien_namtruoc) or 0
                total_tyle = int(round(total_tyle,0))
                total_phan_dau += phan_dau
                total_tyle_phandau = float(total_thuchien_namtruoc) and float(total_phan_dau)*100/float(total_thuchien_namtruoc) or 0
                total_tyle_phandau = int(round(total_tyle_phandau,0))
                
            self.total_kehoach_namtruoc += total_kehoach_namtruoc
            self.total_thuchien_namtruoc += total_thuchien_namtruoc
            self.total_kehoach_namnay += total_kehoach_namnay
            self.total_tyle = float(self.total_thuchien_namtruoc) and float(self.total_kehoach_namnay)*100/float(self.total_thuchien_namtruoc) or 0
            self.total_tyle = int(round(self.total_tyle,0))
            self.total_phan_dau += total_phan_dau
            self.total_tyle_phandau = float(self.total_thuchien_namtruoc) and float(self.total_phan_dau)*100/float(self.total_thuchien_namtruoc) or 0
            self.total_tyle_phandau = int(round(self.total_tyle_phandau,0))
            if dt['doanh_thu']=='xs':
                stt = u'I'
                chi_tieu = u'Doanh thu xổ số kiến thiết'
            else:
                stt = u'II'
                chi_tieu = u'Doanh thu khách sạn Bom Bo'
            mang.append({
                            'stt': stt,
                            'chi_tieu': chi_tieu,
                            'kehoach_namtruoc': total_kehoach_namtruoc or 0,
                            'thuchien_namtruoc': total_thuchien_namtruoc or 0,
                            'kehoach_namnay': total_kehoach_namnay or 0,
                            'tyle': total_tyle,
                            'phan_dau': total_phan_dau or 0,
                            'tyle_phandau': total_tyle_phandau,
                            'test': '',
                        })
             
            for line in line_ids:
                mang.append({
                            'stt': line['stt'],
                            'chi_tieu': line['chi_tieu'], 
                            'kehoach_namtruoc': line['kehoach_namtruoc'],
                            'thuchien_namtruoc': line['thuchien_namtruoc'],
                            'kehoach_namnay': line['kehoach_namnay'],
                            'tyle': line['tyle'],
                            'phan_dau': line['phan_dau'],
                            'tyle_phandau': line['tyle_phandau'],
                            'test': line['test'],
                                 })
        mang.append({
                        'stt': '',
                        'chi_tieu': u'Tổng',
                        'kehoach_namtruoc': self.total_kehoach_namtruoc or 0,
                        'thuchien_namtruoc': self.total_thuchien_namtruoc or 0,
                        'kehoach_namnay': self.total_kehoach_namnay or 0,
                        'tyle': self.total_tyle,
                        'phan_dau': self.total_phan_dau or 0,
                        'tyle_phandau': self.total_tyle_phandau,
                        'test': '',
                             })
                     
        return mang
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

