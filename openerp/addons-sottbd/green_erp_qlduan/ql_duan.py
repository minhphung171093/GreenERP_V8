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

class du_an(osv.osv):
    _name = "du.an"
    _columns = {
        'name': fields.char('Tên dự án',size = 1024, required = True),
        'chu_dau_tu_id': fields.many2one('chu.dau.tu','Chủ đầu tư', required = True),
        'tong_dau_tu':fields.float('Tổng mức đầu tư'),
        'tong_du_toan':fields.float('Tổng dự toán'),
#         'nguon_von_id': fields.many2one('nguon.von','Nguồn vốn', required = True),
        'tg_thuchien': fields.char('Thời gian thực hiện',size = 1024),
        'giai_ngan':fields.float('Ước tính giải ngân trong năm'),
        'tre_han': fields.char('Cảnh báo trễ hạn',size = 1024),
        'du_an_line':fields.one2many('du.an.line','duan_id','Du an line'),
        'state':fields.selection([('moi_tao', 'Đang lập dự án'),
                                  ('thuc_hien', 'Đang thực hiện'),
                                  ('hoan_thanh', 'Hoàn thành'),
                                  ('huy', 'Huỷ'),
                                  ('treo', 'Treo')],'Trạng thái', readonly=True),
                }
    _defaults={
        'state':'moi_tao',       
               }
du_an()
class du_an_line(osv.osv):
    _name = "du.an.line"
    _columns = {
        'name': fields.char('Tên',size = 50, required = True),
        'duan_id': fields.many2one( 'du.an','Dự án'),
        'van_ban_id': fields.many2one('van.ban','Văn bản'),
        'state':fields.selection([('moi_tao', 'Mới tạo'),
                                  ('cho_duyet', 'Chờ duyệt'),
                                  ('duyet', 'Duyệt'),
                                ],'Status', readonly=True),
                }
    _defaults={
    'state':'moi_tao',       
           }
    def bt_cho_duyet(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cho_duyet'})
    def bt_duyet(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'duyet'})
du_an_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
