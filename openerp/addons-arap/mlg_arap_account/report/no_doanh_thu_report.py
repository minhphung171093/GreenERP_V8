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
        self.localcontext.update({
            'get_line': self.get_line,
        })
    
    def get_line(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        sql = '''
            select ai.name as ma_giaodich, ai.date_invoice as ngay_giaodich, rp.ma_doi_tuong as ma_doituong, rp.name as ten_doituong, ldt.name as loai_doituong, dx.code as ma_doixe,
                dx.name as ten_doixe, bgc.code as ma_baigiaoca, bgc.name as ten_baigiaoca, tnbgc.name as thungan_baigiaoca,
                dhbgc.name as dieuhanh_baigiaoca, ail.price_unit as sotien, ail.name as diengiai
                
                from account_invoice_line ail
                left join account_invoice ai on ail.invoice_id = ai.id
                left join res_partner rp on ai.partner_id = rp.id
                left join loai_doi_tuong ldt on ai.loai_doituong_id = ldt.id
                left join account_account dx on ai.account_id = dx.id
                left join bai_giaoca bgc on ai.bai_giaoca_id = bgc.id
                left join thungan_bai_giaoca tnbgc on bgc.thungan_id = tnbgc.id
                left join dieuhanh_bai_giaoca dhbgc on bgc.dieuhanh_id = dhbgc.id
                where date_invoice between '%s' and '%s' and mlg_type='no_doanh_thu' 
        '''%(date_from,date_to)
        
        partner_ids = wizard_data['partner_ids']
        if partner_ids:
            partner_ids = str(partner_ids).replace('[', '(')
            partner_ids = str(partner_ids).replace(']', ')')
            sql+='''
                and ai.partner_id in %s 
            '''%(partner_ids)
        
        doi_xe_ids = wizard_data['doi_xe_ids']
        if doi_xe_ids:
            doi_xe_ids = str(doi_xe_ids).replace('[', '(')
            doi_xe_ids = str(doi_xe_ids).replace(']', ')')
            sql+='''
                and ai.account_id in %s 
            '''%(doi_xe_ids)
            
        bai_giaoca_ids = wizard_data['bai_giaoca_ids']
        if bai_giaoca_ids:
            bai_giaoca_ids = str(bai_giaoca_ids).replace('[', '(')
            bai_giaoca_ids = str(bai_giaoca_ids).replace(']', ')')
            sql+='''
                and ai.bai_giaoca_id in %s 
            '''%(bai_giaoca_ids)
            
        chinhanh_ids = wizard_data['chinhanh_ids']
        if chinhanh_ids:
            chinhanh_ids = str(chinhanh_ids).replace('[', '(')
            chinhanh_ids = str(chinhanh_ids).replace(']', ')')
            sql+='''
                and ai.chinhanh_id in %s 
            '''%(chinhanh_ids)
        
        self.cr.execute(sql)
        res = self.cr.dictfetchall()
        return res
    
    