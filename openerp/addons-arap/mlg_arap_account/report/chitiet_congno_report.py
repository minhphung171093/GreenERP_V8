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
        self.tongcong_no = 0
        self.tongcong_co = 0
        self.tongcong_congno = 0
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
            'get_from_thang': self.get_from_thang,
            'get_to_thang': self.get_to_thang,
            'get_payment': self.get_payment,
            'get_chinhanh': self.get_chinhanh,
            'get_lichsu_thutienlai': self.get_lichsu_thutienlai,
            'get_loaidoituong': self.get_loaidoituong,
            'get_name_loaidoituong': self.get_name_loaidoituong,
            'get_tongno': self.get_tongno,
            'get_tongco': self.get_tongco,
            'get_congno': self.get_congno,
            'get_congco': self.get_congco,
            'get_loai_congno_tuongung': self.get_loai_congno_tuongung,
            'get_title_lcntu': self.get_title_lcntu,
            'get_tongcong_no': self.get_tongcong_no,
            'get_tongcong_co': self.get_tongcong_co,
            'get_tongcong_congno': self.get_tongcong_congno,
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
        
    def get_loai_congno_tuongung(self, ldt):
        wizard_data = self.localcontext['data']['form']
        mlg_type = wizard_data['mlg_type']
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
        if lcntu['loai']=='loai_tamung':
            tt = 'Loại tạm ứng: '+lcntu['name']
        return tt
        
    def get_doituong(self, ldt, lcntu):
        wizard_data = self.localcontext['data']['form']
        partner_ids = wizard_data['partner_ids']
        if partner_ids:
            p_ids = []
            partner_obj = self.pool.get('res.partner')
            for partner in partner_obj.browse(self.cr, self.uid, partner_ids):
                if ldt=='taixe' and partner.taixe:
                    p_ids.append(partner.id)
                if ldt=='nhadautu' and partner.nhadautu:
                    p_ids.append(partner.id)
                if ldt=='nhanvienvanphong' and partner.nhanvienvanphong:
                    p_ids.append(partner.id)
            return p_ids
        else:
            period_from_id = wizard_data['period_from_id']
            period_to_id = wizard_data['period_to_id']
            period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
            period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
            chinhanh_id = wizard_data['chinhanh_id']
            mlg_type = wizard_data['mlg_type']
            sql = '''
                select partner_id from account_invoice where date_invoice between '%s' and '%s' and chinhanh_id=%s
                    and state in ('open','paid') and mlg_type='%s' and loai_doituong='%s' 
            '''%(period_from.date_start,period_to.date_stop,chinhanh_id[0],mlg_type,ldt)
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
            if lcntu['loai']=='loai_tamung' and lcntu['id']:
                sql+='''
                    and loai_tamung_id = %s 
                '''%(lcntu['id'])
            sql += ''' group by partner_id '''
            self.cr.execute(sql)
            partner_ids = [r[0] for r in self.cr.fetchall()]
            if ldt=='taixe':
                sql = '''
                    select partner_id from congno_dauky where period_id=%s
                        and id in (select congno_dauky_id from congno_dauky_line where chinhanh_id=%s and mlg_type='%s') and partner_id in (select id from res_partner where taixe=True)
                '''%(period_from_id[0],chinhanh_id[0],mlg_type)
            elif ldt=='nhadautu':
                sql = '''
                    select partner_id from congno_dauky where period_id=%s
                        and id in (select congno_dauky_id from congno_dauky_line where chinhanh_id=%s and mlg_type='%s') and partner_id in (select id from res_partner where nhadautu=True)
                '''%(period_from_id[0],chinhanh_id[0],mlg_type)
            else:
                sql = '''
                    select partner_id from congno_dauky where period_id=%s
                        and id in (select congno_dauky_id from congno_dauky_line where chinhanh_id=%s and mlg_type='%s') and partner_id in (select id from res_partner where nhanvienvanphong=True)
                '''%(period_from_id[0],chinhanh_id[0],mlg_type)
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
            tt='NỢ DT-BH-AL'
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
    
    def get_nodauky(self, partner_id,lcntu):
        wizard_data = self.localcontext['data']['form']
        if partner_id:
            period_id = wizard_data['period_from_id']
            chinhanh_id = wizard_data['chinhanh_id']
            mlg_type = wizard_data['mlg_type']
            sql = '''
                select case when sum(so_tien_no)!=0 then sum(so_tien_no) else 0 end nodauky
                    from congno_dauky_line where mlg_type='%s' and chinhanh_id=%s
                        and congno_dauky_id in (select id from congno_dauky where partner_id=%s and period_id=%s) 
            '''%(mlg_type,chinhanh_id[0],partner_id,period_id[0])
            if lcntu['loai']!='loai_conlai' and lcntu['id']:
                sql = '''
                    select case when sum(so_tien_no)!=0 then sum(so_tien_no) else 0 end nodauky
                        from chitiet_congno_dauky_line where congno_dauky_line_id in (select id from congno_dauky_line where mlg_type='%s' and chinhanh_id=%s
                            and congno_dauky_id in (select id from congno_dauky where partner_id=%s and period_id=%s)) and loai_id=%s
                '''%(mlg_type,chinhanh_id[0],partner_id,period_id[0],lcntu['id'])
            self.cr.execute(sql)
            return self.cr.fetchone()[0]
        return 0
    
    def get_tongcongno(self):
        tongcongno = self.tongcongno
        self.tongcongno = 0
        self.tongcong_congno += tongcongno
        return tongcongno
    
    def get_tongno(self):
        tongno = self.tongno
        self.tongno = 0
        self.tongcong_no += tongno
        return tongno
    
    def get_tongco(self):
        tongco = self.tongco
        self.tongco = 0
        self.tongcong_co += tongco
        return tongco
    
    def get_tongcong_congno(self):
        tongcong_congno = self.tongcong_congno
        self.tongcong_congno = 0
        return tongcong_congno
    
    def get_tongcong_no(self):
        tongcong_no = self.tongcong_no
        self.tongcong_no = 0
        return tongcong_no
    
    def get_tongcong_co(self):
        tongcong_co = self.tongcong_co
        self.tongcong_co = 0
        return tongcong_co
    
    def get_congno(self):
        congno = self.congno
        self.congno = 0
        return congno
    
    def get_congco(self):
        congco = self.congco
        self.congco = 0
        return congco
    
    def get_nocuoiky(self, partner_id,lcntu):
        wizard_data = self.localcontext['data']['form']
        if partner_id:
            period_from_id = wizard_data['period_from_id']
            period_to_id = wizard_data['period_to_id']
            period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
            period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
            chinhanh_id = wizard_data['chinhanh_id']
            mlg_type = wizard_data['mlg_type']
            sql = '''
                select case when sum(COALESCE(residual,0)+COALESCE(sotien_lai_conlai,0))!=0 then sum(COALESCE(residual,0)+COALESCE(sotien_lai_conlai,0)) else 0 end notrongky
                    from account_invoice where mlg_type='%s' and chinhanh_id=%s and partner_id=%s
                        and date_invoice between '%s' and '%s' and state in ('open','paid')  
            '''%(mlg_type,chinhanh_id[0],partner_id,period_from.date_start,period_to.date_stop)
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
            if lcntu['loai']=='loai_tamung' and lcntu['id']:
                sql+='''
                    and loai_tamung_id = %s 
                '''%(lcntu['id'])
            self.cr.execute(sql)
            notrongky = self.cr.fetchone()[0]
            nodauky = self.get_nodauky(partner_id,lcntu)
            nocuoiky = nodauky+notrongky
            self.tongcongno += nocuoiky
            return nocuoiky
        return 0
    
    def get_chitiet_congno(self, partner_id, lcntu):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        mlg_type = wizard_data['mlg_type']
        sql = '''
            select ai.id as invoice_id,ai.date_invoice as ngay,ai.name as maphieudexuat,rp.ma_doi_tuong as madoituong,rp.name as tendoituong,
                (COALESCE(ai.so_tien,0)+COALESCE(sotien_lai,0)) as no,ai.loai_giaodich,
                (COALESCE(ai.so_tien,0)+COALESCE(ai.sotien_lai,0)-COALESCE(ai.residual,0)-COALESCE(ai.sotien_lai_conlai,0)) as co,ai.fusion_id as fusion_id
            
                from account_invoice ai
                left join res_partner rp on rp.id = ai.partner_id
                
                where ai.partner_id=%s and ai.state in ('open','paid') and ai.date_invoice between '%s' and '%s' and ai.chinhanh_id=%s
                    and ai.mlg_type='%s' 
        '''%(partner_id,period_from.date_start,period_to.date_stop,chinhanh_id[0],mlg_type)
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
        if lcntu['loai']=='loai_tamung' and lcntu['id']:
            sql+='''
                and ai.loai_tamung_id = %s 
            '''%(lcntu['id'])
        self.cr.execute(sql)
        lines = self.cr.dictfetchall()
        for line in lines:
            self.tongno += line['no']
            self.tongco += line['co']
            self.congno += line['no']
            self.congco += line['co']
        return lines
    
    def get_payment(self, invoice_id):
        if not invoice_id:
            return []
        invoice = self.pool.get('account.invoice').browse(self.cr, self.uid, invoice_id)
        return invoice.payment_ids
            
    def get_lichsu_thutienlai(self, invoice_id):
        if not invoice_id:
            return []
        invoice = self.pool.get('account.invoice').browse(self.cr, self.uid, invoice_id)
        return invoice.lichsu_thutienlai_line
    