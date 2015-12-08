# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import sys
reload(sys)
sys.setdefaultencoding('utf-8')



class doanh_so_phaithu_wizard(osv.osv_memory):
    _name = "doanh.so.phaithu.wizard"
    
    _columns = {
        'from_date': fields.date('Ngày bắt đầu', required=True),
        'to_date': fields.date('Ngày kết thúc', required=True),
        'chinhanh_id': fields.many2one('account.account','Chi nhánh'),
    }
    
    def _get_chinhanh(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.chinhanh_id and user.chinhanh_id.id or False
    
    _defaults = {
        'from_date': time.strftime('%Y-%m-01'),
        'to_date': lambda *a: str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10],
        'chinhanh_id': _get_chinhanh,
    }
    
    def review_report(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        sql = '''
            select * from fin_output_theodoanhsophaithu_oracle('%s','%s',%s)
        '''%(this.from_date,this.to_date,this.chinhanh_id.id)
        cr.execute(sql)
        doanhsophaithu_line = []
        for line in cr.dictfetchall():
            doanhsophaithu_line.append((0,0,{
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
            'chinhanh_id': this.chinhanh_id.id,
            'doanhsophaithu_line':doanhsophaithu_line,
        }
        report_id = self.pool.get('doanh.so.phaithu').create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'mlg_arap_account', 'view_doanh_so_phaithu_form')
        return {
                    'name': 'Doanh số phải thu',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'doanh.so.phaithu',
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
        datas['model'] = 'doanh.so.phaithu.wizard'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0]})
        return {'type': 'ir.actions.report.xml', 'report_name': 'doanh_so_phaithu_wizard_report', 'datas': datas}
        
doanh_so_phaithu_wizard()

class doanh_so_phaithu(osv.osv_memory):
    _name = "doanh.so.phaithu"
    
    _columns = {
        'from_date': fields.date('Ngày bắt đầu'),
        'to_date': fields.date('Ngày kết thúc'),
        'doanhsophaithu_line': fields.one2many('doanh.so.phaithu.line', 'doanhsophaithu_id', 'Chi tiết'),
        'chinhanh_id': fields.many2one('account.account','Chi nhánh'),
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'doanh.so.phaithu'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0]})
        return {'type': 'ir.actions.report.xml', 'report_name': 'doanh_so_phaithu_report', 'datas': datas}
    
doanh_so_phaithu()

class doanh_so_phaithu_line(osv.osv_memory):
    _name = "doanh.so.phaithu.line"
    
    _columns = {
        'doanhsophaithu_id': fields.many2one('doanh.so.phaithu', 'Doanh số phải thu', ondelete='cascade'),
        'chinhanh': fields.char('Chi nhánh', size=1024),
        'machinhanh': fields.char('Mã chi nhánh', size=1024),
        'loaicongno': fields.char('Loại công nợ', size=1024),
        'taikhoan': fields.char('Tài khoản', size=1024),
        'sotien': fields.float('Số tiền',digits=(16,0)),
        'ghichu': fields.char('Ghi chú', size=1024),
    }
    
doanh_so_phaithu_line()
