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
        
        self.partner_ids = []
        self.bsx_dict = {}
        
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
            'get_only_payment': self.get_only_payment,
            
            'get_khoitao': self.get_khoitao,
        })
        
    def get_khoitao(self):
        self.get_doituong_data()
        self.get_bsx_data()
        return True
        
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
        account = self.pool.get('account.account').browse(self.cr, 1, chinhanh_id[0])
        return {'name':account.name,'code':account.code}
    
    def get_title_doituong(self, partner_id):
        if partner_id:
            partner = self.pool.get('res.partner').browse(self.cr, 1, partner_id)
            return (partner.ma_doi_tuong or '')+'_'+(partner.name or '')
        return ''
    
    def get_doituong(self):
        return self.partner_ids
    
    def get_doituong_data(self):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, 1, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, 1, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        sql = '''
            select thu_cho_doituong_id from account_invoice where date_invoice between '%s' and '%s' and chinhanh_id=%s
                and state in ('open','paid') and mlg_type='tra_gop_xe' and thu_cho_doituong_id is not null  
        '''%(period_from.date_start,period_to.date_stop,chinhanh_id[0])
        pa_ids = wizard_data['partner_ids']
        if pa_ids:
            pa_ids = str(pa_ids).replace('[', '(')
            pa_ids = str(pa_ids).replace(']', ')')
            sql+='''
                and thu_cho_doituong_id in %s 
            '''%(pa_ids)
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
        sql = '''
            select ai.thu_cho_doituong_id as thu_cho_doituong_id
                from account_move_line aml
                left join account_voucher av on aml.move_id=av.move_id
                left join account_invoice ai on ai.name=av.reference
                
                where ai.date_invoice < '%s' and ai.chinhanh_id=%s
                    and ai.state in ('open','paid') and ai.mlg_type='tra_gop_xe' and ai.thu_cho_doituong_id is not null
                    and aml.date between '%s' and '%s'  
        '''%(period_from.date_start,chinhanh_id[0],period_from.date_start,period_to.date_stop)
        if pa_ids:
            pa_ids = str(pa_ids).replace('[', '(')
            pa_ids = str(pa_ids).replace(']', ')')
            sql+='''
                and ai.thu_cho_doituong_id in %s 
            '''%(pa_ids)
        bien_so_xe_ids = wizard_data['bien_so_xe_ids']
        if bien_so_xe_ids:
            bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
            bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
            sql+='''
                and ai.bien_so_xe_id in %s 
            '''%(bien_so_xe_ids)
        self.cr.execute(sql)
        for partner in self.cr.fetchall():
            if partner[0] not in partner_ids:
                partner_ids.append(partner[0])
        self.partner_ids = partner_ids
        return True
    
    def get_bsx(self, partner_id):
        if self.bsx_dict.get(partner_id, False):
            return self.bsx_dict[partner_id]
        return []
    
    def get_bsx_data(self):
        res = []
        wizard_data = self.localcontext['data']['form']
        if self.partner_ids:
            p_ids = self.partner_ids
            p_ids = str(p_ids).replace('[', '(')
            p_ids = str(p_ids).replace(']', ')')
            period_from_id = wizard_data['period_from_id']
            period_to_id = wizard_data['period_to_id']
            period_from = self.pool.get('account.period').browse(self.cr, 1, period_from_id[0])
            period_to = self.pool.get('account.period').browse(self.cr, 1, period_to_id[0])
            chinhanh_id = wizard_data['chinhanh_id']
            bien_so_xe_ids = wizard_data['bien_so_xe_ids']
            sql = '''
            select partner_id, id, name from (
                select ai.thu_cho_doituong_id as partner_id, bsx.id as id, bsx.name as name 
                    
                    from bien_so_xe bsx
                    left join account_invoice ai on bsx.id = ai.bien_so_xe_id 
                    where ai.mlg_type='tra_gop_xe' and ai.thu_cho_doituong_id in %s and ai.state in ('open','paid')
                            and ai.chinhanh_id=%s and ai.date_invoice between '%s' and '%s' 
                    
            '''%(p_ids,chinhanh_id[0],period_from.date_start,period_to.date_stop)
            if bien_so_xe_ids:
                bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
                bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
                sql+='''
                    and bsx.id in %s 
                '''%(bien_so_xe_ids)
            sql += '''
                    group by ai.thu_cho_doituong_id, bsx.id, bsx.name 
                union 
                select ai.thu_cho_doituong_id as partner_id, bsx.id as id, bsx.name as name 
                    from account_move_line aml
                    left join account_voucher av on aml.move_id=av.move_id
                    left join account_invoice ai on ai.name=av.reference
                    left join bien_so_xe bsx on bsx.id=ai.bien_so_xe_id
                    
                    where ai.date_invoice < '%s' and ai.chinhanh_id=%s
                        and ai.state in ('open','paid') and ai.mlg_type='tra_gop_xe' and ai.thu_cho_doituong_id in %s
                        and aml.date between '%s' and '%s'  
            '''%(period_from.date_start,chinhanh_id[0],p_ids,period_from.date_start,period_to.date_stop)
            if bien_so_xe_ids:
                bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
                bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
                sql+='''
                    and bsx.id in %s 
                '''%(bien_so_xe_ids)
            sql += ''' group by ai.thu_cho_doituong_id, bsx.id, bsx.name
                )foo group by partner_id, id, name '''
            
            self.cr.execute(sql)
            for bsx in self.cr.dictfetchall():
                if self.bsx_dict.get(bsx['partner_id'], False):
                    self.bsx_dict[bsx['partner_id']].append({'id': bsx['id'], 'name': bsx['name']})
                else:
                    self.bsx_dict[bsx['partner_id']] = [{'id': bsx['id'], 'name': bsx['name']}]
        return True
    
    def get_phaithu(self, partner_id, bsx_id):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, 1, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, 1, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        sql = '''
            select case when sum(sotien)!=0 then sum(sotien) else 0 end sotien from (
            select case when sum(so_tien)!=0 then sum(so_tien) else 0 end sotien
                from account_invoice
                where thu_cho_doituong_id=%s and state in ('open','paid') and date_invoice between '%s' and '%s' and chinhanh_id=%s
                    and mlg_type='tra_gop_xe' and bien_so_xe_id=%s
            union all
            select case when sum(aml.credit)!=0 then -1*sum(aml.credit) else 0 end sotien
                    from account_move_line aml
                    left join account_voucher av on aml.move_id=av.move_id
                    left join account_invoice ai on ai.name=av.reference
                    
                    where ai.date_invoice between '%s' and '%s' and ai.chinhanh_id=%s
                        and ai.state in ('open','paid') and ai.mlg_type='tra_gop_xe' and ai.thu_cho_doituong_id = %s
                        and aml.date between '%s' and '%s' and ai.bien_so_xe_id=%s  
            )foo
        '''%(partner_id,period_from.date_start,period_to.date_stop,chinhanh_id[0],bsx_id, period_from.date_start,period_to.date_stop,chinhanh_id[0],partner_id,period_from.date_start,period_to.date_stop,bsx_id)
        self.cr.execute(sql)
        phaithu = self.cr.fetchone()[0]
        self.phaithu += phaithu
        return phaithu
    
    def get_dathu(self, partner_id, bsx_id):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, 1, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, 1, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        sql = '''
            select case when sum(aml.credit)!=0 then sum(aml.credit) else 0 end sotien
                from account_move_line aml
                left join account_voucher av on aml.move_id=av.move_id
                left join account_invoice ai on ai.name=av.reference
                
                where ai.date_invoice <= '%s' and ai.chinhanh_id=%s
                    and ai.state in ('open','paid') and ai.mlg_type='tra_gop_xe' and ai.thu_cho_doituong_id = %s
                    and aml.date between '%s' and '%s' and ai.bien_so_xe_id=%s 
        '''%(period_to.date_stop,chinhanh_id[0],partner_id,period_from.date_start,period_to.date_stop,bsx_id)
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
        period_from = self.pool.get('account.period').browse(self.cr, 1, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, 1, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        sql = '''
            select ai.id as invoice_id,ai.date_invoice as ngay,ai.name as maphieudexuat,rp.ma_doi_tuong as madoituong,rp.name as tendoituong,
                (COALESCE(ai.so_tien,0)) as no, ai.fusion_id as fusion_id,ai.loai_giaodich,ai.dien_giai as dien_giai
            
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
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, 1, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, 1, period_to_id[0])
        invoice = self.pool.get('account.invoice').browse(self.cr, 1, invoice_id)
        pays = []
        for pay in invoice.payment_ids:
            if pay.date >= period_from.date_start and pay.date<=period_to.date_stop:
                pays.append(pay)
        return pays
    
    def get_only_payment(self, partner_id, bsx_id):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, 1, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, 1, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        sql = '''
            select date,fusion_id,credit,ref,loai_giaodich,note_giaodich,id
                from account_move_line
                where credit!=0 and move_id in (select move_id from account_voucher
                    where reference in (select name from account_invoice
                        where date_invoice<'%s' and mlg_type='tra_gop_xe' and state in ('open','paid') and chinhanh_id=%s and thu_cho_doituong_id=%s and bien_so_xe_id=%s 
        '''%(period_from.date_start,chinhanh_id[0],partner_id,bsx_id)
        sql += ''' ))
                and date between '%s' and '%s' '''%(period_from.date_start,period_to.date_stop)
        self.cr.execute(sql)
        onlypay = self.cr.dictfetchall()
        return onlypay
    