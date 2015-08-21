# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class xem_cay_nguonvon(osv.osv_memory):
    _name = "xem.cay.nguonvon"
    _columns = {
        'nam': fields.char('Năm', size=5, required=True),
    }
    
    _defaults = {
         'nam': time.strftime('%Y'),
    }
    
    def xem_cay_nguonvon(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        if context is None:
            context = {}
        data = self.browse(cr, uid, ids, context=context)[0]
        result = mod_obj.get_object_reference(cr, uid, 'ql_duan_dautu', 'action_cay_nguon_von')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        result['context'] = str({'nam_nguonvon': data.nam})
        return result
    
xem_cay_nguonvon()