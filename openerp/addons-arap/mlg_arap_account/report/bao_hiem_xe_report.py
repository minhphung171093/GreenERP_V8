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
            'convert_date': self.convert_date,
            'get_loaihinhkinhdoanh': self.get_loaihinhkinhdoanh,
            'get_sotien_conlai': self.get_sotien_conlai,
            'get_sotien_datra': self.get_sotien_datra,
        })
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def get_loaihinhkinhdoanh(self, loai_hinh_kd):
        if loai_hinh_kd=='thuong_quyen':
            return u'Thương quyền'
        else:
            return u'Công ty'
    
    def get_sotien_conlai(self, bh_id):
        return bh_id and self.pool.get('ql.bao.hiem').browse(self.cr, self.uid, bh_id).sotien_conlai or 0
    
    def get_sotien_datra(self, bh_id):
        return bh_id and self.pool.get('ql.bao.hiem').browse(self.cr, self.uid, bh_id).sotien_datra or 0
    
    def get_line(self):
        wizard_data = self.localcontext['data']['form']
        from_date = wizard_data['from_date']
        to_date = wizard_data['to_date']
        sql = '''
            select bh.name as biensoxe, aa.code as machinhanh, aa.name as tenchinhanh, rp.ma_doi_tuong as madoituong, rp.name as tendoituong,
                bh.nha_cung_cap_bh as nha_cung_cap_bh, bh.ngay_tham_gia as ngay_tham_gia, bh.ngay_ket_thuc as ngay_ket_thuc, bh.so_hoa_don as so_hoa_don,
                bh.hieu_xe as hieu_xe, bh.dong_xe as dong_xe, bh.cap_noi_that as cap_noi_that, bh.loai_hinh_kd as loai_hinh_kd,bh.id as bh_id
                
                from ql_bao_hiem bh
                left join account_account aa on bh.chinhanh_id = aa.id
                left join res_partner rp on bh.partner_id = rp.id
                where ngay_tham_gia >= '%s' and ngay_ket_thuc <= '%s' 
        '''%(from_date,to_date)
        
        partner_ids = wizard_data['partner_ids']
        if partner_ids:
            partner_ids = str(partner_ids).replace('[', '(')
            partner_ids = str(partner_ids).replace(']', ')')
            sql+='''
                and bh.partner_id in %s 
            '''%(partner_ids)
        
        so_hoa_don = wizard_data['so_hoa_don']
        if so_hoa_don:
            sql+='''
                and bh.so_hoa_don like '%'''+so_hoa_don+'''%' '''
        
        bien_so_xe = wizard_data['bien_so_xe']
        if bien_so_xe:
            sql+='''
                and bh.name like '%'''+bien_so_xe+'''%' ''' 
        
        self.cr.execute(sql)
        res = self.cr.dictfetchall()
        return res
    
    