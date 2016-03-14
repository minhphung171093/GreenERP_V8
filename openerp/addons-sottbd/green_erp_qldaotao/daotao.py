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

class ke_hoach_dt(osv.osv): 
    _name = "ke.hoach.dt"
    _columns = {
        'name': fields.char('Tên khóa đào tạo',size = 1024, required = True),
        'lop_id': fields.many2one('lop.hoc','Lớp học'),
        'dia_diem': fields.char('Địa điểm',size = 1024),
        'noi_dung': fields.text('Nội dung'),
        'ctr_lop': fields.text('Cấu trúc lớp'),
        'dieu_kien': fields.char('Điều kiện',size = 1024),
                }
ke_hoach_dt()

class lop_hoc(osv.osv):
    _name = "lop.hoc"
    _columns = {
        'name': fields.char('Tên lớp',size = 1024, required = True),
#         'hocvien_ids': fields.many2many('gv.hv', 'hocvien_lophoc_ref', 'lop_hoc_id', 'hocvien_id', 'Học viên'),
#         'giang_vien_ids': fields.many2many('gv.hv', 'giangvien_donvi_ref', 'lop_hoc_id', 'giangvien_id', 'Giảng viên'),
        'lop_line':fields.one2many('lop.hoc.line','lop_id','Danh sách theo ngày'),  
        'tt_phoc': fields.text('Thông tin phòng học'),
        'tt_tbcs': fields.text('Thông tin thiết bị, cơ sở'),
        'tg_hoc': fields.char('Thời gian học',size = 1024),
        'tl_mon': fields.char('Tài liệu môn học',size = 1024),
                }
lop_hoc()

class lop_hoc_line(osv.osv):
    _name = "lop.hoc.line"
    _columns = {
        'name': fields.date('Ngày'),
        'ten_lop': fields.related('lop_id','name', type='char',string='Tên lớp',readonly=True),
        'lop_id': fields.many2one('lop.hoc','Lớp học',ondelete='cascade'),
        'hocvien_ids': fields.many2many('gv.hv', 'hocvien_lophoc_line_ref', 'line_id', 'hocvien_id', 'Học viên'),
        'giang_vien_id': fields.many2one('gv.hv','Giảng viên'),
                }
    
    def btn_save(self, cr, uid, ids, context=None):
        line_id = self.browse(cr, uid, ids[0],context=context)
        line_ids = self.search(cr, uid, [('id','!=',line_id.id),('name', '=', line_id.name),('lop_id','=',line_id.lop_id.id)]) or []
        ds_ids = [l.id for l in line_id.hocvien_ids] or []
        
        if line_ids:
            ds_ids += [m.id for m in self.browse(cr, uid,line_ids[0],context=context).hocvien_ids] or []
            self.unlink(cr, uid, ids[0], context=context)
            return self.write(cr,uid,line_ids[0],{'hocvien_ids':[(6,0,ds_ids)]})
        else:
            return True
        
    def onchange_hv(self, cr, uid, ids, context=None):
        res = {'value':{'hocvien_ids': [],}}

        return res
        
lop_hoc_line()

class hoso_nangluc(osv.osv):
    _name = "hoso.nangluc"
    _columns = {
        'name': fields.char('Tên',size = 1024, required = True),
                }
hoso_nangluc()

class gv_hv(osv.osv):
    _name = "gv.hv"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns = {
        'name': fields.char('Họ Tên',size = 1024, required = True),
        'noi_ct': fields.char('Nơi công tác',size = 1024),
        'dthoai': fields.char('Điện thoại',size = 1024),
        'email': fields.char('Email',size = 1024),
        'giang_vien': fields.boolean('Giảng viên'),
        'hoc_vien': fields.boolean('Học viên'),
        'can_bo': fields.boolean('Cán bộ'),
        'co_quan': fields.char('Cơ quan',size = 1024, track_visibility='onchange'),
        'chuc_vu': fields.char('Chức vụ',size = 1024, track_visibility='onchange'),
        'td_cntt': fields.char('Trình độ CNTT',size = 1024, track_visibility='onchange'),
        'td_av': fields.char('Trình độ anh văn',size = 1024, track_visibility='onchange'),
        'cc_cntt': fields.char('Chứng chỉ CNTT',size = 1024),
        'qt_thamgia': fields.char('Quá trình tham gia các lớp CNTT',size = 1024, track_visibility='onchange'),
        'hoi_thao': fields.char('Quá trình tham gia hội thảo',size = 1024, track_visibility='onchange'),
        'ghi_nhan': fields.char('Ghi nhận',size = 1024, track_visibility='onchange'),
        'user_account_id': fields.many2one('res.users', 'Tài khoản', track_visibility='onchange'),
                }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('ds_hv') and context.get('name') and context.get('lop_id'):
            sql = '''
                select id from gv_hv where hoc_vien is True and id not in 
                    (select hocvien_id from hocvien_lophoc_line_ref where line_id 
                        in (select id from lop_hoc_line where name='%s' and lop_id=%s))
            '''%(context.get('name'),context.get('lop_id'))
            cr.execute(sql)
            hoc_vien_ids = [row[0] for row in cr.fetchall()]
            hv_ids = self.search(cr, uid, [('id','in',hoc_vien_ids)])
            args += [('id','in',hv_ids)]
        if context.get('ds_hv') and (not context.get('name') or not context.get('lop_id')):
            return []
        return super(gv_hv, self).search(cr, uid, args, offset, limit, order, context, count)
gv_hv()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
