# -*- coding: utf-8 -*-
##############################################################################
#
#    HLVSolution, Open Source Management Solution
#
##############################################################################
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from mmap import mmap,ACCESS_READ
from openerp.addons.xlrd import open_workbook

import os
from openerp import modules
base_path = os.path.dirname(modules.get_module_path('ql_duan_dautu'))

class mau_baocao_giamsat(osv.osv):
    _name = "mau.baocao.giamsat"
    _description = "Mau bao cao giam sat"
#     _order = "stt"
    
    _columns = {
        'name' :fields.char('Nội dung', size=256, required=True),
        'stt' : fields.char('STT', size=64, required=True),
        'tieude' : fields.boolean('Tiêu đề'),
    }
    def init(self, cr):
        wb = open_workbook(base_path     + '/ql_duan_dautu/data/MauBaoCaoGiamSat.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    val0 = s.cell(row,0).value
                    val1 = s.cell(row,1).value
                    danhmuc_ids = self.search(cr, 1, [('stt','=',val0),('name','=',val1)])
                    if not danhmuc_ids:
                        self.create(cr, 1, {'name': val1,'stt':val0})
mau_baocao_giamsat()

class baocao_giamsat(osv.osv):
    _name = "baocao.giamsat"
    _description = "Bao cao giam sat"
#     _order = "stt"
    
    _columns = {
        'kemtheo_baocao_id': fields.many2one('vanban.den','Kèm theo báo cáo', required=True, states={'done':[('readonly', True)]}),
        'user_id': fields.many2one('res.users','Người tạo', required=True, states={'done':[('readonly', True)]}),
        'donvi_baocao_id': fields.many2one('res.partner','Đơn vị báo cáo', required=True, states={'done':[('readonly', True)]}),
        'name': fields.selection([(num, str(num)) for num in range(2010, 2100)], 'Năm', required = True, states={'done':[('readonly', True)]}),
        'baocao_giamsat_lines': fields.one2many('baocao.giamsat.line','baocao_giamsat_id','Báo cáo giám sát chi tiết', states={'done':[('readonly', True)]}),
        'datao_baocao': fields.boolean('Đã tạo báo cáo', states={'done':[('readonly', True)]}),
        'state': fields.selection([('draft','Mới tạo'),('done','Đã báo cáo')],'Trạng thái',readonly=True),
        'loai_baocao': fields.selection([('6thang','6 Tháng'),('1nam','1 Năm')],'Loại báo cáo', required = True, states={'done':[('readonly', True)]}),
    }
    
    _defaults = {
        'datao_baocao': False,
        'user_id': lambda self, cr, uid, ids, c={}: uid,
        'name': int(time.strftime('%Y')),
        'state': 'draft',
    }
    
    def tao_baocao(self, cr, uid, ids, context=None):
        mau_bacao_obj = self.pool.get('mau.baocao.giamsat')
        for id in ids:
            mau_bacao_ids = mau_bacao_obj.search(cr, uid, [])
            if mau_bacao_ids:
                for mau_bacao in mau_bacao_obj.browse(cr, uid, mau_bacao_ids):
                    self.pool.get('baocao.giamsat.line').create(cr, uid, {'name':mau_bacao.name,'tieude':mau_bacao.tieude,'stt':mau_bacao.stt,'baocao_giamsat_id':id})
                self.write(cr, uid, ids, {'datao_baocao': True})
        return True
    
    def baocao(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'})
    
baocao_giamsat()

class baocao_giamsat_line(osv.osv):
    _name = "baocao.giamsat.line"
    _description = "Bao cao giam sat chi tiet"
    
    def _total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for baocao in self.browse(cr, uid, ids, context=context):
            res[baocao.id] = {'tongso': int(baocao.nhom_a + baocao.nhom_b + baocao.nhom_c)}
        return res
    
    _columns = {
        'sequence' :fields.integer('Sequence'),
        'name' :fields.char('Nội dung', size=256),
        'stt' : fields.char('STT', size=64),
        'tieude' : fields.boolean('Tiêu đề'),
        'baocao_giamsat_id': fields.many2one('baocao.giamsat', 'Báo cáo giám sát', ondelete='cascade'),
        'tongso': fields.function(_total, string='Tổng số',type='float', digits=(16,0),
            store={
                'baocao.giamsat.line': (lambda self, cr, uid, ids, c={}: ids, ['nhom_a','nhom_b','nhom_c'], 10),
            },
            multi='sums'),
        'nhom_a': fields.integer('A'),
        'nhom_b': fields.integer('B'),
        'nhom_c': fields.integer('C'),
        'ghichu' : fields.text('Ghi chú'),
    }
    
    def unlink(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            update_ids = self.search(cr, uid,[('baocao_giamsat_id','=',line.invoice_id.id),('sequence','>',line.sequence)])
            if update_ids:
                cr.execute("UPDATE baocao_giamsat_line SET sequence=sequence-1 WHERE id in %s",(tuple(update_ids),))
        return super(baocao_giamsat_line, self).unlink(cr, uid, ids, context)  
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('baocao_giamsat_id',False):
            vals['sequence'] = len(self.search(cr, uid,[('baocao_giamsat_id', '=', vals['baocao_giamsat_id'])])) + 1
        return super(baocao_giamsat_line, self).create(cr, uid, vals, context)
    
baocao_giamsat_line()

class print_baocao_giamsat(osv.osv_memory):
    _name = "print.baocao.giamsat"
    
    _columns = {
        'name': fields.selection([(num, str(num)) for num in range(2010, 2100)], 'Năm', required = True),
        'loai_baocao': fields.selection([('6thang','6 Tháng'),('1nam','1 Năm')],'Loại báo cáo', required = True),
    }
    
    _defaults = {
        'name': int(time.strftime('%Y')),
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
             
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'print.baocao.giamsat'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'print_baocao_giamsat_report', 'datas': datas}
    
print_baocao_giamsat()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
