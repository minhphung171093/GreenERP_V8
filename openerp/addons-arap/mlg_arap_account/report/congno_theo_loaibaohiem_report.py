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
            'get_line': self.get_line,
            'convert_date': self.convert_date,
            'get_loaicongno': self.get_loaicongno,
            'get_chinhanh': self.get_chinhanh,
            'get_loaidoituong': self.get_loaidoituong,
            'get_name_loaidoituong': self.get_name_loaidoituong,
        })
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def get_chinhanh(self):
        wizard_data = self.localcontext['data']['form']
        chinhanh_id = wizard_data['chinhanh_id']
        if not chinhanh_id:
            return {'name':'','code':''}
        account = self.pool.get('account.account').browse(self.cr, 1, chinhanh_id[0])
        return {'name':account.name,'code':account.code}
    
    def get_loaicongno(self, loaicongno):
        lcn = ''
        if loaicongno=='no_doanh_thu':
            lcn = u'Nợ DT-BH-AL'
        if loaicongno=='chi_ho_dien_thoai':
            lcn = u'Phải thu chi hộ điện thoại'
        if loaicongno=='phai_thu_bao_hiem':
            lcn = u'Phải thu bảo hiểm'
        if loaicongno=='phai_thu_ky_quy':
            lcn = u'Phải thu ký quỹ'
        if loaicongno=='phat_vi_pham':
            lcn = u'Phạt vi phạm'
        if loaicongno=='thu_no_xuong':
            lcn = u'Thu nợ xưởng'
        if loaicongno=='thu_phi_thuong_hieu':
            lcn = u'Thu phí thương hiệu'
        if loaicongno=='tra_gop_xe':
            lcn = u'Trả góp xe'
        if loaicongno=='hoan_tam_ung':
            lcn = u'Phải thu tạm ứng'
        return lcn
    
#     def get_loaidoituong(self, partner_id):
#         ldt = ''
#         if partner_id:
#             sql = '''
#                 select taixe,nhadautu,nhanvienvanphong from res_partner where id=%s
#             '''%(partner_id)
#             self.cr.execute(sql)
#             partner = self.cr.fetchone()
#             if partner and partner[0]:
#                 ldt = u'Lái xe'
#             if partner and partner[1]:
#                 ldt = u'Nhà đầu tư'
#             if partner and partner[2]:
#                 ldt = u'Nhân viên văn phòng'
#         return ldt
    
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
    
    def get_line(self, ldt):
        wizard_data = self.localcontext['data']['form']
        from_date = wizard_data['from_date']
        to_date = wizard_data['to_date']
        chinhanh_id = wizard_data['chinhanh_id']
        sql = '''
            select ai.name as ma_giaodich, ai.date_invoice as ngay_giaodich, cn.code as ma_chinhanh, cn.name as ten_chinhanh,
                rp.ma_doi_tuong as ma_doituong, rp.name as ten_doituong, ldt.name as loai_doituong, dx.code as ma_doixe,rp.id as partner_id,
                dx.name as ten_doixe, bgc.code as ma_baigiaoca, bgc.name as ten_baigiaoca, tnbgc.name as thungan_baigiaoca,
                dhbgc.name as dieuhanh_baigiaoca, ail.price_unit as sotien, ail.name as diengiai,ai.mlg_type as loaicongno,
                ai.so_hop_dong as so_hop_dong, bsx.name as bien_so_xe, ai.so_hoa_don as so_hoa_don,lbh.name as loaibaohiem,
                ai.ma_bang_chiettinh_chiphi_sua as ma_bang_chiettinh_chiphi_sua,ai.residual as sotienconlai,(ai.so_tien-ai.residual) as sotiendathu
                
                from account_invoice_line ail
                left join account_invoice ai on ail.invoice_id = ai.id
                left join res_partner rp on ai.partner_id = rp.id
                left join loai_doi_tuong ldt on ai.loai_doituong_id = ldt.id
                left join account_account dx on ai.account_id = dx.id
                left join bai_giaoca bgc on ai.bai_giaoca_id = bgc.id
                left join thungan_bai_giaoca tnbgc on bgc.thungan_id = tnbgc.id
                left join dieuhanh_bai_giaoca dhbgc on bgc.dieuhanh_id = dhbgc.id
                left join account_account cn on ai.chinhanh_id = cn.id
                left join bien_so_xe bsx on ai.bien_so_xe_id = bsx.id
                left join loai_bao_hiem lbh on ai.loai_baohiem_id = lbh.id
                where ai.state='open' and ai.chinhanh_id=%s and ai.date_invoice between '%s' and '%s' and ai.mlg_type in ('phai_thu_bao_hiem') 
        '''%(chinhanh_id[0],from_date,to_date)
        
        if ldt=='taixe':
            sql+='''
                and rp.taixe=True 
            '''
        elif ldt=='nhadautu':
            sql+='''
                and rp.nhadautu=True 
            '''
        else:
            sql+='''
                and rp.nhanvienvanphong=True 
            '''
        
        loai_bao_hiem = wizard_data['loai_bao_hiem_id']
        if loai_bao_hiem:
            sql+='''
                and ai.loai_baohiem_id=%s 
            '''%(loai_bao_hiem[0])
        
        self.cr.execute(sql)
        res = self.cr.dictfetchall()
        return res
    
    