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

class tinh_tp(osv.osv):
    _name = "tinh.tp"
    _columns = {
        'name': fields.char('Mã Tỉnh/Thành Phố',size = 1024, required = True),
        'ten': fields.char('Tên Tỉnh/Thành Phố',size = 1024, required = True),
                }
tinh_tp()

class dai_ly(osv.osv):
    _name = "dai.ly"
    _columns = {
        'name': fields.char('Mã Đại Lý',size = 1024, required = True),
        'ten': fields.char('Tên Đại Lý',size = 1024, required = True),
        'tinh_tp_id': fields.many2one( 'tinh.tp','Tỉnh/Thành Phố', required = True),
        'khu_vuc_id': fields.many2one( 'khu.vuc','Thuộc khu vực', required = True),
                }
dai_ly()

class khu_vuc(osv.osv):
    _name = "khu.vuc"
    _columns = {
        'name': fields.char('Mã Khu Vực',size = 1024, required = True),
                }
khu_vuc()
class quan_huyen(osv.osv):
    _name = "quan.huyen"
    _columns = {
        'name': fields.char('Quận (huyện)',size = 1024, required = True),
        'tinh_thanh_id':fields.many2one('tinh.tp','Thuộc Tỉnh/Thành phố', required = True),
                }
quan_huyen()

class tieu_chi(osv.osv):
    _name = "tieu.chi"
    _columns = {
        'name': fields.char('Tên tiêu chí',size = 1024, required = True),
                }
tieu_chi()

class coquan_quanly(osv.osv):
    _name = "coquan.quanly"
    _columns = {
        'name': fields.char('Tên cơ quan quản lý',size = 1024, required = True),
                }
coquan_quanly()

class phan_loai(osv.osv):
    _name = "phan.loai"
    _columns = {
        'name': fields.char('Tên loại',size = 1024, required = True),
                }
phan_loai()

class hethong_dambao_attp(osv.osv):
    _name = "hethong.dambao.attp"
    _columns = {
        'name': fields.char('Hệ thống đảm bảo ATTP',size = 1024, required = True),
                }
hethong_dambao_attp()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
