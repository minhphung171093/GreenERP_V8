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

class product_template(osv.osv):
    _inherit = "product.template"
    _columns = {
                'nguon_goc': fields.char('Nguồn gốc',size=1024),
                'tt_ct': fields.char('Thông tin chi tiết',size=1024),
                'nha_cc_id': fields.many2one('nha.cc','Nhà cung cấp'),
                'xuat_xu': fields.char('Xuất xứ',size=1024),
                'muc_dich': fields.char('Mục đích sử dụng',size=1024),
                'tg_bhanh': fields.char('Thời gian bảo hành',size=1024),
                'tg_khauhao': fields.char('Thời gian khấu hao',size=1024),
                'tg_tly': fields.char('Thời gian thanh lý',size=1024),
                'vong_doi': fields.text('Thông tin vòng đời sản phẩm'),
                'uu_tien': fields.boolean('Ưu tiên mua sắm'),
                
    }
    
product_template

class nha_cc(osv.osv):
    _name = "nha.cc"
    _columns = {
        'name': fields.char('Nhà cung cấp',required=True),
                }

nha_cc()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
