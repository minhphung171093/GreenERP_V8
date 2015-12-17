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
            'get_title_congno': self.get_title_congno,
            'get_nodauky': self.get_nodauky,
            'convert_amount': self.convert_amount,
            'get_chitiet_congno': self.get_chitiet_congno,
            'get_nocuoiky': self.get_nocuoiky,
            'get_tongcongno': self.get_tongcongno,
            'get_thang': self.get_thang,
            'get_chinhanh': self.get_chinhanh,
            'get_congno': self.get_congno,
        })
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        return ''
    
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
    
    def get_thang(self):
        wizard_data = self.localcontext['data']['form']
        period_id = wizard_data['period_id']
        return period_id and period_id[1] or ''
    
    def convert_amount(self, amount):
        a = format(int(amount),',')
        return a
    
    def get_congno(self):
        wizard_data = self.localcontext['data']['form']
        loai_congno_ids = wizard_data['loai_congno_ids']
        loai_congno_obj = self.pool.get('loai.cong.no')
        if not loai_congno_ids:
            loai_congno_ids = loai_congno_obj.search(self.cr, self.uid, [])
        return loai_congno_obj.browse(self.cr, self.uid, loai_congno_ids)
    
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
    
    def get_title_doituong(self, partner_id):
        if partner_id:
            partner = self.pool.get('res.partner').browse(self.cr, self.uid, partner_id)
            return (partner.ma_doi_tuong or '')+'_'+(partner.name or '')
        return ''
    
    def get_nodauky(self, mlg_type):
        wizard_data = self.localcontext['data']['form']
        if mlg_type:
            period_id = wizard_data['period_id']
            period = self.pool.get('account.period').browse(self.cr, self.uid, period_id[0])
            chinhanh_id = wizard_data['chinhanh_id']
            partner_id = wizard_data['partner_id']
#             mlg_type = self.get_title_congno(congno)
            sql = '''
                select case when sum(so_tien_no)!=0 then sum(so_tien_no) else 0 end nodauky
                    from congno_dauky_line where mlg_type='%s' and chinhanh_id=%s
                        and congno_dauky_id in (select id from congno_dauky where partner_id=%s and period_id=%s)
            '''%(mlg_type,chinhanh_id[0],partner_id[0],period_id[0])
            self.cr.execute(sql)
            return self.cr.fetchone()[0]
        return 0
    
    def get_tongcongno(self):
        return self.tongcongno
    
    def get_nocuoiky(self, mlg_type):
        wizard_data = self.localcontext['data']['form']
        if mlg_type:
            period_id = wizard_data['period_id']
            period = self.pool.get('account.period').browse(self.cr, self.uid, period_id[0])
            chinhanh_id = wizard_data['chinhanh_id']
            partner_id = wizard_data['partner_id']
#             mlg_type = self.get_title_congno(congno)
            sql = '''
                select case when sum(residual+sotien_lai_conlai)!=0 then sum(residual+sotien_lai_conlai) else 0 end notrongky
                    from account_invoice where mlg_type='%s' and chinhanh_id=%s and partner_id=%s
                        and date_invoice between '%s' and '%s' and state in ('open','paid') 
            '''%(mlg_type,chinhanh_id[0],partner_id[0],period.date_start,period.date_stop)
            self.cr.execute(sql)
            notrongky = self.cr.fetchone()[0]
            nodauky = self.get_nodauky(mlg_type)
            nocuoiky = nodauky+notrongky
            self.tongcongno += nocuoiky
            return nocuoiky
        return 0
    
    def get_chitiet_congno(self, mlg_type):
        wizard_data = self.localcontext['data']['form']
        period_id = wizard_data['period_id']
        chinhanh_id = wizard_data['chinhanh_id']
        partner_id = wizard_data['partner_id']
#         mlg_type = self.get_title_congno(congno)
        period = self.pool.get('account.period').browse(self.cr, self.uid, period_id[0])
        sql = '''
            select rp.ma_doi_tuong as madoituong,rp.name as tendoituong,
                sum(ai.so_tien+ai.sotien_lai) as no, sum(ai.so_tien+ai.sotien_lai-ai.residual-ai.sotien_lai_conlai) as co
            
                from account_invoice ai
                left join res_partner rp on rp.id = ai.partner_id
                
                where ai.partner_id=%s and ai.state in ('open','paid') and ai.date_invoice between '%s' and '%s' and ai.chinhanh_id=%s
                    and ai.mlg_type='%s'
                group by rp.ma_doi_tuong,rp.name
        '''%(partner_id[0],period.date_start,period.date_stop,chinhanh_id[0],mlg_type)
        self.cr.execute(sql)
        return self.cr.dictfetchall()
            
    
    