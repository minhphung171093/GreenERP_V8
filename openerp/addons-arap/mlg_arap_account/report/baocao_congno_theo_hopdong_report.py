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
        self.tongtien = 0
        self.localcontext.update({
            'get_sohopdong': self.get_sohopdong,
            'get_line': self.get_line,
            'convert_date': self.convert_date,
            'get_tongtien': self.get_tongtien,
            'get_loaicongno': self.get_loaicongno,
            'convert_amount': self.convert_amount,
            'convert': self.convert,
        })
        
    def convert(self, amount):
        amount_text = amount_to_text_vn.amount_to_text(amount, 'vn')
        if amount_text and len(amount_text)>1:
            amount = amount_text[1:]
            head = amount_text[:1]
            amount_text = head.upper()+amount
        return amount_text
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def get_sohopdong(self):
        wizard_data = self.localcontext['data']['form']
        so_hop_dong = wizard_data['so_hop_dong']
        return so_hop_dong
    
    def get_loaicongno(self, mlg_type):
        tt = ''
        if mlg_type=='no_doanh_thu':
            tt='Nợ DT-BH-AL'
        if mlg_type=='chi_ho_dien_thoai':
            tt='Phải thu chi hộ điện thoại'
        if mlg_type=='phai_thu_bao_hiem':
            tt='Phải thu bảo hiểm'
        if mlg_type=='phai_thu_ky_quy':
            tt='Phải thu ký quỹ'
        if mlg_type=='phat_vi_pham':
            tt='Phạt vi phạm'
        if mlg_type=='thu_no_xuong':
            tt='Thu nợ xưởng'
        if mlg_type=='thu_phi_thuong_hieu':
            tt='Thu phí thương hiệu'
        if mlg_type=='tra_gop_xe':
            tt='Trả góp xe'
        if mlg_type=='hoan_tam_ung':
            tt='Phải thu tạm ứng'
        return tt
    
    def get_tongtien(self):
        return self.convert_amount(self.tongtien)
    
    def convert_amount(self, amount):
        a = format(int(amount),',')
#         return a.replace(',',' ')
        return a
    
    def get_line(self):
        wizard_data = self.localcontext['data']['form']
        from_date = wizard_data['from_date']
        to_date = wizard_data['to_date']
        so_hop_dong = wizard_data['so_hop_dong']
        res = []
        sql = '''
            select rp.name as tendoituong, ai.mlg_type as loaicongno, ai.so_tien as sotien
                from account_invoice ai
                left join res_partner rp on ai.partner_id = rp.id
                
                where ai.so_hop_dong='%s' 
        '''%(so_hop_dong)
        if from_date:
            sql += ''' and ai.date_invoice>='%s' '''%(from_date)
        if to_date:
            sql += ''' and ai.date_invoice<='%s' '''%(to_date)
            
        self.cr.execute(sql)
        
        for line in self.cr.dictfetchall():
            res.append({
                'tendoituong': line['tendoituong'],
                'loaicongno': self.get_loaicongno(line['loaicongno']),
                'sotien': self.convert_amount(line['sotien']),
            })
            self.tongtien+=line['sotien']
        return res
    
    