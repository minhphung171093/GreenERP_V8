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

from math import radians, cos, sin, asin, sqrt
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
class tinh_tp(osv.osv):
    _name = "tinh.tp"
    _columns = {
        'name': fields.char('Mã Tỉnh/Thành Phố',size = 1024, required = True),
        'ten': fields.char('Tên Tỉnh/Thành Phố',size = 1024, required = True),
                }
tinh_tp()
class phuong_xa(osv.osv):
    _name = "phuong.xa"
    _columns = {
        'name': fields.char('Phường (xã)',size = 50, required = True),
         'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)', required = True),
                }
phuong_xa()
class quan_huyen(osv.osv):
    _name = "quan.huyen"
    _columns = {
        'name': fields.char('Quận (huyện)',size = 50, required = True),
        'tinh_thanh_id':fields.many2one('tinh.tp','Thuộc Tỉnh/Thành phố', required = True),
                }
quan_huyen()
class khu_pho(osv.osv):
    _name = "khu.pho"
    _columns = {
        'name': fields.char('Khu phố (ấp)',size = 50, required = True),
        'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)', required = True),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)', required = True),
                }
khu_pho()
class chu_dau_tu(osv.osv):
    _name = "chu.dau.tu"
    _columns = {
        'name': fields.char('Tên chủ đầu tư',size = 1024, required = True),
        'dien_thoai': fields.char('Điện thoại',size = 50),
        'so_nha': fields.char('Số nhà',size = 50),
#         'ngay_cap': fields.date('Thời gian cấp', required = True),
        'tinh_tp_id': fields.many2one( 'tinh.tp','Tỉnh/TP', required = True),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)', required = True),
        'khu_pho_id': fields.many2one('khu.pho','Khu phố (ấp)', required = True),
        'quan_huyen_id': fields.many2one('quan.huyen','Quận (huyện)', required = True),
                }
chu_dau_tu()
class van_ban(osv.osv):
    _name = "van.ban"
    _columns = {
        'name': fields.char('Số',size = 1024, required = True),
        'noi_dung': fields.text('Nội dung'),
                }
van_ban()
class nguon_von(osv.osv):
    _name = "nguon.von"
    _columns = {
        'name': fields.char('Tên',size = 1024, required = True),
                }
nguon_von()

class doi_tac(osv.osv):
    _name = "doi.tac"
    _columns = {
        'name': fields.char('Tên',size = 1024, required = True),
        'so_nha': fields.char('Số nhà',size = 50),
        'tinh_tp_id': fields.many2one('tinh.tp','Tỉnh/TP'),
        'phuong_xa_id': fields.many2one('phuong.xa','Phường (xã)'),
        'khu_pho_id': fields.many2one('khu.pho','Khu phố (ấp)'),
        'quan_huyen_id': fields.many2one('quan.huyen','Quận (huyện)'),
        'dien_thoai': fields.char('Điện thoại',size = 50),
        'fax': fields.char('Fax',size = 50),
        'hoso_id': fields.many2one('hoso.nangluc','Hồ sơ năng lực'),
        'giang_vien_ids': fields.many2many('gv.hv', 'giangvien_donvi_ref', 'donvi_id', 'giangvien_id', 'Giảng viên'),
        'doanh_nghiep': fields.boolean('Doanh Nghiệp'),
        'dv_dtao': fields.boolean('Đơn vị đào tạo'),
        'dia_chi': fields.char('Địa chỉ',size = 1024),
        'tt_dk': fields.char('Thông tin đăng ký',size = 1024),
        'nganh_lq': fields.char('Ngành nghề liên quan',size = 1024),
        'du_an': fields.char('Các dự án, mua sắm thường xuyên',size = 1024),
        'mo_hinh': fields.char('Mô hình tổ chức',size = 1024),
        'kn_tr_khai': fields.char('Kinh nghiệm triển khai',size = 1024),
        'dtac_khang': fields.char('Danh sách đối tác, khách hàng lớn',size = 1024),
        'san_pham': fields.char('Danh mục các sản phẩm cung cấp, phân phối chính',size = 1024),
        'cdo_csach': fields.char('Chế độ, chính sách của doanh nghiệp',size = 1024),
        'lat': fields.float(u'Vĩ độ', digits=(9, 6)),
        'lng': fields.float(u'Kinh độ', digits=(9, 6)),
        'radius': fields.float(u'Radius', digits=(9, 16)),
        'map': fields.dummy(),
        'points': fields.text('Points'), 
        'mo_ta': fields.text('Mo ta'),
                }
doi_tac()

# class can_bo(osv.osv):
#     _name = "can.bo"
#     _inherit = ['mail.thread', 'ir.needaction_mixin']
#     _description = "Can Bo"
#     _columns = {
#         'name': fields.char('Họ và Tên',size = 1024, required = True, track_visibility='onchange'),
#         'co_quan': fields.char('Cơ quan',size = 1024, track_visibility='onchange'),
#         'chuc_vu': fields.char('Chức vụ',size = 1024, track_visibility='onchange'),
#         'td_cntt': fields.char('Trình độ CNTT',size = 1024, track_visibility='onchange'),
#         'td_av': fields.char('Trình độ anh văn',size = 1024, track_visibility='onchange'),
#         'cc_cntt': fields.char('Chứng chỉ CNTT',size = 1024),
#         'qt_thamgia': fields.char('Quá trình tham gia các lớp CNTT',size = 1024, track_visibility='onchange'),
#         'hoi_thao': fields.char('Quá trình tham gia hội thảo',size = 1024, track_visibility='onchange'),
#         'ghi_nhan': fields.char('Ghi nhận',size = 1024, track_visibility='onchange'),
#         'user_account_id': fields.many2one('res.users', 'Tài khoản', track_visibility='onchange'),
#         'history_line': fields.one2many('can.bo','history_id','Lịch sử',readonly = True),
#         'history_id': fields.many2one('can.bo','Chi tiết lịch sử', ondelete='cascade'),
#                 }
# can_bo()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
