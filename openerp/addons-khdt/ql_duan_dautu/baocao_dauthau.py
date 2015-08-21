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

class baocao_dauthau(osv.osv):
    _name = "baocao.dauthau"
    
    _columns = {
        'kemtheo_baocao_id': fields.many2one('vanban.den','Kèm theo báo cáo', required=True, states={'done':[('readonly', True)]}),
        'user_id': fields.many2one('res.users','Người tạo', required=True, states={'done':[('readonly', True)]}),
        'donvi_baocao_id': fields.many2one('res.partner','Đơn vị báo cáo', required=True, states={'done':[('readonly', True)]}),
        'name': fields.selection([(num, str(num)) for num in range(2010, 2100)], 'Năm', required = True, states={'done':[('readonly', True)]}),
        'baocao_dauthau_a_line': fields.one2many('baocao.dauthau.line','baocao_dauthau_id','Báo cáo đấu thầu chi tiết', states={'done':[('readonly', True)]}),
        'baocao_dauthau_b_line': fields.one2many('baocao.dauthau.line','baocao_dauthau_id','Báo cáo đấu thầu chi tiết', states={'done':[('readonly', True)]}),
        'baocao_dauthau_c_line': fields.one2many('baocao.dauthau.line','baocao_dauthau_id','Báo cáo đấu thầu chi tiết', states={'done':[('readonly', True)]}),
        'baocao_dauthau_cong_line': fields.one2many('baocao.dauthau.line','baocao_dauthau_id','Báo cáo đấu thầu chi tiết', states={'done':[('readonly', True)]}),
        'state': fields.selection([('draft','Mới tạo'),('done','Đã báo cáo')],'Trạng thái',readonly=True),
        'datao_baocao': fields.boolean('Đã tạo báo cáo', states={'done':[('readonly', True)]}),
        'loai_baocao': fields.selection([('6thang','6 Tháng'),('1nam','1 Năm')],'Loại báo cáo', required = True, states={'done':[('readonly', True)]}),
    }
    
    _defaults = {
        'user_id': lambda self, cr, uid, ids, c={}: uid,
        'name': int(time.strftime('%Y')),
        'state': 'draft',
    }
    
    def tao_baocao(self, cr, uid, ids, context=None):
        bc_dt_line_obj = self.pool.get('baocao.dauthau.line')
        for line in self.browse(cr, uid, ids):
            bc_dt_line_obj.create(cr, uid ,{
                'baocao_dauthau_id': line.id,
                'tieude': True,
                'name': 'I. THEO LĨNH VỰC ĐẤU THẦU',
            })
            linhvuc_obj = self.pool.get('linhvuc.dauthau')
            linhvuc_ids = linhvuc_obj.search(cr, uid, [])
            for linhvuc in linhvuc_obj.browse(cr, uid, linhvuc_ids):
                bc_dt_line_obj.create(cr, uid ,{
                    'baocao_dauthau_id': line.id,
                    'tieude': False,
                    'name': linhvuc.name,
                })
            bc_dt_line_obj.create(cr, uid ,{
                'baocao_dauthau_id': line.id,
                'tieude': True,
                'name': 'II. THEO HÌNH THỨC LỰA CHỌN NHÀ THẦU',
            })
            hinhthuc_obj = self.pool.get('hinhthuc.luachon.nhathau')
            hinhthuc_ids = hinhthuc_obj.search(cr, uid, [])
            for hinhthuc in hinhthuc_obj.browse(cr, uid, hinhthuc_ids):
                bc_dt_line_obj.create(cr, uid ,{
                    'baocao_dauthau_id': line.id,
                    'tieude': False,
                    'name': hinhthuc.name,
                })
            self.write(cr, uid, [line.id], {'datao_baocao': True})
        return True
    
    def baocao(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'})
    
    def write(self, cr, uid, ids, vals, context=None):
        bc_dt_line_obj = self.pool.get('baocao.dauthau.line')
        new_write = super(baocao_dauthau, self).write(cr, uid, ids, vals, context)
        for bcdt in self.browse(cr, uid, ids):
            bcdt_line_ids = bc_dt_line_obj.search(cr, uid, [('baocao_dauthau_id','=',bcdt.id),('tieude','=',True)],order='sequence') 
            for line in bc_dt_line_obj.browse(cr, uid, bcdt_line_ids):
                tongso_goithau_a = 0
                tongso_goithau_b = 0
                tongso_goithau_c = 0
                tongso_goithau = 0
                tonggia_goithau_a = 0
                tonggia_goithau_b = 0
                tonggia_goithau_c = 0
                tonggia_goithau = 0
                tonggia_trungthau_a = 0
                tonggia_trungthau_b = 0
                tonggia_trungthau_c = 0
                tonggia_trungthau = 0
                chenhlech_a = 0
                chenhlech_b = 0
                chenhlech_c = 0
                tong_chenhlech = 0
                bc_dt_line_ids = bc_dt_line_obj.search(cr, uid, [('sequence','>',line.sequence),('baocao_dauthau_id','=',bcdt.id)],order='sequence')
                for line2 in bc_dt_line_obj.browse(cr, uid, bc_dt_line_ids):
                    if not line2.tieude:
                        tongso_goithau_a += line2.tongso_goithau_a
                        tongso_goithau_b += line2.tongso_goithau_b
                        tongso_goithau_c += line2.tongso_goithau_c
                        tongso_goithau += line2.tongso_goithau
                        tonggia_goithau_a += line2.tonggia_goithau_a
                        tonggia_goithau_b += line2.tonggia_goithau_b
                        tonggia_goithau_c += line2.tonggia_goithau_c
                        tonggia_goithau += line2.tonggia_goithau
                        tonggia_trungthau_a += line2.tonggia_trungthau_a
                        tonggia_trungthau_b += line2.tonggia_trungthau_b
                        tonggia_trungthau_c += line2.tonggia_trungthau_c
                        tonggia_trungthau += line2.tonggia_trungthau
                        chenhlech_a += line2.chenhlech_a
                        chenhlech_b += line2.chenhlech_b
                        chenhlech_c += line2.chenhlech_c
                        tong_chenhlech += line2.tong_chenhlech
                    else:
                        break
                sql = '''
                    update baocao_dauthau_line set
                            tongso_goithau_a = %s,
                            tongso_goithau_b = %s,
                            tongso_goithau_c = %s,
                            tongso_goithau = %s,
                            tonggia_goithau_a = %s,
                            tonggia_goithau_b = %s,
                            tonggia_goithau_c = %s,
                            tonggia_goithau = %s,
                            tonggia_trungthau_a = %s,
                            tonggia_trungthau_b = %s,
                            tonggia_trungthau_c = %s,
                            tonggia_trungthau = %s,
                            chenhlech_a = %s,
                            chenhlech_b = %s,
                            chenhlech_c = %s,
                            tong_chenhlech = %s
                        where id=%s
                '''%(
                    tongso_goithau_a,
                    tongso_goithau_b,
                    tongso_goithau_c,
                    tongso_goithau,
                    tonggia_goithau_a,
                    tonggia_goithau_b,
                    tonggia_goithau_c,
                    tonggia_goithau,
                    tonggia_trungthau_a,
                    tonggia_trungthau_b,
                    tonggia_trungthau_c,
                    tonggia_trungthau,
                    chenhlech_a,
                    chenhlech_b,
                    chenhlech_c,
                    tong_chenhlech,
                    line.id
                )
                cr.execute(sql)
        return new_write
    
baocao_dauthau()

class baocao_dauthau_line(osv.osv):
    _name = "baocao.dauthau.line"

    def _total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        tongso_goithau = 0
        tonggia_goithau = 0
        tonggia_trungthau = 0
        tong_chenhlech = 0
        for baocao in self.browse(cr, uid, ids, context=context):
            tongso_goithau = baocao.tongso_goithau_a + baocao.tongso_goithau_b + baocao.tongso_goithau_c
            tonggia_goithau = baocao.tonggia_goithau_a + baocao.tonggia_goithau_b + baocao.tonggia_goithau_c
            tonggia_trungthau = baocao.tonggia_trungthau_a + baocao.tonggia_trungthau_b + baocao.tonggia_trungthau_c
        res[baocao.id] = {
            'tongso_goithau': tongso_goithau,
            'tonggia_goithau': tonggia_goithau,
            'tonggia_trungthau': tonggia_trungthau,
            'tong_chenhlech': tonggia_goithau - tonggia_trungthau,
        }
        return res
    
    def _get_chenhlech(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        chenhlech_a = 0
        chenhlech_b = 0
        chenhlech_c = 0
        for baocao in self.browse(cr, uid, ids, context=context):
            chenhlech_a = baocao.tonggia_goithau_a - baocao.tonggia_trungthau_a
            chenhlech_b = baocao.tonggia_goithau_b - baocao.tonggia_trungthau_b
            chenhlech_c = baocao.tonggia_goithau_c - baocao.tonggia_trungthau_c
        res[baocao.id] = {
            'chenhlech_a': chenhlech_a,
            'chenhlech_b': chenhlech_b,
            'chenhlech_c': chenhlech_c,
        }
        return res
    
    _columns = {
        'sequence' :fields.integer('Sequence'),
        'name' :fields.char('Nội dung', size=256),
        'tieude' : fields.boolean('Tiêu đề'),
        'baocao_dauthau_id': fields.many2one('baocao.dauthau', 'Báo cáo đấu thầu', ondelete='cascade'),
        'tongso_goithau_a': fields.integer('Tổng số gói thầu'),
        'tongso_goithau_b': fields.integer('Tổng số gói thầu'),
        'tongso_goithau_c': fields.integer('Tổng số gói thầu'),
        'tonggia_goithau_a': fields.float('Tổng giá gói thầu'),
        'tonggia_goithau_b': fields.float('Tổng giá gói thầu'),
        'tonggia_goithau_c': fields.float('Tổng giá gói thầu'),
        'tonggia_trungthau_a': fields.float('Tổng giá trúng thầu'),
        'tonggia_trungthau_b': fields.float('Tổng giá trúng thầu'),
        'tonggia_trungthau_c': fields.float('Tổng giá trúng thầu'),
        'chenhlech_a': fields.function(_get_chenhlech, string='Chênh lệch',type='float', digits=(16,0),
            store={
                'baocao.dauthau.line': (lambda self, cr, uid, ids, c={}: ids, ['tongso_goithau_a',
                                                                               'tongso_goithau_b',
                                                                               'tongso_goithau_c',
                                                                               'tonggia_goithau_a',
                                                                               'tonggia_goithau_b',
                                                                               'tonggia_goithau_c',
                                                                               'tonggia_trungthau_a',
                                                                               'tonggia_trungthau_b',
                                                                               'tonggia_trungthau_c',], 10),
            },
            multi='chenhlech'),
        'chenhlech_b': fields.function(_get_chenhlech, string='Chênh lệch',type='float', digits=(16,0),
            store={
                'baocao.dauthau.line': (lambda self, cr, uid, ids, c={}: ids, ['tongso_goithau_a',
                                                                               'tongso_goithau_b',
                                                                               'tongso_goithau_c',
                                                                               'tonggia_goithau_a',
                                                                               'tonggia_goithau_b',
                                                                               'tonggia_goithau_c',
                                                                               'tonggia_trungthau_a',
                                                                               'tonggia_trungthau_b',
                                                                               'tonggia_trungthau_c',], 10),
            },
            multi='chenhlech'),
        'chenhlech_c': fields.function(_get_chenhlech, string='Chênh lệch',type='float', digits=(16,0),
            store={
                'baocao.dauthau.line': (lambda self, cr, uid, ids, c={}: ids, ['tongso_goithau_a',
                                                                               'tongso_goithau_b',
                                                                               'tongso_goithau_c',
                                                                               'tonggia_goithau_a',
                                                                               'tonggia_goithau_b',
                                                                               'tonggia_goithau_c',
                                                                               'tonggia_trungthau_a',
                                                                               'tonggia_trungthau_b',
                                                                               'tonggia_trungthau_c',], 10),
            },
            multi='chenhlech'),
        'tongso_goithau': fields.function(_total, string='Tổng số gói thầu',type='float', digits=(16,0),
            store={
                'baocao.dauthau.line': (lambda self, cr, uid, ids, c={}: ids, ['tongso_goithau_a',
                                                                               'tongso_goithau_b',
                                                                               'tongso_goithau_c',
                                                                               'tonggia_goithau_a',
                                                                               'tonggia_goithau_b',
                                                                               'tonggia_goithau_c',
                                                                               'tonggia_trungthau_a',
                                                                               'tonggia_trungthau_b',
                                                                               'tonggia_trungthau_c',], 10),
            },
            multi='sums'),
        'tonggia_goithau': fields.function(_total, string='Tổng giá gói thầu',type='float', digits=(16,0),
            store={
                'baocao.dauthau.line': (lambda self, cr, uid, ids, c={}: ids, ['tongso_goithau_a',
                                                                               'tongso_goithau_b',
                                                                               'tongso_goithau_c',
                                                                               'tonggia_goithau_a',
                                                                               'tonggia_goithau_b',
                                                                               'tonggia_goithau_c',
                                                                               'tonggia_trungthau_a',
                                                                               'tonggia_trungthau_b',
                                                                               'tonggia_trungthau_c',], 10),
            },
            multi='sums'),
        'tonggia_trungthau': fields.function(_total, string='Tổng giá trúng thầu',type='float', digits=(16,0),
            store={
                'baocao.dauthau.line': (lambda self, cr, uid, ids, c={}: ids, ['tongso_goithau_a',
                                                                               'tongso_goithau_b',
                                                                               'tongso_goithau_c',
                                                                               'tonggia_goithau_a',
                                                                               'tonggia_goithau_b',
                                                                               'tonggia_goithau_c',
                                                                               'tonggia_trungthau_a',
                                                                               'tonggia_trungthau_b',
                                                                               'tonggia_trungthau_c',], 10),
            },
            multi='sums'),
        'tong_chenhlech': fields.function(_total, string='Chênh lệch',type='float', digits=(16,0),
            store={
                'baocao.dauthau.line': (lambda self, cr, uid, ids, c={}: ids, ['tongso_goithau_a',
                                                                               'tongso_goithau_b',
                                                                               'tongso_goithau_c',
                                                                               'tonggia_goithau_a',
                                                                               'tonggia_goithau_b',
                                                                               'tonggia_goithau_c',
                                                                               'tonggia_trungthau_a',
                                                                               'tonggia_trungthau_b',
                                                                               'tonggia_trungthau_c',], 10),
            },
            multi='sums'),
    }
    
    def unlink(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            update_ids = self.search(cr, uid,[('baocao_dauthau_id','=',line.invoice_id.id),('sequence','>',line.sequence)])
            if update_ids:
                cr.execute("UPDATE baocao_dauthau_line SET sequence=sequence-1 WHERE id in %s",(tuple(update_ids),))
        return super(baocao_dauthau_line, self).unlink(cr, uid, ids, context)  
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('baocao_dauthau_id',False):
            vals['sequence'] = len(self.search(cr, uid,[('baocao_dauthau_id', '=', vals['baocao_dauthau_id'])])) + 1
        return super(baocao_dauthau_line, self).create(cr, uid, vals, context)
    
baocao_dauthau_line()

class print_baocao_dauthau(osv.osv_memory):
    _name = "print.baocao.dauthau"
    
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
        datas['model'] = 'print.baocao.dauthau'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'print_baocao_dauthau_report', 'datas': datas}
    
print_baocao_dauthau()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
