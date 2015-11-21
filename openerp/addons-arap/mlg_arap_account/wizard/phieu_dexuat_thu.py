# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class phieu_de_xuat(osv.osv_memory):
    _name = "phieu.de.xuat"
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(phieu_de_xuat, self).default_get(cr, uid, fields, context=context)
        if context.get('active_id', False):
            invoice_obj = self.pool.get('account.invoice')
            invoice = invoice_obj.browse(cr, uid, context['active_id'])
            res.update({'so_tien': invoice.residual,'partner_id': invoice.partner_id.id})
        return res
    
    _columns = {
        'so_tien': fields.float('Số tiền', required=True),
        'phuongthuc_thanhtoan': fields.selection([('tienmat','Tiền mặt'),('nganhang','Ngân hàng')],'Phương thức thanh toán', required=True),
        'partner_id': fields.many2one('res.partner','Đối tượng'),
        'ngay': fields.date('Ngày'),
        'diengiai': fields.char('Diễn giải', size=1024),
    }
    
    _defaults = {
        'phuongthuc_thanhtoan': 'tienmat',
        'ngay': time.strftime('%Y-%m-%d'),
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'account.invoice'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'phieu_dexuat_thu_report', 'datas': datas}
        
phieu_de_xuat()

