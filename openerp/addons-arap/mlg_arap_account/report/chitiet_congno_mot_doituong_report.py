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
        self.tongcongno = 0
        self.tongno = 0
        self.tongco = 0
        self.congno = 0
        self.congco = 0
        self.nocuoiky = 0
        self.localcontext.update({
            'get_doituong': self.get_doituong,
            'convert_date': self.convert_date,
            'get_title_congno': self.get_title_congno,
            'get_nodauky': self.get_nodauky,
            'convert_amount': self.convert_amount,
            'get_chitiet_congno': self.get_chitiet_congno,
            'get_nocuoiky': self.get_nocuoiky,
            'get_tongcongno': self.get_tongcongno,
            'get_from_thang': self.get_from_thang,
            'get_to_thang': self.get_to_thang,
            'get_payment': self.get_payment,
            'get_chinhanh': self.get_chinhanh,
            'get_congno': self.get_congno,
            'get_lichsu_thutienlai': self.get_lichsu_thutienlai,
            'get_tongno': self.get_tongno,
            'get_tongco': self.get_tongco,
            'get_cong_no': self.get_cong_no,
            'get_congco': self.get_congco,
            'get_loai_congno_tuongung': self.get_loai_congno_tuongung,
            'get_title_lcntu': self.get_title_lcntu,
            'get_only_payment': self.get_only_payment,
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
        partner_id = wizard_data['partner_id']
        partner = self.pool.get('res.partner').browse(self.cr, self.uid, partner_id[0])
        return {'madoituong': partner.ma_doi_tuong,'tendoituong':partner.name}
    
    def get_congno(self):
        wizard_data = self.localcontext['data']['form']
        loai_congno_ids = wizard_data['loai_congno_ids']
        loai_congno_obj = self.pool.get('loai.cong.no')
        if not loai_congno_ids:
            loai_congno_ids = loai_congno_obj.search(self.cr, self.uid, [])
        return loai_congno_obj.browse(self.cr, self.uid, loai_congno_ids)
    
    def get_loai_congno_tuongung(self, mlg_type):
        wizard_data = self.localcontext['data']['form']
        chinhanh_id = wizard_data['chinhanh_id']
        lcntu_ids = []
        if mlg_type=='no_doanh_thu':
            loai = 'loai_nodoanhthu'
            loai_nodoanhthu_id = wizard_data['loai_nodoanhthu_id']
            if loai_nodoanhthu_id:
                lcntu_ids.append({
                    'id':loai_nodoanhthu_id[0],
                    'name':loai_nodoanhthu_id[1],
                    'loai':loai
                })
            else:
                sql = '''
                    select id,name from loai_no_doanh_thu
                '''
                self.cr.execute(sql)
                for lndt in self.cr.fetchall():
                    lcntu_ids.append({
                        'id':lndt[0],
                        'name':lndt[1],
                        'loai':loai
                    })
        elif mlg_type=='phai_thu_bao_hiem':
            loai = 'loai_baohiem'
            loai_baohiem_id = wizard_data['loai_baohiem_id']
            if loai_baohiem_id:
                lcntu_ids.append({
                    'id':loai_baohiem_id[0],
                    'name':loai_baohiem_id[1],
                    'loai':loai
                })
            else:
                sql = '''
                    select id,name from loai_bao_hiem
                '''
                self.cr.execute(sql)
                for lndt in self.cr.fetchall():
                    lcntu_ids.append({
                        'id':lndt[0],
                        'name':lndt[1],
                        'loai':loai
                    })
        elif mlg_type=='phat_vi_pham':
            loai = 'loai_vipham'
            loai_vipham_id = wizard_data['loai_vipham_id']
            if loai_vipham_id:
                lcntu_ids.append({
                    'id':loai_vipham_id[0],
                    'name':loai_vipham_id[1],
                    'loai':loai
                })
            else:
                sql = '''
                    select id,name from loai_vi_pham
                '''
                self.cr.execute(sql)
                for lndt in self.cr.fetchall():
                    lcntu_ids.append({
                        'id':lndt[0],
                        'name':lndt[1],
                        'loai':loai
                    })
        elif mlg_type=='thu_no_xuong':
            loai = 'maxuong'
            ma_xuong_id = wizard_data['ma_xuong_id']
            if ma_xuong_id:
                lcntu_ids.append({
                    'id':ma_xuong_id[0],
                    'name':ma_xuong_id[1],
                    'loai':loai
                })
            else:
                sql = '''
                    select id,name from ma_xuong where chinhanh_id=%s
                '''%(chinhanh_id[0])
                self.cr.execute(sql)
                for lndt in self.cr.fetchall():
                    lcntu_ids.append({
                        'id':lndt[0],
                        'name':lndt[1],
                        'loai':loai
                    })
        elif mlg_type=='hoan_tam_ung':
            loai = 'loai_tamung'
            loai_tamung_id = wizard_data['loai_tamung_id']
            if loai_tamung_id:
                lcntu_ids.append({
                    'id':loai_tamung_id[0],
                    'name':loai_tamung_id[1],
                    'loai':loai
                })
            else:
                sql = '''
                    select id,name from loai_tam_ung
                '''
                self.cr.execute(sql)
                for lndt in self.cr.fetchall():
                    lcntu_ids.append({
                        'id':lndt[0],
                        'name':lndt[1],
                        'loai':loai
                    })
        else:
            lcntu_ids.append({
                'id':False,
                'name':'',
                'loai': 'loai_conlai'
            })
        return lcntu_ids
        
    def get_title_lcntu(self, lcntu):
        tt = ''
        if lcntu['loai']=='loai_nodoanhthu':
            tt = 'Loại nợ DT-BH-AL: '+lcntu['name']
        if lcntu['loai']=='loai_baohiem':
            tt = 'Loại bảo hiểm: '+lcntu['name']
        if lcntu['loai']=='loai_vipham':
            tt = 'Loại vi phạm: '+lcntu['name']
        if lcntu['loai']=='maxuong':
            tt = 'Mã xưởng: '+lcntu['name']
        if lcntu['loai']=='loai_tamung':
            tt = 'Loại tạm ứng: '+lcntu['name']
        return tt
    
    def get_title_congno(self, congno):
        tt = ''
        if congno=='Nợ doanh thu':
            tt='no_doanh_thu'
        if congno=='Phải thu chi hộ điện thoại':
            tt='chi_ho_dien_thoai'
        if congno=='Phải thu bảo hiểm':
            tt='phai_thu_bao_hiem'
        if congno=='Phạt vi phạm':
            tt='phat_vi_pham'
        if congno=='Thu nợ xưởng':
            tt='thu_no_xuong'
        if congno=='Thu phí thương hiệu':
            tt='thu_phi_thuong_hieu'
        if congno=='Trả góp xe':
            tt='tra_gop_xe'
        if congno=='Phải thu tạm ứng':
            tt='hoan_tam_ung'
        if congno=='Phải trả ký quỹ':
            tt='phai_tra_ky_quy'
        if congno=='Phải trả chi hộ':
            tt='chi_ho'
        return tt
    
    def get_nodauky(self, mlg_type, lcntu):
        wizard_data = self.localcontext['data']['form']
        if mlg_type:
            period_id = wizard_data['period_from_id']
            chinhanh_id = wizard_data['chinhanh_id']
            partner_id = wizard_data['partner_id']
#             mlg_type = self.get_title_congno(congno)
            sql = '''
                select case when sum(so_tien_no)!=0 then sum(so_tien_no) else 0 end nodauky
                    from congno_dauky_line where mlg_type='%s' and chinhanh_id=%s
                        and congno_dauky_id in (select id from congno_dauky where partner_id=%s and period_id=%s)
            '''%(mlg_type,chinhanh_id[0],partner_id[0],period_id[0])
            if lcntu and lcntu['loai']!='loai_conlai' and lcntu['id']:
                sql = '''
                    select case when sum(so_tien_no)!=0 then sum(so_tien_no) else 0 end nodauky
                        from chitiet_congno_dauky_line where congno_dauky_line_id in (select id from congno_dauky_line where mlg_type='%s' and chinhanh_id=%s
                            and congno_dauky_id in (select id from congno_dauky where partner_id=%s and period_id=%s)) and loai_id=%s
                '''%(mlg_type,chinhanh_id[0],partner_id[0],period_id[0],lcntu['id'])
            self.cr.execute(sql)
            nodauky = self.cr.fetchone()[0]
            self.nocuoiky += nodauky
            return nodauky
        return 0
    
    def get_tongcongno(self):
        tongcongno = self.tongcongno
        self.tongcongno = 0
        return tongcongno
    
    def get_tongno(self):
        tongno = self.tongno
        self.tongno = 0
        return tongno
    
    def get_tongco(self):
        tongco = self.tongco
        self.tongco = 0
        return tongco
    
    def get_cong_no(self):
        congno = self.congno
        self.congno = 0
        return congno
    
    def get_congco(self):
        congco = self.congco
        self.congco = 0
        return congco
    
    def get_nocuoiky(self, partner_id,lcntu):
        nocuoiky = self.nocuoiky
        self.nocuoiky = 0
        self.tongcongno += nocuoiky
        return nocuoiky
    
#     def get_nocuoiky(self, mlg_type,lcntu):
#         wizard_data = self.localcontext['data']['form']
#         if mlg_type:
#             period_from_id = wizard_data['period_from_id']
#             period_to_id = wizard_data['period_to_id']
#             period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
#             period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
#             chinhanh_id = wizard_data['chinhanh_id']
#             partner_id = wizard_data['partner_id']
# #             mlg_type = self.get_title_congno(congno)
#             sql = '''
#                 select case when sum(COALESCE(residual,0)+COALESCE(sotien_lai_conlai,0))!=0 then sum(COALESCE(residual,0)+COALESCE(sotien_lai_conlai,0)) else 0 end notrongky
#                     from account_invoice where mlg_type='%s' and chinhanh_id=%s and partner_id=%s
#                         and date_invoice between '%s' and '%s' and state in ('open','paid') 
#             '''%(mlg_type,chinhanh_id[0],partner_id[0],period_from.date_start,period_to.date_stop)
#             if lcntu['loai']=='loai_nodoanhthu' and lcntu['id']:
#                 sql+='''
#                     and loai_nodoanhthu_id = %s 
#                 '''%(lcntu['id'])
#             if lcntu['loai']=='loai_baohiem' and lcntu['id']:
#                 sql+='''
#                     and loai_baohiem_id = %s 
#                 '''%(lcntu['id'])
#             if lcntu['loai']=='loai_vipham' and lcntu['id']:
#                 sql+='''
#                     and loai_vipham_id = %s 
#                 '''%(lcntu['id'])
#             if lcntu['loai']=='maxuong' and lcntu['id']:
#                 sql+='''
#                     and ma_xuong_id = %s 
#                 '''%(lcntu['id'])
#             if lcntu['loai']=='loai_tamung' and lcntu['id']:
#                 sql+='''
#                     and loai_tamung_id = %s 
#                 '''%(lcntu['id'])
#             self.cr.execute(sql)
#             notrongky = self.cr.fetchone()[0]
#             nodauky = self.get_nodauky(mlg_type,lcntu)
#             nocuoiky = nodauky+notrongky
#             self.tongcongno += nocuoiky
#             return nocuoiky
#         return 0
    
    def get_chitiet_congno(self, mlg_type,lcntu):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        partner_id = wizard_data['partner_id']
        sql = '''
            select ai.id as invoice_id,ai.date_invoice as ngay,ai.name as maphieudexuat,rp.ma_doi_tuong as madoituong,rp.name as tendoituong,
                (COALESCE(ai.so_tien,0)+COALESCE(sotien_lai,0)) as no,ai.loai_giaodich as loai_giaodich,ai.dien_giai as dien_giai,bsx.name as bien_so_xe,
                (COALESCE(ai.so_tien,0)+COALESCE(ai.sotien_lai,0)-COALESCE(ai.residual,0)-COALESCE(ai.sotien_lai_conlai,0)) as co,ai.fusion_id as fusion_id
            
                from account_invoice ai
                left join res_partner rp on rp.id = ai.partner_id
                left join bien_so_xe bsx on ai.bien_so_xe_id=bsx.id
                
                where ai.partner_id=%s and ai.state in ('open','paid') and ai.date_invoice between '%s' and '%s' and ai.chinhanh_id=%s
                    and ai.mlg_type='%s' 
        '''%(partner_id[0],period_from.date_start,period_to.date_stop,chinhanh_id[0],mlg_type)
        if lcntu['loai']=='loai_nodoanhthu' and lcntu['id']:
            sql+='''
                and ai.loai_nodoanhthu_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_baohiem' and lcntu['id']:
            sql+='''
                and ai.loai_baohiem_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_vipham' and lcntu['id']:
            sql+='''
                and ai.loai_vipham_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='maxuong' and lcntu['id']:
            sql+='''
                and ai.ma_xuong_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_tamung' and lcntu['id']:
            sql+='''
                and ai.loai_tamung_id = %s 
            '''%(lcntu['id'])
        self.cr.execute(sql)
        lines = self.cr.dictfetchall()
        
        sql = '''
            select case when sum(COALESCE(ai.so_tien,0)+COALESCE(ai.sotien_lai,0))!=0 then sum(COALESCE(ai.so_tien,0)+COALESCE(ai.sotien_lai,0)) else 0 end sotienno
            
                from account_invoice ai
                left join res_partner rp on rp.id = ai.partner_id
                left join bien_so_xe bsx on ai.bien_so_xe_id=bsx.id
                
                where ai.partner_id=%s and ai.state in ('open','paid') and ai.date_invoice between '%s' and '%s' and ai.chinhanh_id=%s
                    and ai.mlg_type='%s' 
        '''%(partner_id[0],period_from.date_start,period_to.date_stop,chinhanh_id[0],mlg_type)
        if lcntu['loai']=='loai_nodoanhthu' and lcntu['id']:
            sql+='''
                and ai.loai_nodoanhthu_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_baohiem' and lcntu['id']:
            sql+='''
                and ai.loai_baohiem_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_vipham' and lcntu['id']:
            sql+='''
                and ai.loai_vipham_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='maxuong' and lcntu['id']:
            sql+='''
                and ai.ma_xuong_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_tamung' and lcntu['id']:
            sql+='''
                and ai.loai_tamung_id = %s 
            '''%(lcntu['id'])
        self.cr.execute(sql)
        congno = self.cr.fetchone()[0]
        self.tongno += congno
        self.congno += congno
        self.nocuoiky += congno
        
        return lines
    
    def get_payment(self, invoice_id):
        if not invoice_id:
            return []
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
        invoice = self.pool.get('account.invoice').browse(self.cr, self.uid, invoice_id)
        pays = []
        for pay in invoice.payment_ids:
            if pay.date >= period_from.date_start and pay.date<=period_to.date_stop:
                pays.append(pay)
                self.nocuoiky = self.nocuoiky-pay.credit
        return pays
    
    def get_only_payment(self, mlg_type, lcntu):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        partner_id = wizard_data['partner_id']
        sql = '''
            select case when sum(credit)!=0 then sum(credit) else 0 end sotien
                from account_move_line
                where move_id in (select move_id from account_voucher
                    where reference in (select name from account_invoice
                        where mlg_type='%s' and state in ('open','paid') and chinhanh_id=%s and partner_id=%s and date_invoice<'%s' 
        '''%(mlg_type,chinhanh_id[0],partner_id[0],period_from.date_start)
        if lcntu['loai']=='loai_nodoanhthu' and lcntu['id']:
            sql+='''
                and loai_nodoanhthu_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_baohiem' and lcntu['id']:
            sql+='''
                and loai_baohiem_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_vipham' and lcntu['id']:
            sql+='''
                and loai_vipham_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='maxuong' and lcntu['id']:
            sql+='''
                and ma_xuong_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_tamung' and lcntu['id']:
            sql+='''
                and loai_tamung_id = %s 
            '''%(lcntu['id'])
        sql += ''' ))
                and date between '%s' and '%s' '''%(period_from.date_start,period_to.date_stop)
        self.cr.execute(sql)
        co = self.cr.fetchone()[0]
        self.tongco += co
        self.congco += co
        self.nocuoiky = self.nocuoiky-co
        
        sql = '''
            select date,fusion_id,credit,ref,loai_giaodich,note_giaodich
                from account_move_line
                where credit!=0 and move_id in (select move_id from account_voucher
                    where reference in (select name from account_invoice
                        where mlg_type='%s' and state in ('open','paid') and chinhanh_id=%s and partner_id=%s and date_invoice<'%s' 
        '''%(mlg_type,chinhanh_id[0],partner_id[0],period_from.date_start)
        if lcntu['loai']=='loai_nodoanhthu' and lcntu['id']:
            sql+='''
                and loai_nodoanhthu_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_baohiem' and lcntu['id']:
            sql+='''
                and loai_baohiem_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_vipham' and lcntu['id']:
            sql+='''
                and loai_vipham_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='maxuong' and lcntu['id']:
            sql+='''
                and ma_xuong_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_tamung' and lcntu['id']:
            sql+='''
                and loai_tamung_id = %s 
            '''%(lcntu['id'])
        sql += ''' ))
                and date between '%s' and '%s' '''%(period_from.date_start,period_to.date_stop)
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_lichsu_thutienlai(self, invoice_id):
        if not invoice_id:
            return []
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
        invoice = self.pool.get('account.invoice').browse(self.cr, self.uid, invoice_id)
        invoice = self.pool.get('account.invoice').browse(self.cr, self.uid, invoice_id)
        pays = []
        for pay in invoice.lichsu_thutienlai_line:
            if pay.ngay >= period_from.date_start and pay.ngay<=period_to.date_stop:
                pays.append(pay)
                self.nocuoiky = self.nocuoiky-pay.so_tien
        return pays
    
    