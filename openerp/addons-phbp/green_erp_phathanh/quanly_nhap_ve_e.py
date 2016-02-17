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

class nhap_ve_e(osv.osv):
    _name = "nhap.ve.e"
    _columns = {
        'ky_ve_id': fields.many2one('ky.ve','Kỳ vé',required = True),
        'loai_ve_id': fields.many2one('loai.ve','Loại vé',required = True),
        'ngay_mo_thuong': fields.date('Ngày mở thưởng',required = True),
        'nhap_ve_e_line': fields.one2many('nhap.ve.e.line','nhap_ve_e_id','Nhap ve e line'),
                }
nhap_ve_e()

class nhap_ve_e_line(osv.osv):
    _name = "nhap.ve.e.line"
    
    def _thieu_thua(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for tg in self.browse(cr,uid,ids):
            if tg.thuc_kiem>tg.ve_e_theo_bangke:
                res[tg.id]['kiem_dem_thua']=tg.thuc_kiem-tg.ve_e_theo_bangke
            elif tg.thuc_kiem<tg.ve_e_theo_bangke:
                res[tg.id]['kiem_dem_thieu']=tg.ve_e_theo_bangke - tg.thuc_kiem
        return res
    
    _columns = {
        'nhap_ve_e_id': fields.many2one('nhap.ve.e','Nhập vế ế', ondelete='cascade'),
        'ten_daily': fields.char('Tên Đại Lý',size = 1024, required = True),
        'daily_id': fields.many2one('dai.ly','Đại lý', required = True),
        'diem_tra_e_id': fields.many2one('khu.vuc','Mã điểm trả ế', required = True),
        'ma_khu_vuc': fields.char('Mã Khu Vực',size = 1024, required = True),
        've_e_theo_bangke': fields.float('Số vé ế theo bảng kê'),
        'thuc_kiem': fields.float('Thực kiểm'),
        'kiem_dem_thieu':fields.function(_thieu_thua, string='Kiểm đếm (Thiếu)',
                                    type='float', store={
                                                'nhap.ve.e.line':(lambda self, cr, uid, ids, c={}: ids, ['ve_e_theo_bangke','thuc_kiem'], 10),
                                            }),
        'kiem_dem_thua':fields.function(_thieu_thua, string='Kiểm đếm (Thừa)',
                                    type='float', store={
                                                'nhap.ve.e.line':(lambda self, cr, uid, ids, c={}: ids, ['ve_e_theo_bangke','thuc_kiem'], 10),
                                            }),
        'ghi_chu':fields.char('Tên Đại Lý',size = 1024),
                }
    def onchange_daily_id(self, cr, uid, ids, daily_id=False, gan_cho_ids=False):
        vals = {}
        if daily_id :
            daily = self.pool.get('dai.ly').browse(cr,uid,daily_id)
            vals = {'ten_daily':daily.ten,
                    'ma_khu_vuc':daily.tinh_tp_id.name,
                }
        return {'value': vals}  
nhap_ve_e_line()


class hethong_dambao_attp(osv.osv):
    _name = "hethong.dambao.attp"
    _columns = {
        'name': fields.char('Hệ thống đảm bảo ATTP',size = 1024, required = True),
                }
hethong_dambao_attp()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
