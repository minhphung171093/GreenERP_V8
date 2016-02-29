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
        self.sdtlkdauky = 0
        self.sdttrongky = 0
        self.sdtlkcuoiky = 0
        self.tong_sdtlkdauky = 0
        self.tong_sdttrongky = 0
        self.tong_sdtlkcuoiky = 0
        self.localcontext.update({
            'get_doituong': self.get_doituong,
            'convert_date': self.convert_date,
            'get_title_doituong': self.get_title_doituong,
            'convert_amount': self.convert_amount,
            'get_from_thang': self.get_from_thang,
            'get_to_thang': self.get_to_thang,
            'get_chinhanh': self.get_chinhanh,
            'get_bsx': self.get_bsx,
            'get_sdtlkdauky': self.get_sdtlkdauky,
            'get_sdttrongky': self.get_sdttrongky,
            'get_sdtlkcuoiky': self.get_sdtlkcuoiky,
            'get_cong_sdtlkdauky': self.get_cong_sdtlkdauky,
            'get_cong_sdttrongky': self.get_cong_sdttrongky,
            'get_cong_sdtlkcuoiky': self.get_cong_sdtlkcuoiky,
            'get_tongcong_sdtlkdauky': self.get_tongcong_sdtlkdauky,
            'get_tongcong_sdttrongky': self.get_tongcong_sdttrongky,
            'get_tongcong_sdtlkcuoiky': self.get_tongcong_sdtlkcuoiky,
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
    
    def get_doituong(self):
        wizard_data = self.localcontext['data']['form']
        partner_ids = wizard_data['partner_ids']
        chinhanh_id = wizard_data['chinhanh_id']
        if partner_ids:
            return partner_ids
        else:
            partner_ids = []
            sql='''
                select partner_id from chi_nhanh_line where chinhanh_id=%s and partner_id in (select id from res_partner where nhadautugiantiep=True) group by partner_id
            '''%(chinhanh_id[0])
            self.cr.execute(sql)
            for r in self.cr.fetchall():
                partner_ids.append(r[0])
            return partner_ids
    
    def get_title_doituong(self, partner_id):
        if partner_id:
            partner = self.pool.get('res.partner').browse(self.cr, self.uid, partner_id)
            return (partner.ma_doi_tuong or '')+'_'+(partner.name or '')
        return ''
    
    def get_bsx(self, partner_id):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        tat_toan = wizard_data['tat_toan']
        sql = '''
            select id, name from bien_so_xe where id in (
                    select bien_so_xe_id from account_invoice where mlg_type='tra_gop_xe' and thu_cho_doituong_id=%s and state in ('open','paid')
                        and chinhanh_id=%s and date_invoice<='%s' and so_tien!=residual 
        '''%(partner_id,chinhanh_id[0],period_to.date_stop)
        if not tat_toan:
            sql +='''
                and (ngay_tat_toan is null or (ngay_tat_toan is not null and '%s'<ngay_tat_toan)) 
                ) 
            '''%(period_to.date_stop)
        else:
            sql +='''
                and tat_toan=True and ngay_tat_toan<='%s' 
                ) 
            '''%(period_to.date_stop)
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_cong_sdtlkdauky(self):
        sdtlkdauky = self.sdtlkdauky
        self.tong_sdtlkdauky += sdtlkdauky
        self.sdtlkdauky = 0
        return sdtlkdauky
    
    def get_cong_sdttrongky(self):
        sdttrongky = self.sdttrongky
        self.tong_sdttrongky += sdttrongky
        self.sdttrongky = 0
        return sdttrongky
    
    def get_cong_sdtlkcuoiky(self):
        sdtlkcuoiky = self.sdtlkcuoiky
        self.tong_sdtlkcuoiky += sdtlkcuoiky
        self.sdtlkcuoiky = 0
        return sdtlkcuoiky
    
    def get_tongcong_sdtlkdauky(self):
        tong_sdtlkdauky = self.tong_sdtlkdauky
        self.tong_sdtlkdauky = 0
        return tong_sdtlkdauky
    
    def get_tongcong_sdttrongky(self):
        tong_sdttrongky = self.tong_sdttrongky
        self.tong_sdttrongky = 0
        return tong_sdttrongky
    
    def get_tongcong_sdtlkcuoiky(self):
        tong_sdtlkcuoiky = self.tong_sdtlkcuoiky
        self.tong_sdtlkcuoiky = 0
        return tong_sdtlkcuoiky
    
    def get_sdtlkdauky(self, partner_id,bsx_id):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        tat_toan = wizard_data['tat_toan']
        sql = '''
            select case when sum(credit)!=0 then sum(credit) else 0 end sotien
                from account_move_line
                where move_id in (select move_id from account_voucher
                    where reference in (select name from account_invoice
                        where mlg_type='tra_gop_xe' and state in ('open','paid') and chinhanh_id=%s and thu_cho_doituong_id=%s and date_invoice<='%s'
                           
        '''%(chinhanh_id[0],partner_id,period_to.date_stop)
        if not tat_toan:
            sql +='''
                and (ngay_tat_toan is null or (ngay_tat_toan is not null and '%s'<ngay_tat_toan)) and bien_so_xe_id=%s ))
                    and date<'%s'
            '''%(period_to.date_stop,bsx_id,period_from.date_start)
        else:
            sql +='''
                and tat_toan=True and ngay_tat_toan<='%s' and bien_so_xe_id=%s ))
                    and date<'%s'
            '''%(period_to.date_stop,bsx_id,period_from.date_start)
        self.cr.execute(sql)
        sdtlkdauky = self.cr.fetchone()[0]
        self.sdtlkdauky += sdtlkdauky
        return sdtlkdauky
        
    def get_sdttrongky(self, partner_id,bsx_id):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        tat_toan = wizard_data['tat_toan']
        sql = '''
            select case when sum(credit)!=0 then sum(credit) else 0 end sotien
                from account_move_line
                where move_id in (select move_id from account_voucher
                    where reference in (select name from account_invoice
                        where mlg_type='tra_gop_xe' and state in ('open','paid') and chinhanh_id=%s and thu_cho_doituong_id=%s and date_invoice<='%s'
                           
        '''%(chinhanh_id[0],partner_id,period_to.date_stop)
        if not tat_toan:
            sql +='''
                and (ngay_tat_toan is null or (ngay_tat_toan is not null and '%s'<ngay_tat_toan)) and bien_so_xe_id=%s ))
                    and date between '%s' and '%s'
            '''%(period_to.date_stop,bsx_id,period_from.date_start,period_to.date_stop)
        else:
            sql +='''
                and tat_toan=True and ngay_tat_toan<='%s' and bien_so_xe_id=%s ))
                    and date between '%s' and '%s'
            '''%(period_to.date_stop,bsx_id,period_from.date_start,period_to.date_stop)
        self.cr.execute(sql)
        sdttrongky = self.cr.fetchone()[0]
        self.sdttrongky += sdttrongky
        return sdttrongky
    
    def get_sdtlkcuoiky(self, partner_id,bsx_id):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        tat_toan = wizard_data['tat_toan']
        sql = '''
            select case when sum(credit)!=0 then sum(credit) else 0 end sotien
                from account_move_line
                where move_id in (select move_id from account_voucher
                    where reference in (select name from account_invoice
                        where mlg_type='tra_gop_xe' and state in ('open','paid') and chinhanh_id=%s and thu_cho_doituong_id=%s and date_invoice<='%s'
                           
        '''%(chinhanh_id[0],partner_id,period_to.date_stop)
        if not tat_toan:
            sql +='''
                and (ngay_tat_toan is null or (ngay_tat_toan is not null and '%s'<ngay_tat_toan)) and bien_so_xe_id=%s ))
                    and date<='%s'
            '''%(period_to.date_stop,bsx_id,period_to.date_stop)
        else:
            sql +='''
                and tat_toan=True and ngay_tat_toan<='%s' and bien_so_xe_id=%s ))
                    and date<='%s'
            '''%(period_to.date_stop,bsx_id,period_to.date_stop)
        self.cr.execute(sql)
        sdtlkcuoiky = self.cr.fetchone()[0]
        self.sdtlkcuoiky += sdtlkcuoiky
        return sdtlkcuoiky
            
    
    