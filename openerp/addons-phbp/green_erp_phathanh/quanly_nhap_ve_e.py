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

class phanphoi_truyenthong(osv.osv):
    _name = "phanphoi.truyenthong"
    _columns = {
        'ky_ve_id': fields.many2one('ky.ve','Kỳ vé',required = True),
        'loai_ve_id': fields.many2one('loai.ve','Loại vé',required = True),
        'ngay_ph': fields.date('Ngày phát hành',required = True),
        'phanphoi_tt_line': fields.one2many('phanphoi.tt.line','phanphoi_tt_id','Phan phoi line'),
                }
phanphoi_truyenthong()

class phanphoi_tt_line(osv.osv):
    _name = "phanphoi.tt.line"
    
    def _tang_giam(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for tg in self.browse(cr,uid,ids):
            res[tg.id]=tg.socay_kytruoc-tg.socay_kynay
        return res
    
    _columns = {
        'phanphoi_tt_id': fields.many2one('phanphoi.truyenthong','Phân phối truyền thống', ondelete='cascade'),
        'ten_daily': fields.char('Tên Đại Lý',size = 1024, required = True),
        'daily_id': fields.many2one('dai.ly','Đại lý', required = True),
        'socay_kytruoc': fields.float('Số cây kỳ trước'),
        'sove_kytruoc': fields.float('Số vé kỳ trước'),
        'socay_kynay': fields.float('Số cây kỳ này'),
        'sove_kynay': fields.float('Số vé kỳ này'),
        'tang_giam':fields.function(_tang_giam, string='Tăng, giảm (cây)',
                                    type='float', store={
                                                'phanphoi.tt.line':(lambda self, cr, uid, ids, c={}: ids, ['socay_kytruoc','socay_kynay'], 10),
                                            }),
                }
    def onchange_daily_id(self, cr, uid, ids, daily_id=False, gan_cho_ids=False):
        vals = {}
        if daily_id :
            daily = self.pool.get('dai.ly').browse(cr,uid,daily_id)
            vals = {'ten_daily':daily.ten,
                }
        return {'value': vals}  
phanphoi_tt_line()


class hethong_dambao_attp(osv.osv):
    _name = "hethong.dambao.attp"
    _columns = {
        'name': fields.char('Hệ thống đảm bảo ATTP',size = 1024, required = True),
                }
hethong_dambao_attp()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
