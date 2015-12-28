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
        self.tongcongnothu = 0
        self.tongcongnocantru = 0
        self.tongcongnochi = 0
        self.localcontext.update({
            'get_doituong': self.get_doituong,
            'convert_date': self.convert_date,
            'get_title_doituong': self.get_title_doituong,
            'convert_amount': self.convert_amount,
            'get_chitiet_congno': self.get_chitiet_congno,
            'get_tongcongnothu': self.get_tongcongnothu,
            'get_tongcongnocantru': self.get_tongcongnocantru,
            'get_tongcongnochi': self.get_tongcongnochi,
            'get_chinhanh': self.get_chinhanh,
            'get_from_thang': self.get_from_thang,
            'get_to_thang': self.get_to_thang,
            'get_loaidoituong': self.get_loaidoituong,
            'get_name_loaidoituong': self.get_name_loaidoituong,
            'get_chitiet_congno_ndt': self.get_chitiet_congno_ndt,
            'get_bsx': self.get_bsx,
        })
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        return ''
    
    def get_from_thang(self):
        wizard_data = self.localcontext['data']['form']
        period_id = wizard_data['period_from_id']
        return period_id and period_id[1] or ''
    
    def get_to_thang(self):
        wizard_data = self.localcontext['data']['form']
        period_id = wizard_data['period_to_id']
        return period_id and period_id[1] or ''
    
    def convert_amount(self, amount):
        a = format(int(amount),',')
        return a
    
    def get_chinhanh(self):
        wizard_data = self.localcontext['data']['form']
        chinhanh_id = wizard_data['chinhanh_id']
        if not chinhanh_id:
            return {'name':'','code':''}
        account = self.pool.get('account.account').browse(self.cr, self.uid, chinhanh_id[0])
        return {'name':account.name,'code':account.code}
    
    def get_loaidoituong(self):
        wizard_data = self.localcontext['data']['form']
        loai_doituong = wizard_data['loai_doituong']
        if loai_doituong:
            return [loai_doituong]
        else:
            return ['taixe','nhadautu','nhanvienvanphong']
        
    def get_name_loaidoituong(self, ldt):
        if ldt=='taixe':
            return 'Lái xe'
        if ldt=='nhadautu':
            return 'Nhà đầu tư'
        if ldt=='nhanvienvanphong':
            return 'Nhân viên văn phòng'
    
    def get_doituong(self, ldt):
        wizard_data = self.localcontext['data']['form']
        partner_ids = wizard_data['partner_ids']
        if partner_ids:
            return partner_ids
        else:
            period_from_id = wizard_data['period_from_id']
            period_to_id = wizard_data['period_to_id']
            period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
            period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
            chinhanh_id = wizard_data['chinhanh_id']
            sql = '''
                select foo.partner_id as partner_id from (
            
                    select partner_id from thu_ky_quy where ngay_thu between '%s' and '%s' and chinhanh_id=%s
                        and state in ('paid') and loai_doituong='%s'
                    union
                    select partner_id from tra_ky_quy where ngay_tra between '%s' and '%s' and chinhanh_id=%s
                        and state in ('paid') and loai_doituong='%s'
                )foo group by foo.partner_id
            '''%(period_from.date_start,period_to.date_stop,chinhanh_id[0],ldt,period_from.date_start,period_to.date_stop,chinhanh_id[0],ldt)
            self.cr.execute(sql)
            partner_ids = [r[0] for r in self.cr.fetchall()]
            if ldt=='taixe':
                sql = '''
                    select partner_id from account_move_line where date between '%s' and '%s'
                        and account_id in (select id from account_account where parent_id=%s)
                        and partner_id in (select id from res_partner where taixe=True)
                        and loai_giaodich='Giao dịch cấn trừ ký quỹ'
                        group by partner_id
                '''%(period_from.date_start,period_to.date_stop ,chinhanh_id[0])
            elif ldt=='nhadautu':
                sql = '''
                    select partner_id from account_move_line where date between '%s' and '%s'
                        and account_id in (select id from account_account where parent_id=%s)
                        and partner_id in (select id from res_partner where nhadautu=True)
                        and loai_giaodich='Giao dịch cấn trừ ký quỹ'
                        group by partner_id
                '''%(period_from.date_start,period_to.date_stop ,chinhanh_id[0])
            else:
                sql = '''
                    select partner_id from account_move_line where date between '%s' and '%s'
                        and account_id in (select id from account_account where parent_id=%s)
                        and partner_id in (select id from res_partner where nhanvienvanphong=True)
                        and loai_giaodich='Giao dịch cấn trừ ký quỹ'
                        group by partner_id
                '''%(period_from.date_start,period_to.date_stop ,chinhanh_id[0])
            self.cr.execute(sql)
            for partner_id in self.cr.fetchall():
                if partner_id[0] not in partner_ids:
                    partner_ids.append(partner_id[0])
            return partner_ids

    def get_title_doituong(self, partner_id):
        if partner_id:
            partner = self.pool.get('res.partner').browse(self.cr, self.uid, partner_id)
            return (partner.ma_doi_tuong or '')+'_'+(partner.name or '')
        return ''
    
    def get_bsx(self, partner_id):
        res = []
        wizard_data = self.localcontext['data']['form']
        if partner_id:
            period_from_id = wizard_data['period_from_id']
            period_to_id = wizard_data['period_to_id']
            period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
            period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
            chinhanh_id = wizard_data['chinhanh_id']
            sql = '''
                select id, name from bien_so_xe where id in (
                    select foo.bien_so_xe_id as bien_so_xe_id from (
                
                        select bien_so_xe_id from thu_ky_quy where ngay_thu between '%s' and '%s' and chinhanh_id=%s
                            and state in ('paid') and partner_id=%s
                        union
                        select bien_so_xe_id from tra_ky_quy where ngay_tra between '%s' and '%s' and chinhanh_id=%s
                            and state in ('paid') and partner_id=%s
                        union
                        select bien_so_xe_id from account_move_line where date between '%s' and '%s'
                            and account_id in (select id from account_account where parent_id=%s)
                            and partner_id=%s
                            and loai_giaodich='Giao dịch cấn trừ ký quỹ'
                    )foo group by foo.bien_so_xe_id
                )
            '''%(period_from.date_start,period_to.date_stop,chinhanh_id[0],partner_id,period_from.date_start,period_to.date_stop,chinhanh_id[0],partner_id,period_from.date_start,period_to.date_stop ,chinhanh_id[0],partner_id)
            
            self.cr.execute(sql)
            return self.cr.dictfetchall()
        return res
    
    def get_chitiet_congno_ndt(self, partner_id, bsx_id):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        res = []
        sql = '''
            select ngay_thu,name,so_tien from thu_ky_quy where ngay_thu between '%s' and '%s' and chinhanh_id=%s
                    and state in ('paid') and partner_id=%s and bien_so_xe_id=%s 
        '''%(period_from.date_start,period_to.date_stop,chinhanh_id[0],partner_id,bsx_id)
        self.cr.execute(sql)
        for line in self.cr.dictfetchall():
            res.append({
                'ngay': line['ngay_thu'],
                'maphieu': line['name'],
                'diengiai': '',
                'thu': line['so_tien'],
                'cantru': 0,
                'chi': 0,
            })
            self.tongcongnothu += line['so_tien']
        sql = '''
            select aml.date as date,aml.loai_giaodich as loai_giaodich,aml.credit as credit, am.ref as ref
                from account_move_line aml
                left join account_move am on am.id = aml.move_id
                
                where aml.date between '%s' and '%s'
                    and aml.account_id in (select id from account_account where parent_id=%s)
                    and aml.partner_id=%s and aml.credit is not null and aml.credit>0
                    and aml.loai_giaodich='Giao dịch cấn trừ ký quỹ' and aml.bien_so_xe_id=%s 
        '''%(period_from.date_start,period_to.date_stop,chinhanh_id[0],partner_id,bsx_id)
        self.cr.execute(sql)
        for line in self.cr.dictfetchall():
            res.append({
                'ngay': line['date'],
                'maphieu': line['ref'],
                'diengiai': line['loai_giaodich'],
                'thu': 0,
                'cantru': line['credit'],
                'chi': 0,
            })
            self.tongcongnocantru = line['credit']
        sql = '''
            select ngay_tra,name,so_tien from tra_ky_quy where ngay_tra between '%s' and '%s' and chinhanh_id=%s
                    and state in ('paid') and partner_id=%s and bien_so_xe_id=%s  
        '''%(period_from.date_start,period_to.date_stop,chinhanh_id[0],partner_id,bsx_id)
        self.cr.execute(sql)
        for line in self.cr.dictfetchall():
            res.append({
                'ngay': line['ngay_tra'],
                'maphieu': line['name'],
                'diengiai': '',
                'thu': 0,
                'cantru': 0,
                'chi': line['so_tien'],
            })
            self.tongcongnochi = line['so_tien']
        res = sorted(res,key=lambda t: t['ngay'])
        return res
    
    def get_chitiet_congno(self, partner_id):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        res = []
        sql = '''
            select ngay_thu,name,so_tien from thu_ky_quy where ngay_thu between '%s' and '%s' and chinhanh_id=%s
                    and state in ('paid') and partner_id=%s 
        '''%(period_from.date_start,period_to.date_stop,chinhanh_id[0],partner_id)
        self.cr.execute(sql)
        for line in self.cr.dictfetchall():
            res.append({
                'ngay': line['ngay_thu'],
                'maphieu': line['name'],
                'diengiai': '',
                'thu': line['so_tien'],
                'cantru': 0,
                'chi': 0,
            })
            self.tongcongnothu += line['so_tien']
        sql = '''
            select aml.date as date,aml.loai_giaodich as loai_giaodich,aml.credit as credit, am.ref as ref
                from account_move_line aml
                left join account_move am on am.id = aml.move_id
                
                where aml.date between '%s' and '%s'
                    and aml.account_id in (select id from account_account where parent_id=%s)
                    and aml.partner_id=%s and aml.credit is not null and aml.credit>0
                    and aml.loai_giaodich='Giao dịch cấn trừ ký quỹ'
        '''%(period_from.date_start,period_to.date_stop,chinhanh_id[0],partner_id)
        self.cr.execute(sql)
        for line in self.cr.dictfetchall():
            res.append({
                'ngay': line['date'],
                'maphieu': line['ref'],
                'diengiai': line['loai_giaodich'],
                'thu': 0,
                'cantru': line['credit'],
                'chi': 0,
            })
            self.tongcongnocantru += line['credit']
        sql = '''
            select ngay_tra,name,so_tien from tra_ky_quy where ngay_tra between '%s' and '%s' and chinhanh_id=%s
                    and state in ('paid') and partner_id=%s 
        '''%(period_from.date_start,period_to.date_stop,chinhanh_id[0],partner_id)
        self.cr.execute(sql)
        for line in self.cr.dictfetchall():
            res.append({
                'ngay': line['ngay_tra'],
                'maphieu': line['name'],
                'diengiai': '',
                'thu': 0,
                'cantru': 0,
                'chi': line['so_tien'],
            })
            self.tongcongnochi += line['so_tien']
        res = sorted(res,key=lambda t: t['ngay'])
        return res
    
    def get_tongcongnothu(self):
        tongcongnothu = self.tongcongnothu
        self.tongcongnothu = 0
        return tongcongnothu
    
    def get_tongcongnocantru(self):
        tongcongnocantru = self.tongcongnocantru
        self.tongcongnocantru = 0
        return tongcongnocantru
    
    def get_tongcongnochi(self):
        tongcongnochi = self.tongcongnochi
        self.tongcongnochi = 0
        return tongcongnochi
        
        
    