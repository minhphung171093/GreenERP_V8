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
        self.localcontext.update({
            'get_doituong': self.get_doituong,
            'convert_date': self.convert_date,
            'get_title_doituong': self.get_title_doituong,
            'convert_amount': self.convert_amount,
            'get_chitiet_congno': self.get_chitiet_congno,
            'get_loai_congno': self.get_loai_congno,
            'get_tongcong': self.get_tongcong,
            'get_chinhanh': self.get_chinhanh,
            'get_from_date': self.get_from_date,
            'get_to_date': self.get_to_date,
        })
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        return ''
    
    def get_from_date(self):
        wizard_data = self.localcontext['data']['form']
        from_date = wizard_data['from_date']
        return self.convert_date(from_date)
    
    def get_to_date(self):
        wizard_data = self.localcontext['data']['form']
        to_date = wizard_data['to_date']
        return self.convert_date(to_date)
    
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
    
    def get_doituong(self):
        wizard_data = self.localcontext['data']['form']
        from_date = wizard_data['from_date']
        to_date = wizard_data['to_date']
        chinhanh_id = wizard_data['chinhanh_id']
        mlg_type = wizard_data['mlg_type']
        sql = '''
            select partner_id from account_invoice
                where date_invoice between '%s' and '%s' and chinhanh_id=%s and mlg_type='%s'
                    and state in ('draft') 
                
                group by partner_id
        '''%(from_date,to_date,chinhanh_id[0],mlg_type)
        self.cr.execute(sql)
        partner_ids = [r[0] for r in self.cr.fetchall()]
        return partner_ids
    
    def get_loai_congno(self):
        wizard_data = self.localcontext['data']['form']
        mlg_type = wizard_data['mlg_type']
        tt = ''
        if mlg_type=='no_doanh_thu':
            tt='NỢ DT-BH-AL'
        if mlg_type=='chi_ho_dien_thoai':
            tt='PHẢI THU CHI HỘ ĐIỆN THOẠI'
        if mlg_type=='phai_thu_bao_hiem':
            tt='PHẢI THU BẢO HIỂM'
        if mlg_type=='phat_vi_pham':
            tt='PHẠT VI PHẠM'
        if mlg_type=='thu_no_xuong':
            tt='THU NỢ XƯỞNG'
        if mlg_type=='thu_phi_thuong_hieu':
            tt='THU PHÍ THƯƠNG HIỆU'
        if mlg_type=='tra_gop_xe':
            tt='TRẢ GÓP XE'
        if mlg_type=='hoan_tam_ung':
            tt='PHẢI THU TẠM ỨNG'
        if mlg_type=='phai_tra_ky_quy':
            tt='PHẢI TRẢ TRẢ KÝ QUỸ'
        if mlg_type=='chi_ho':
            tt='PHẢI TRẢ CHI HỘ'
        return tt
    
    def get_title_doituong(self, partner_id):
        if partner_id:
            partner = self.pool.get('res.partner').browse(self.cr, self.uid, partner_id)
            return (partner.ma_doi_tuong or '')+'_'+(partner.name or '')
        return ''
    
    def get_chitiet_congno(self, partner_id):
        wizard_data = self.localcontext['data']['form']
        from_date = wizard_data['from_date']
        to_date = wizard_data['to_date']
        chinhanh_id = wizard_data['chinhanh_id']
        mlg_type = wizard_data['mlg_type']
        sql = '''
            select ai.date_invoice as ngay,ai.name as maphieudexuat,rp.ma_doi_tuong as madoituong,rp.name as tendoituong,
                ai.so_tien as no, (ai.so_tien-ai.residual) as co
            
                from account_invoice ai
                left join res_partner rp on rp.id = ai.partner_id
                
                where ai.partner_id=%s and ai.state in ('draft') and ai.date_invoice between '%s' and '%s' and ai.chinhanh_id=%s
                    and ai.mlg_type='%s'
        '''%(partner_id,from_date,to_date,chinhanh_id[0],mlg_type)
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_tongcong(self, partner_id):
        wizard_data = self.localcontext['data']['form']
        from_date = wizard_data['from_date']
        to_date = wizard_data['to_date']
        chinhanh_id = wizard_data['chinhanh_id']
        mlg_type = wizard_data['mlg_type']
        sql = '''
            select case when sum(so_tien)!=0 then sum(so_tien) else 0 end tongtien from account_invoice
                where date_invoice between '%s' and '%s' and chinhanh_id=%s and mlg_type='%s' and partner_id=%s
                    and state in ('draft') 
        '''%(from_date,to_date,chinhanh_id[0],mlg_type,partner_id)
        self.cr.execute(sql)
        return self.cr.fetchone()[0]
        
        
    