# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tinh_hinh_cap_giay_chung_nhan_report(osv.osv_memory):
    _name = "tinh.hinh.cap.giay.chung.nhan.report"
    _columns = {
        'date_from': fields.date('Ngày bắt đầu', required=True),
        'date_to': fields.date('Ngày kết thúc', required=True),
    }
    
    _defaults = {
         'date_from': time.strftime('%Y-01-01'),
         'date_to': time.strftime('%Y-12-31'),
        }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
             
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tinh.hinh.cap.giay.chung.nhan.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tinh_hinh_cap_giay_chung_nhan_report', 'datas': datas}
    
    def print_thu_hoi(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
             
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tinh.hinh.cap.giay.chung.nhan.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tinh_hinh_thu_hoi_giay_chung_nhan_report', 'datas': datas}
        
tinh_hinh_cap_giay_chung_nhan_report()