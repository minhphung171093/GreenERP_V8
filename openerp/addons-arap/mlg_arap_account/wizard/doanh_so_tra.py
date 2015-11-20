# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare



class doanh_so_tra_wizard(osv.osv_memory):
    _name = "doanh.so.tra.wizard"
    
    _columns = {
        'from_date': fields.date('Ngày bắt đầu', required=True),
        'to_date': fields.date('Ngày kết thúc', required=True),
    }
    
    _defaults = {
        'from_date': time.strftime('%Y-%m-01'),
        'to_date': lambda *a: str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10]
    }
    
    def review_report(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        sql = '''
            select * from fin_output_theodoanhsotra_oracle('%s','%s')
        '''%(this.from_date,this.to_date)
        cr.execute(sql)
        doanhsotra_line = []
        for line in cr.dictfetchall():
            doanhsotra_line.append((0,0,{
                'chinhanh': line['chinhanh'],
                'machinhanh': line['machinhanh'],
                'loaicongno': line['loaicongno'],
                'taikhoan': line['taikhoan'],
                'sotien': line['sotien'],
                'ghichu': line['ghichu'],
            }))
        vals = {
            'from_date': this.from_date,
            'to_date': this.to_date,
            'doanhsotra_line':doanhsotra_line,
        }
        report_id = self.pool.get('doanh.so.tra').create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'mlg_arap_account', 'view_doanh_so_tra_form')
        return {
                    'name': 'Doanh số trả',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'doanh.so.tra',
                    'domain': [],
                    'view_id': res and res[1] or False,
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': report_id,
                }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'doanh.so.tra.wizard'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0]})
        return {'type': 'ir.actions.report.xml', 'report_name': 'doanh_so_tra_wizard_report', 'datas': datas}
        
doanh_so_tra_wizard()

class doanh_so_tra(osv.osv_memory):
    _name = "doanh.so.tra"
    
    _columns = {
        'from_date': fields.date('Ngày bắt đầu'),
        'to_date': fields.date('Ngày kết thúc'),
        'doanhsotra_line': fields.one2many('doanh.so.tra.line', 'doanhsotra_id', 'Chi tiết'),
        
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'doanh.so.tra'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0]})
        return {'type': 'ir.actions.report.xml', 'report_name': 'doanh_so_tra_report', 'datas': datas}
    
doanh_so_tra()

class doanh_so_tra_line(osv.osv_memory):
    _name = "doanh.so.tra.line"
    
    _columns = {
        'doanhsotra_id': fields.many2one('doanh.so.tra', 'Doanh số trả', ondelete='cascade'),
        'chinhanh': fields.char('Chi nhánh', size=1024),
        'machinhanh': fields.char('Mã chi nhánh', size=1024),
        'loaicongno': fields.char('Loại công nợ', size=1024),
        'taikhoan': fields.char('Tài khoản', size=1024),
        'sotien': fields.float('Số tiền'),
        'ghichu': fields.char('Ghi chú', size=1024),
    }
    
doanh_so_tra_line()
