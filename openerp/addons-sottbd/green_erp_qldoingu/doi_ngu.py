# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import time
from datetime import date
from datetime import timedelta
from datetime import datetime
import calendar
import openerp.addons.decimal_precision as dp
import codecs
import os
# from xlrd import open_workbook,xldate_as_tuple
from openerp import modules

class ls_daotao(osv.osv):
    _name = "ls.daotao"
    _columns = {
        'name': fields.many2one('gv.hv','Cán bộ'),
        'ls_dt_line':fields.one2many('ls.daotao.line','ls_dt_id','Danh sách lớp tham gia'),  
                }
    
    def onchange_line(self, cr, uid, ids, name, context=None):
        if context is None:
            context = {}
        lop_hoc_ids = []
        res = {'value':{'ls_dt_line': lop_hoc_ids,}}
        vals = {}
        if name:
            sql='''
                select lop_id,name from lop_hoc_line where id in (select line_id from hocvien_lophoc_line_ref where hocvien_id = %s)
            '''%(name)
            cr.execute(sql)
            rs = cr.fetchall()
            for r in rs:
                lop_hoc_ids.append((0,0,{'lop_id':r[0],'ngay':r[1]}))
            
            if lop_hoc_ids:
                vals.update({'ls_dt_line': lop_hoc_ids})
                res['value'] = {
                                'ls_dt_line': lop_hoc_ids,
                }

        return res
        
ls_daotao()

class ls_daotao_line(osv.osv):
    _name = "ls.daotao.line"
    _columns = {
        'ls_dt_id': fields.many2one('ls.daotao','Danh sách lớp tham gia',ondelete='cascade'),
        'lop_id': fields.many2one('lop.hoc','Lớp'),
        'ngay': fields.date('Ngày'),
                }
ls_daotao_line()

class kthuong_kluat(osv.osv):
    _name = "kthuong.kluat"
    _columns = {
        'name': fields.char('Tiêu đề',required=True),
        'kt_kluat_line':fields.one2many('kthuong.kluat.line','kt_kluat_id','Danh sách Cán bộ'),  
                }

kthuong_kluat()

class kthuong_kluat_line(osv.osv):
    _name = "kthuong.kluat.line"
    _columns = {
        'kt_kluat_id': fields.many2one('kthuong.kluat','Khen Thưởng Kỉ Luật',ondelete='cascade'),
        'cb_id': fields.many2one('gv.hv','Cán bộ'),
                }
kthuong_kluat_line()

class phu_cap(osv.osv):
    _name = "phu.cap"
    _columns = {
        'name': fields.char('Tiêu đề',required=True),
        'phucap_line':fields.one2many('phu.cap.line','phu_cap_id','Danh sách Cán bộ'),  
                }

phu_cap()

class phu_cap_line(osv.osv):
    _name = "phu.cap.line"
    _columns = {
        'phu_cap_id': fields.many2one('phu.cap','Phụ cấp',ondelete='cascade'),
        'cb_id': fields.many2one('gv.hv','Cán bộ'),
                }
phu_cap_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
