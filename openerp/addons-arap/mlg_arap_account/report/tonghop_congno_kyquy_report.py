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
        self.tongcongnoconlai = 0
        self.tongcong_thu = 0
        self.tongcong_cantru = 0
        self.tongcong_chi = 0
        self.tongcong_conlai = 0
        self.tongcongdauky = 0
        self.tongcong_dauky = 0
        self.partner_ids = []
        self.chitiet_congno_dict = {}
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
            'get_soducuoi': self.get_soducuoi,
            'get_tongcong_thu': self.get_tongcong_thu,
            'get_tongcong_cantru': self.get_tongcong_cantru,
            'get_tongcong_chi': self.get_tongcong_chi,
            'get_tongcongnoconlai': self.get_tongcongnoconlai,
            'get_tongcong_conlai': self.get_tongcong_conlai,
            'get_tongcongdauky': self.get_tongcongdauky,
            'get_tongcong_dauky': self.get_tongcong_dauky,
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
        account = self.pool.get('account.account').browse(self.cr, 1, chinhanh_id[0])
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
            p_ids = []
            partner_obj = self.pool.get('res.partner')
            for partner in partner_obj.browse(self.cr, 1, partner_ids):
                if ldt=='taixe' and partner.taixe:
                    p_ids.append(partner.id)
                if ldt=='nhadautu' and partner.nhadautu:
                    p_ids.append(partner.id)
                if ldt=='nhanvienvanphong' and partner.nhanvienvanphong:
                    p_ids.append(partner.id)
            self.partner_ids = p_ids
            self.get_chitiet_congno_data()
            return p_ids
        else:
            period_from_id = wizard_data['period_from_id']
            period_to_id = wizard_data['period_to_id']
            period_from = self.pool.get('account.period').browse(self.cr, 1, period_from_id[0])
            period_to = self.pool.get('account.period').browse(self.cr, 1, period_to_id[0])
            chinhanh_id = wizard_data['chinhanh_id']
            sql = '''
                select foo.partner_id as partner_id from (
            
                    select partner_id from thu_ky_quy where ngay_thu <= '%s' and chinhanh_id=%s
                        and state in ('paid') and loai_doituong='%s'
                    union
                    select partner_id from tra_ky_quy where ngay_tra <= '%s' and chinhanh_id=%s
                        and state in ('paid') and loai_doituong='%s'
                )foo group by foo.partner_id
            '''%(period_to.date_stop,chinhanh_id[0],ldt,period_to.date_stop,chinhanh_id[0],ldt)
            self.cr.execute(sql)
            partner_ids = [r[0] for r in self.cr.fetchall()]
            if ldt=='taixe':
                sql = '''
                    select partner_id from account_move_line where date <= '%s'
                        and account_id in (select id from account_account where parent_id=%s)
                        and partner_id in (select id from res_partner where taixe=True)
                        and loai_giaodich='Giao dịch cấn trừ ký quỹ'
                        group by partner_id
                '''%(period_to.date_stop ,chinhanh_id[0])
            elif ldt=='nhadautu':
                sql = '''
                    select partner_id from account_move_line where date <= '%s'
                        and account_id in (select id from account_account where parent_id=%s)
                        and partner_id in (select id from res_partner where nhadautu=True)
                        and loai_giaodich='Giao dịch cấn trừ ký quỹ'
                        group by partner_id
                '''%(period_to.date_stop ,chinhanh_id[0])
            else:
                sql = '''
                    select partner_id from account_move_line where date <= '%s'
                        and account_id in (select id from account_account where parent_id=%s)
                        and partner_id in (select id from res_partner where nhanvienvanphong=True)
                        and loai_giaodich='Giao dịch cấn trừ ký quỹ'
                        group by partner_id
                '''%(period_to.date_stop ,chinhanh_id[0])
            self.cr.execute(sql)
            for partner_id in self.cr.fetchall():
                if partner_id[0] not in partner_ids:
                    partner_ids.append(partner_id[0])
            self.partner_ids = partner_ids
            self.get_chitiet_congno_data()
            return partner_ids

    def get_title_doituong(self, partner_id):
        if partner_id:
            partner = self.pool.get('res.partner').browse(self.cr, 1, partner_id)
            return {'name': partner.name or '','ma': partner.ma_doi_tuong or ''}
        return {'name': '','ma': ''}
    
    def get_bsx(self, partner_id):
        res = []
        wizard_data = self.localcontext['data']['form']
        if partner_id:
            period_from_id = wizard_data['period_from_id']
            period_to_id = wizard_data['period_to_id']
            period_from = self.pool.get('account.period').browse(self.cr, 1, period_from_id[0])
            period_to = self.pool.get('account.period').browse(self.cr, 1, period_to_id[0])
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
        period_from = self.pool.get('account.period').browse(self.cr, 1, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, 1, period_to_id[0])
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
        if self.chitiet_congno_dict.get(partner_id, False):
            return self.chitiet_congno_dict[partner_id]
        return []
    
    def get_chitiet_congno_data(self):
        if self.partner_ids:
            p_ids = self.partner_ids
            p_ids = str(p_ids).replace('[', '(')
            p_ids = str(p_ids).replace(']', ')')
            wizard_data = self.localcontext['data']['form']
            period_from_id = wizard_data['period_from_id']
            period_to_id = wizard_data['period_to_id']
            period_from = self.pool.get('account.period').browse(self.cr, 1, period_from_id[0])
            period_to = self.pool.get('account.period').browse(self.cr, 1, period_to_id[0])
            chinhanh_id = wizard_data['chinhanh_id']
            res = []
            dauky = 0
            thu = 0
            cantru = 0
            chi = 0
            
            sql = '''
            select partner_id,case when sum(sotien)!=0 then sum(sotien) else 0 end dauky from (
                select partner_id,case when sum(COALESCE(so_tien,0))!=0 then sum(COALESCE(so_tien,0)) else 0 end sotien
                    from thu_ky_quy where ngay_thu < '%s' and chinhanh_id=%s
                        and state in ('paid') and partner_id in %s
                    group by partner_id
                union
                
                select aml.partner_id as partner_id,case when sum(COALESCE(aml.credit,0))!=0 then -1*sum(COALESCE(aml.credit,0)) else 0 end sotien
                    from account_move_line aml
                    left join account_move am on am.id = aml.move_id
                    
                    where aml.date < '%s'
                        and aml.account_id in (select id from account_account where parent_id=%s)
                        and aml.partner_id in %s and aml.credit is not null and aml.credit>0
                        and aml.loai_giaodich='Giao dịch cấn trừ ký quỹ'
                    group by aml.partner_id
                union
                
                select partner_id,case when sum(COALESCE(so_tien,0))!=0 then -1*sum(COALESCE(so_tien,0)) else 0 end sotien
                    from tra_ky_quy where ngay_tra < '%s' and chinhanh_id=%s
                        and state in ('paid') and partner_id in %s 
                    group by partner_id
                )foo group by partner_id
            '''%(period_from.date_start,chinhanh_id[0],p_ids,period_from.date_start,chinhanh_id[0],p_ids,period_from.date_start,chinhanh_id[0],p_ids)
            self.cr.execute(sql)
            for line in self.cr.dictfetchall():
                dauky += line['dauky']
                self.tongcongdauky += line['dauky']
                if self.chitiet_congno_dict.get(line['partner_id'], False):
                    self.chitiet_congno_dict[line['partner_id']][0]['dauky'] += line['dauky']
                    self.chitiet_congno_dict[line['partner_id']][0]['conlai'] += line['dauky']
                else:
                    self.chitiet_congno_dict[line['partner_id']] = [{'dauky': line['dauky'],'thu': 0,'cantru': 0,'chi': 0, 'conlai': line['dauky']}]
                    
            sql = '''
                select partner_id,case when sum(so_tien)!=0 then sum(so_tien) else 0 end so_tien from thu_ky_quy where ngay_thu between '%s' and '%s' and chinhanh_id=%s
                        and state in ('paid') and partner_id in %s
                    group by partner_id 
            '''%(period_from.date_start,period_to.date_stop,chinhanh_id[0],p_ids)
            self.cr.execute(sql)
            for line in self.cr.dictfetchall():
                thu += line['so_tien']
                self.tongcongnothu += line['so_tien']
                if self.chitiet_congno_dict.get(line['partner_id'], False):
                    self.chitiet_congno_dict[line['partner_id']][0]['thu'] += line['so_tien']
                    self.chitiet_congno_dict[line['partner_id']][0]['conlai'] += line['so_tien']
                else:
                    self.chitiet_congno_dict[line['partner_id']] = [{'dauky': 0,'thu': line['so_tien'],'cantru': 0,'chi': 0, 'conlai': line['so_tien']}]
                    
            sql = '''
                select aml.partner_id as partner_id,case when sum(aml.credit)!=0 then sum(aml.credit) else 0 end credit
                    from account_move_line aml
                    left join account_move am on am.id = aml.move_id
                    
                    where aml.date between '%s' and '%s'
                        and aml.account_id in (select id from account_account where parent_id=%s)
                        and aml.partner_id in %s and aml.credit is not null and aml.credit>0
                        and aml.loai_giaodich='Giao dịch cấn trừ ký quỹ'
                    group by aml.partner_id
            '''%(period_from.date_start,period_to.date_stop,chinhanh_id[0],p_ids)
            self.cr.execute(sql)
            for line in self.cr.dictfetchall():
                cantru += line['credit']
                self.tongcongnocantru += line['credit']
                if self.chitiet_congno_dict.get(line['partner_id'], False):
                    self.chitiet_congno_dict[line['partner_id']][0]['cantru'] += line['credit']
                    self.chitiet_congno_dict[line['partner_id']][0]['conlai'] += -line['credit']
                else:
                    self.chitiet_congno_dict[line['partner_id']] = [{'dauky': 0,'thu': 0,'cantru': line['credit'],'chi': 0, 'conlai': -line['so_tien']}]
                    
            sql = '''
                select partner_id,case when sum(so_tien)!=0 then sum(so_tien) else 0 end so_tien from tra_ky_quy where ngay_tra between '%s' and '%s' and chinhanh_id=%s
                        and state in ('paid') and partner_id in %s
                    group by partner_id 
            '''%(period_from.date_start,period_to.date_stop,chinhanh_id[0],p_ids)
            self.cr.execute(sql)
            for line in self.cr.dictfetchall():
                chi += line['so_tien']
                self.tongcongnochi += line['so_tien']
                if self.chitiet_congno_dict.get(line['partner_id'], False):
                    self.chitiet_congno_dict[line['partner_id']][0]['chi'] += line['so_tien']
                    self.chitiet_congno_dict[line['partner_id']][0]['conlai'] += -line['so_tien']
                else:
                    self.chitiet_congno_dict[line['partner_id']] = [{'dauky': 0,'thu': 0,'cantru': 0,'chi': line['so_tien'], 'conlai': -line['so_tien']}]
                    
            conlai = dauky + thu - cantru - chi
            self.tongcongnoconlai += conlai
#             res = [{'dauky': dauky,'thu': thu,'cantru': cantru,'chi': chi, 'conlai': conlai}]
        return True
    
    def get_tongcongdauky(self):
        tongcongdauky = self.tongcongdauky
        self.tongcong_dauky += tongcongdauky
        self.tongcongdauky = 0
        return tongcongdauky
    
    def get_tongcongnothu(self):
        tongcongnothu = self.tongcongnothu
        self.tongcong_thu += tongcongnothu
        self.tongcongnothu = 0
        return tongcongnothu
    
    def get_tongcongnocantru(self):
        tongcongnocantru = self.tongcongnocantru
        self.tongcong_cantru += tongcongnocantru
        self.tongcongnocantru = 0
        return tongcongnocantru
    
    def get_tongcongnochi(self):
        tongcongnochi = self.tongcongnochi
        self.tongcong_chi += tongcongnochi
        self.tongcongnochi = 0
        return tongcongnochi
    
    def get_tongcongnoconlai(self):
        tongcongnoconlai = self.tongcongnoconlai
        self.tongcong_conlai += tongcongnoconlai
        self.tongcongnoconlai = 0
        return tongcongnoconlai
    
    def get_tongcong_dauky(self):
        tongcong_dauky = self.tongcong_dauky
        self.tongcong_dauky = 0
        return tongcong_dauky
    
    def get_tongcong_thu(self):
        tongcong_thu = self.tongcong_thu
        self.tongcong_thu = 0
        return tongcong_thu
    
    def get_tongcong_cantru(self):
        tongcong_cantru = self.tongcong_cantru
        self.tongcong_cantru = 0
        return tongcong_cantru
    
    def get_tongcong_chi(self):
        tongcong_chi = self.tongcong_chi
        self.tongcong_chi = 0
        return tongcong_chi
    
    def get_tongcong_conlai(self):
        tongcong_conlai = self.tongcong_conlai
        self.tongcong_conlai = 0
        return tongcong_conlai
    
    def get_soducuoi(self):
        return 0
        
        
    