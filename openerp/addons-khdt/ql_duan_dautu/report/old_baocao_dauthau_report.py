# -*- coding: utf-8 -*-
##############################################################################
#
#    HLVSolution, Open Source Management Solution
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
import random
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.danhmuc_tam=[]
        self.danhmuc_arr=[]
        self.tongso = 0.0
        self.localcontext.update({
             'get_from_date':self.get_from_date,
             'get_to_date':self.get_to_date,
             'get_vietname_date': self.get_vietname_date,
             'get_sum_linhvuc_dauthau_theonhom': self.get_sum_linhvuc_dauthau_theonhom,
             'get_linhvuc_dautu_theonhom': self.get_linhvuc_dautu_theonhom,
             'get_linhvuc_dautu_line': self.get_linhvuc_dautu_line,
             'get_hinhthuc_theonhom': self.get_hinhthuc_theonhom,
             'get_hinhthuc_line': self.get_hinhthuc_line,
        })
    
    def get_vietname_date(self, date):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_from_date(self):
        wizard_data = self.localcontext['data']['form']
        from_date = wizard_data['date_from']
        return from_date
    
    def get_to_date(self):
        wizard_data = self.localcontext['data']['form']
        to_date = wizard_data['date_to']
        return to_date
    
    def get_sum_linhvuc_dauthau_theonhom(self,nhom):
        wizard_data = self.localcontext['data']['form']
        from_date = wizard_data['date_from']
        to_date = wizard_data['date_to']
        sql = '''
            SELECT CASE WHEN count(id)!= 0 THEN count(id) ELSE 0 END as sogoithau ,
                CASE WHEN sum(pheduyet_giagoithau)!= 0 THEN round(sum(pheduyet_giagoithau)/1000000,0) ELSE 0 END as tonggiagoithau,
                CASE WHEN sum(pheduyet_giatrungthau)!= 0 THEN round(sum(pheduyet_giatrungthau)/1000000,0) ELSE 0 END as tonggiatrungthau,
                (CASE WHEN sum(pheduyet_giagoithau)!= 0 THEN round(sum(pheduyet_giagoithau)/1000000,0) ELSE 0 END)-(CASE WHEN sum(pheduyet_giatrungthau)!= 0 THEN round(sum(pheduyet_giatrungthau)/1000000,0) ELSE 0 END) as chenhlech
            FROM pheduyet_kqdt
            WHERE (pheduyet_kqdt_ngay between '%(from_date)s' and '%(to_date)s')
            and duan_dautu_id in (select id from duan_dautu where nhom_id in (select id from duan_nhom where name in (%(nhom)s)))
        '''%{'from_date': from_date,
             'to_date': to_date,
             'nhom':nhom}
        self.cr.execute(sql)
        return self.cr.dictfetchall()[0]
    
    def get_linhvuc_dautu_line(self):
        linhvuc_obj = self.pool.get('linhvuc.dauthau')
        linhvuc_ids = linhvuc_obj.search(self.cr, self.uid, [])
        linhvucs = linhvuc_obj.browse(self.cr, self.uid, linhvuc_ids)
        return linhvucs
    
    def get_linhvuc_dautu_theonhom(self,linhvuc_id,nhom):
        wizard_data = self.localcontext['data']['form']
        from_date = wizard_data['date_from']
        to_date = wizard_data['date_to']
        sql = '''
            SELECT CASE WHEN count(id)!= 0 THEN count(id) ELSE 0 END as sogoithau,
                CASE WHEN sum(pheduyet_giagoithau)!= 0 THEN round(sum(pheduyet_giagoithau)/1000000,0) ELSE 0 END as tonggiagoithau,
                CASE WHEN sum(pheduyet_giatrungthau)!= 0 THEN round(sum(pheduyet_giatrungthau)/1000000,0) ELSE 0 END as tonggiatrungthau,
                (CASE WHEN sum(pheduyet_giagoithau)!= 0 THEN round(sum(pheduyet_giagoithau)/1000000,0) ELSE 0 END)-(CASE WHEN sum(pheduyet_giatrungthau)!= 0 THEN round(sum(pheduyet_giatrungthau)/1000000,0) ELSE 0 END) as chenhlech
            FROM pheduyet_kqdt
            WHERE linhvuc_dauthau_id = %(linhvuc_id)s
                and (pheduyet_kqdt_ngay between '%(from_date)s' and '%(to_date)s')
                and duan_dautu_id in (select id from duan_dautu where nhom_id in (select id from duan_nhom where name in (%(nhom)s)))
        '''%{'from_date': from_date,
             'to_date': to_date,
             'nhom':nhom,
             'linhvuc_id':linhvuc_id}
        self.cr.execute(sql)
        return self.cr.dictfetchall()[0]
    
    def get_hinhthuc_line(self):
        hinhthuc_obj = self.pool.get('hinhthuc.luachon.nhathau')
        hinhthuc_ids = hinhthuc_obj.search(self.cr, self.uid, [])
        hinhthucs = hinhthuc_obj.browse(self.cr, self.uid, hinhthuc_ids)
        return hinhthucs
    
    def get_hinhthuc_theonhom(self,hinhthuc_id,nhom):
        wizard_data = self.localcontext['data']['form']
        from_date = wizard_data['date_from']
        to_date = wizard_data['date_to']
        sql = '''
            SELECT CASE WHEN count(id)!= 0 THEN count(id) ELSE 0 END as sogoithau,
                CASE WHEN sum(pheduyet_giagoithau)!= 0 THEN round(sum(pheduyet_giagoithau)/1000000,0) ELSE 0 END as tonggiagoithau,
                CASE WHEN sum(pheduyet_giatrungthau)!= 0 THEN round(sum(pheduyet_giatrungthau)/1000000,0) ELSE 0 END as tonggiatrungthau,
                (CASE WHEN sum(pheduyet_giagoithau)!= 0 THEN round(sum(pheduyet_giagoithau)/1000000,0) ELSE 0 END)-(CASE WHEN sum(pheduyet_giatrungthau)!= 0 THEN round(sum(pheduyet_giatrungthau)/1000000,0) ELSE 0 END) as chenhlech
            FROM pheduyet_kqdt
            WHERE hinhthuc_luachon_nhathau_id = %(hinhthuc_id)s
                and (pheduyet_kqdt_ngay between '%(from_date)s' and '%(to_date)s')
                and duan_dautu_id in (select id from duan_dautu where nhom_id in (select id from duan_nhom where name in (%(nhom)s)))
        '''%{'from_date': from_date,
             'to_date': to_date,
             'nhom':nhom,
             'hinhthuc_id':hinhthuc_id}
        self.cr.execute(sql)
        return self.cr.dictfetchall()[0]
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
