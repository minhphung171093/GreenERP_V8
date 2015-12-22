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
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.phaithu = 0
        self.dathu = 0
        self.localcontext.update({
            'get_from_thang': self.get_from_thang,
            'get_to_thang': self.get_to_thang,
            'convert_date': self.convert_date,
            'get_chinhanh': self.get_chinhanh,
            'convert_amount': self.convert_amount,
            'get_title_doituong': self.get_title_doituong,
            'get_doituong': self.get_doituong,
            'get_bsx': self.get_bsx,
            'get_chitiet_congno': self.get_chitiet_congno,
            'get_payment': self.get_payment,
            'get_phaithu': self.get_phaithu,
            'get_dathu': self.get_dathu,
            'get_tong_phaithu': self.get_tong_phaithu,
            'get_tong_dathu': self.get_tong_dathu,
        })
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        return ''
    
    def convert_amount(self, amount):
        a = format(int(amount),',')
        return a
    
    def get_from_thang(self):
        wizard_data = self.localcontext['data']['form']
        period_id = wizard_data['period_from_id']
        return period_id and period_id[1] or ''
    
    def get_to_thang(self):
        wizard_data = self.localcontext['data']['form']
        period_id = wizard_data['period_to_id']
        return period_id and period_id[1] or ''
    
    def get_chinhanh(self):
        wizard_data = self.localcontext['data']['form']
        chinhanh_id = wizard_data['chinhanh_id']
        if not chinhanh_id:
            return {'name':'','code':''}
        account = self.pool.get('account.account').browse(self.cr, self.uid, chinhanh_id[0])
        return {'name':account.name,'code':account.code}
    
    def get_title_doituong(self, partner_id):
        if partner_id:
            partner = self.pool.get('res.partner').browse(self.cr, self.uid, partner_id)
            return (partner.ma_doi_tuong or '')+'_'+(partner.name or '')
        return ''
    
    def get_doituong(self):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        sql = '''
            select thu_cho_doituong_id from account_invoice where date_invoice between '%s' and '%s' and chinhanh_id=%s
                and state in ('open','paid') and mlg_type='tra_gop_xe' and thu_cho_doituong_id is not null  
        '''%(period_from.date_start,period_to.date_stop,chinhanh_id[0])
        partner_ids = wizard_data['partner_ids']
        if partner_ids:
            partner_ids = str(partner_ids).replace('[', '(')
            partner_ids = str(partner_ids).replace(']', ')')
            sql+='''
                and thu_cho_doituong_id in %s 
            '''%(partner_ids)
        bien_so_xe_ids = wizard_data['bien_so_xe_ids']
        if bien_so_xe_ids:
            bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
            bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
            sql+='''
                and bien_so_xe_id in %s 
            '''%(bien_so_xe_ids)
        sql += ''' group by thu_cho_doituong_id '''
        self.cr.execute(sql)
        partner_ids = [r[0] for r in self.cr.fetchall()]
        return partner_ids
    
    def get_bsx(self, partner_id):
        res = []
        wizard_data = self.localcontext['data']['form']
        if partner_id:
            period_from_id = wizard_data['period_from_id']
            period_to_id = wizard_data['period_to_id']
            period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
            period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
            chinhanh_id = wizard_data['chinhanh_id']
            bien_so_xe_ids = wizard_data['bien_so_xe_ids']
            sql = '''
                select id, name from bien_so_xe where id in (
                        select bien_so_xe_id from account_invoice where mlg_type='tra_gop_xe' and thu_cho_doituong_id=%s and state in ('open','paid')
                            and chinhanh_id=%s and date_invoice between '%s' and '%s'
                    ) 
            '''%(partner_id,chinhanh_id[0],period_from.date_start,period_to.date_stop)
            
            if bien_so_xe_ids:
                bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
                bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
                sql+='''
                    and id in %s 
                '''%(bien_so_xe_ids)
            
            self.cr.execute(sql)
            return self.cr.dictfetchall()
        return res
    
    def get_phaithu(self, partner_id, bsx_id):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        sql = '''
            select case when sum(residual)!=0 then sum(residual) else 0 end phaithu
            
                from account_invoice
                
                where thu_cho_doituong_id=%s and state in ('open') and date_invoice between '%s' and '%s' and chinhanh_id=%s
                    and mlg_type='tra_gop_xe' and bien_so_xe_id=%s
        '''%(partner_id,period_from.date_start,period_to.date_stop,chinhanh_id[0],bsx_id)
        self.cr.execute(sql)
        phaithu = self.cr.fetchone()[0]
        self.phaithu += phaithu
        return phaithu
    
    def get_dathu(self, partner_id, bsx_id):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        sql = '''
            select case when sum(COALESCE(so_tien,0)-COALESCE(residual,0))!=0 then sum(COALESCE(so_tien,0)-COALESCE(residual,0)) else 0 end dathu
            
                from account_invoice
                
                where thu_cho_doituong_id=%s and state in ('open','paid') and date_invoice between '%s' and '%s' and chinhanh_id=%s
                    and mlg_type='tra_gop_xe' and bien_so_xe_id=%s
        '''%(partner_id,period_from.date_start,period_to.date_stop,chinhanh_id[0],bsx_id)
        self.cr.execute(sql)
        dathu = self.cr.fetchone()[0]
        self.dathu += dathu
        return dathu
    
    def get_tong_phaithu(self):
        return self.phaithu
    
    def get_tong_dathu(self):
        return self.dathu
    
    def get_chitiet_congno(self, partner_id, bsx_id):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        sql = '''
            select ai.id as invoice_id,ai.date_invoice as ngay,ai.name as maphieudexuat,rp.ma_doi_tuong as madoituong,rp.name as tendoituong,
                (COALESCE(ai.so_tien,0)) as no, ai.fusion_id as fusion_id,ai.loai_giaodich
            
                from account_invoice ai
                left join res_partner rp on rp.id = ai.thu_cho_doituong_id
                
                where ai.thu_cho_doituong_id=%s and ai.state in ('open','paid') and ai.date_invoice between '%s' and '%s' and ai.chinhanh_id=%s
                    and ai.mlg_type='tra_gop_xe' and ai.bien_so_xe_id=%s
        '''%(partner_id,period_from.date_start,period_to.date_stop,chinhanh_id[0],bsx_id)
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_payment(self, invoice_id):
        if not invoice_id:
            return []
        invoice = self.pool.get('account.invoice').browse(self.cr, self.uid, invoice_id)
        return invoice.payment_ids
    