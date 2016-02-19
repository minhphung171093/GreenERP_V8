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


class tragopxe_wizard(osv.osv_memory):
    _name = "tragopxe.wizard"
    _columns = {    
        'bien_so_xe_id': fields.many2one('bien.so.xe','Biển số xe', required=True),
    }
    
    def bt_xemcongno(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        sql = '''
            select id from account_invoice where mlg_type='tra_gop_xe' and bien_so_xe_id=%s
        '''%(this.bien_so_xe_id.id)
        cr.execute(sql)
        invoice_ids = [r[0] for r in cr.fetchall()]
        vals = {
            'bien_so_xe_id': this.bien_so_xe_id.id,
            'tra_gop_xe_ids': [(6,0,invoice_ids)],
        }
        tattoan_id = self.pool.get('tragopxe.tattoan').create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'mlg_arap_xuathoadongiam', 'view_tragopxe_tattoan_form')
        return {
                    'name': 'Doanh số thu',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'tragopxe.tattoan',
                    'domain': [],
                    'view_id': res and res[1] or False,
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': tattoan_id,
                }
    
tragopxe_wizard()

class tragopxe_tattoan(osv.osv_memory):
    _name = "tragopxe.tattoan"
    
    def _get_tattoan(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        for tattoan in self.browse(cr, uid, ids, context=context):
            res[tattoan.id] = True
            temp = 0
            for line in tattoan.tra_gop_xe_ids:
                if line.state!='paid':
                    res[tattoan.id] = False
                    break
                if not line.tat_toan:
                    res[tattoan.id] = True
                    break
                if line.tat_toan:
                    temp += 1
            if temp==len(tattoan.tra_gop_xe_ids):
                res[tattoan.id] = False
        return res
    
    _columns = {    
        'bien_so_xe_id': fields.many2one('bien.so.xe','Biển số xe'),
        'show_tattoan': fields.function(_get_tattoan, type='boolean', string='Show tất toán'),
        'tra_gop_xe_ids': fields.many2many('account.invoice','tragopxetattoan_invoice_ref', 'tattoan_id', 'invoice_id','Các công nợ'),
    }
    
    def bt_tattoan(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        for tattoan in self.browse(cr, uid, ids, context=context):
            invoice_ids = [inv.id for inv in tattoan.tra_gop_xe_ids]
            invoice_obj.write(cr, uid, invoice_ids, {'tat_toan':True})
        return True
    
tragopxe_tattoan()
