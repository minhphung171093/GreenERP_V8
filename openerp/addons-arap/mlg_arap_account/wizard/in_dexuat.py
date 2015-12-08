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

class in_dexuat(osv.osv_memory):
    _name = "in.dexuat"
    
    _columns = {
        'from_date': fields.date('Ngày bắt đầu', required=False),
        'to_date': fields.date('Ngày kết thúc', required=False),
        'so_hoa_don':fields.char('Số hóa đơn',size = 64),
        'bien_so_xe_id': fields.many2one('bien.so.xe','Biển số xe'),
        'so_hop_dong': fields.char('Số hợp đồng', size=1024),
        'ma_bang_chiettinh_chiphi_sua': fields.char('Mã chiết tính'),
    }
    
    _defaults = {
        'from_date': time.strftime('%Y-%m-01'),
        'to_date': lambda *a: str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10]
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'in.dexuat'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        name_report = context['name_report']
        return {'type': 'ir.actions.report.xml', 'report_name': name_report, 'datas': datas}
        
in_dexuat()

