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
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
