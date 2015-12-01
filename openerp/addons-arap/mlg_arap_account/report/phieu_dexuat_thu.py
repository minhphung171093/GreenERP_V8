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
from openerp.addons.mlg_arap_account.report import amount_to_text_vn

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'convert_date': self.convert_date,
            'convert_amount': self.convert_amount,
            'convert': self.convert,
            'get_sotien': self.get_sotien,
            'get_title': self.get_title,
            'get_ngay': self.get_ngay,
            'get_diengiai': self.get_diengiai,
            'get_phuongthuc_thanhtoan': self.get_phuongthuc_thanhtoan,
            'get_loai': self.get_loai,
            'get_ghichu': self.get_ghichu,
            'get_datenow': self.get_datenow,
            'get_user': self.get_user,
        })
        
    def get_loai(self):
        wizard_data = self.localcontext['data']['form']
        loai=wizard_data['loai']
        if loai=='thu':
            return 'THU'
        else:
            return 'CHI'
        
    def get_user(self):
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
        return user.name
        
    def get_sotien(self):
        wizard_data = self.localcontext['data']['form']
        so_tien = wizard_data['so_tien']
        return so_tien
    
    def get_diengiai(self):
        wizard_data = self.localcontext['data']['form']
        diengiai = wizard_data['diengiai']
        return diengiai
    
    def get_ghichu(self,o):
        wizard_data = self.localcontext['data']['form']
        loai=wizard_data['loai']
        if loai=='chi':
            return o.dien_giai
        else:
            return ''
    
    def get_phuongthuc_thanhtoan(self):
        wizard_data = self.localcontext['data']['form']
        phuongthuc_thanhtoan = wizard_data['phuongthuc_thanhtoan']
        if phuongthuc_thanhtoan=='tienmat':
            return 'Tiền mặt'
        return 'Ngân hàng'
    
    def get_ngay(self):
        wizard_data = self.localcontext['data']['form']
        ngay = wizard_data['ngay']
        if ngay:
            return self.convert_date(ngay)
        else:
            return ''
    
    def get_datenow(self):
        date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        return ''
    
    def get_title(self, mlg_type):
        tt = ''
        if mlg_type=='no_doanh_thu':
            tt='NỢ DOANH THU'
        if mlg_type=='chi_ho_dien_thoai':
            tt='CHI HỘ ĐIỆN THOẠI'
        if mlg_type=='phai_thu_bao_hiem':
            tt='BẢO HIỂM'
        if mlg_type=='phai_thu_ky_quy':
            tt='KÝ QUỸ'
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
            tt='KÝ QUỸ'
        if mlg_type=='chi_ho':
            tt='CHI HỘ'
        return tt
    
    def convert(self, amount):
        amount_text = amount_to_text_vn.amount_to_text(amount, 'vn')
        if amount_text and len(amount_text)>1:
            amount = amount_text[1:]
            head = amount_text[:1]
            amount_text = head.upper()+amount
        return amount_text
    
    def convert_amount(self, amount):
        a = format(int(amount),',')
        return a
    