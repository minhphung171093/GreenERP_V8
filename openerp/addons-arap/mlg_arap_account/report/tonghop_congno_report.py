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
        self.tongcongno = 0
        self.localcontext.update({
            'get_doituong': self.get_doituong,
            'convert_date': self.convert_date,
            'get_title_doituong': self.get_title_doituong,
            'get_nodauky': self.get_nodauky,
            'convert_amount': self.convert_amount,
            'get_chitiet_congno': self.get_chitiet_congno,
            'get_nocuoiky': self.get_nocuoiky,
            'get_tongcongno': self.get_tongcongno,
            'get_loaidoituong': self.get_loaidoituong,
        })
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        return ''
    
    def convert_amount(self, amount):
        a = format(int(amount),',')
        return a
    
    def get_loaidoituong(self, mlg_type):
        tt = ''
        if mlg_type=='no_doanh_thu':
            tt='Nợ doanh thu'
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
        if mlg_type=='phai_tra_ky_quy':
            tt='Phải trả ký quỹ'
        if mlg_type=='chi_ho':
            tt='Phải trả chi hộ'
        return tt
    
    def get_doituong(self):
        wizard_data = self.localcontext['data']['form']
        partner_ids = wizard_data['partner_ids']
        if partner_ids:
            return partner_ids
        else:
            period_id = wizard_data['period_id']
            chinhanh_id = wizard_data['chinhanh_id']
            period = self.pool.get('account.period').browse(self.cr, self.uid, period_id[0])
            sql = '''
                select partner_id from account_invoice where date_invoice between '%s' and '%s' and chinhanh_id=%s
                    and state in ('open','paid') 
            '''%(period.date_start,period.date_stop,chinhanh_id[0])
            doi_xe_ids = wizard_data['doi_xe_ids']
            if doi_xe_ids:
                doi_xe_ids = str(doi_xe_ids).replace('[', '(')
                doi_xe_ids = str(doi_xe_ids).replace(']', ')')
                sql+='''
                    and account_id in %s 
                '''%(doi_xe_ids)
            bai_giaoca_ids = wizard_data['bai_giaoca_ids']
            if bai_giaoca_ids:
                bai_giaoca_ids = str(bai_giaoca_ids).replace('[', '(')
                bai_giaoca_ids = str(bai_giaoca_ids).replace(']', ')')
                sql+='''
                    and bai_giaoca_id in %s 
                '''%(bai_giaoca_ids)
            self.cr.execute(sql)
            partner_ids = [r[0] for r in self.cr.fetchall()]
            sql = '''
                select partner_id from congno_dauky where period_id=%s
                    and id in (select congno_dauky_id from congno_dauky_line where chinhanh_id=%s)
            '''%(period_id[0],chinhanh_id[0])
            self.cr.execute(sql)
            for partner_id in self.cr.fetchall():
                if partner_id not in partner_ids:
                    partner_ids.append(partner_id)
            return partner_ids
    
    def get_title_doituong(self, partner_id):
        if partner_id:
            partner = self.pool.get('res.partner').browse(self.cr, self.uid, partner_id)
            return (partner.ma_doi_tuong or '')+'_'+(partner.name or '')
        return ''
    
    def get_nodauky(self, partner_id):
        wizard_data = self.localcontext['data']['form']
        if partner_id:
            period_id = wizard_data['period_id']
            period = self.pool.get('account.period').browse(self.cr, self.uid, period_id[0])
            chinhanh_id = wizard_data['chinhanh_id']
            sql = '''
                select case when sum(so_tien_no)!=0 then sum(so_tien_no) else 0 end nodauky
                    from congno_dauky_line where chinhanh_id=%s
                        and congno_dauky_id in (select id from congno_dauky where partner_id=%s and period_id=%s)
            '''%(chinhanh_id[0],partner_id,period_id[0])
            self.cr.execute(sql)
            return self.cr.fetchone()[0]
        return 0
    
    def get_tongcongno(self):
        return self.tongcongno
    
    def get_nocuoiky(self, partner_id):
        wizard_data = self.localcontext['data']['form']
        if partner_id:
            period_id = wizard_data['period_id']
            period = self.pool.get('account.period').browse(self.cr, self.uid, period_id[0])
            chinhanh_id = wizard_data['chinhanh_id']
            sql = '''
                select case when sum(residual)!=0 then sum(residual) else 0 end notrongky
                    from account_invoice where chinhanh_id=%s and partner_id=%s
                        and date_invoice between '%s' and '%s' and state in ('open','paid') 
            '''%(chinhanh_id[0],partner_id,period.date_start,period.date_stop)
            self.cr.execute(sql)
            notrongky = self.cr.fetchone()[0]
            nodauky = self.get_nodauky(partner_id)
            nocuoiky = nodauky+notrongky
            self.tongcongno += nocuoiky
            return nocuoiky
        return 0
    
    def get_chitiet_congno(self, partner_id):
        wizard_data = self.localcontext['data']['form']
        period_id = wizard_data['period_id']
        chinhanh_id = wizard_data['chinhanh_id']
        period = self.pool.get('account.period').browse(self.cr, self.uid, period_id[0])
        sql = '''
            select ai.mlg_type as loaicongno,
                sum(ai.so_tien) as no, sum(ai.so_tien-ai.residual) as co
            
                from account_invoice ai
                left join res_partner rp on rp.id = ai.partner_id
                
                where ai.partner_id=%s and ai.state in ('open','paid') and ai.date_invoice between '%s' and '%s' and ai.chinhanh_id=%s
                
                group by ai.mlg_type
        '''%(partner_id,period.date_start,period.date_stop,chinhanh_id[0])
        self.cr.execute(sql)
        return self.cr.dictfetchall()
            
    
    