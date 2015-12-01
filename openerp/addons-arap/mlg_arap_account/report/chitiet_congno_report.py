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
            'get_title': self.get_title,
            'get_nocuoiky': self.get_nocuoiky,
            'get_tongcongno': self.get_tongcongno,
            'get_thang': self.get_thang,
            'get_payment': self.get_payment,
            'get_chinhanh': self.get_chinhanh,
        })
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        return ''
    
    def convert_amount(self, amount):
        a = format(int(amount),',')
        return a
    
    def get_thang(self):
        wizard_data = self.localcontext['data']['form']
        period_id = wizard_data['period_id']
        return period_id and period_id[1] or ''
    
    def get_chinhanh(self):
        wizard_data = self.localcontext['data']['form']
        chinhanh_id = wizard_data['chinhanh_id']
        if not chinhanh_id:
            return {'name':'','code':''}
        account = self.pool.get('account.account').browse(self.cr, self.uid, chinhanh_id[0])
        return {'name':account.name,'code':account.code}
    
    def get_doituong(self):
        wizard_data = self.localcontext['data']['form']
        partner_ids = wizard_data['partner_ids']
        if partner_ids:
            return partner_ids
        else:
            period_id = wizard_data['period_id']
            chinhanh_id = wizard_data['chinhanh_id']
            period = self.pool.get('account.period').browse(self.cr, self.uid, period_id[0])
            mlg_type = wizard_data['mlg_type']
            sql = '''
                select partner_id from account_invoice where date_invoice between '%s' and '%s' and chinhanh_id=%s
                    and state in ('open','paid') and mlg_type='%s' 
            '''%(period.date_start,period.date_stop,chinhanh_id[0],mlg_type)
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
                    and id in (select congno_dauky_id from congno_dauky_line where chinhanh_id=%s and mlg_type='%s')
            '''%(period_id[0],chinhanh_id[0],mlg_type)
            self.cr.execute(sql)
            for partner_id in self.cr.fetchall():
                if partner_id[0] not in partner_ids:
                    partner_ids.append(partner_id[0])
            return partner_ids
    
    def get_title(self):
        wizard_data = self.localcontext['data']['form']
        mlg_type = wizard_data['mlg_type']
        tt = ''
        if mlg_type=='no_doanh_thu':
            tt='NỢ DOANH THU'
        if mlg_type=='chi_ho_dien_thoai':
            tt='CHI HỘ ĐIỆN THOẠI'
        if mlg_type=='phai_thu_bao_hiem':
            tt='BẢO HIỂM'
        if mlg_type=='phat_vi_pham':
            tt='PHẠT VI PHẠM'
        if mlg_type=='thu_no_xuong':
            tt='NỢ XƯỞNG'
        if mlg_type=='thu_phi_thuong_hieu':
            tt='PHÍ THƯƠNG HIỆU'
        if mlg_type=='tra_gop_xe':
            tt='TRẢ GÓP XE'
        if mlg_type=='hoan_tam_ung':
            tt='TẠM ỨNG'
        if mlg_type=='phai_tra_ky_quy':
            tt='TRẢ KÝ QUỸ'
        if mlg_type=='chi_ho':
            tt='CHI HỘ'
        return tt
    
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
            mlg_type = wizard_data['mlg_type']
            sql = '''
                select case when sum(so_tien_no)!=0 then sum(so_tien_no) else 0 end nodauky
                    from congno_dauky_line where mlg_type='%s' and chinhanh_id=%s
                        and congno_dauky_id in (select id from congno_dauky where partner_id=%s and period_id=%s)
            '''%(mlg_type,chinhanh_id[0],partner_id,period_id[0])
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
            mlg_type = wizard_data['mlg_type']
            sql = '''
                select case when sum(residual)!=0 then sum(residual) else 0 end notrongky
                    from account_invoice where mlg_type='%s' and chinhanh_id=%s and partner_id=%s
                        and date_invoice between '%s' and '%s' and state in ('open','paid') 
            '''%(mlg_type,chinhanh_id[0],partner_id,period.date_start,period.date_stop)
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
        mlg_type = wizard_data['mlg_type']
        sql = '''
            select ai.id as invoice_id,ai.date_invoice as ngay,ai.name as maphieudexuat,rp.ma_doi_tuong as madoituong,rp.name as tendoituong,
                ai.so_tien as no, (ai.so_tien-ai.residual) as co,ai.fusion_id as fusion_id
            
                from account_invoice ai
                left join res_partner rp on rp.id = ai.partner_id
                
                where ai.partner_id=%s and ai.state in ('open','paid') and ai.date_invoice between '%s' and '%s' and ai.chinhanh_id=%s
                    and ai.mlg_type='%s'
        '''%(partner_id,period.date_start,period.date_stop,chinhanh_id[0],mlg_type)
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_payment(self, invoice_id):
        if not invoice_id:
            return []
        invoice = self.pool.get('account.invoice').browse(self.cr, self.uid, invoice_id)
        return invoice.payment_ids
            
    
    