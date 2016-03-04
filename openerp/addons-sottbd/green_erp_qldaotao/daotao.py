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
        'hocvien_ids': fields.many2many('gv.hv', 'hocvien_lophoc_ref', 'lop_hoc_id', 'hocvien_id', 'Học viên'),
        'giang_vien_id': fields.many2one('gv.hv','Giảng viên'),
                }
    
    def btn_save(self, cr, uid, ids, context=None):
        return True
lop_hoc_line()

class hoso_nangluc(osv.osv):
    _name = "hoso.nangluc"
    _columns = {
        'name': fields.char('Tên',size = 1024, required = True),
                }
hoso_nangluc()

class gv_hv(osv.osv):
    _name = "gv.hv"
    _columns = {
        'name': fields.char('Họ Tên',size = 1024, required = True),
        'noi_ct': fields.char('Nơi công tác',size = 1024),
        'dthoai': fields.char('Điện thoại',size = 1024),
        'email': fields.char('Email',size = 1024),
        'giang_vien': fields.boolean('Giảng viên'),
        'hoc_vien': fields.boolean('Học viên'),
                }
gv_hv()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
