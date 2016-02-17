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
    
    def onchange_previous_phanphoi(self, cr, uid, ids, ky_ve_id=False, loai_ve_id=False):
        vals = {}
        phanphoi_ids = []
        mang = []
        if ky_ve_id and loai_ve_id:
            sql = '''
                select id from phanphoi_truyenthong where loai_ve_id = %s 
                order by create_date desc limit 1
            '''%(loai_ve_id)
            cr.execute(sql)
            phanphoi_ids = [r[0] for r in cr.fetchall()]
            if phanphoi_ids:
                pp = self.browse(cr,uid,phanphoi_ids[0])   
                for line in pp.phanphoi_tt_line:
                    mang.append((0,0,{
                                      'daily_id': line.daily_id.id,
                                      'ten_daily': line.ten_daily,
                                      'socay_kytruoc': line.socay_kynay,
                                      'sove_kytruoc': line.sove_kynay,
                                      }))
                                 
                vals = {'phanphoi_tt_line':mang,
                    }
        return {'value': vals} 
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
    
    def onchange_daily_id(self, cr, uid, ids, daily_id=False):
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
            res[tg.id] = {
                'kiem_dem_thua': 0.0,
                'kiem_dem_thieu': 0.0,
            }
            if tg.thuc_kiem>tg.ve_e_theo_bangke:
                res[tg.id]['kiem_dem_thua']=tg.thuc_kiem-tg.ve_e_theo_bangke
            if tg.thuc_kiem<tg.ve_e_theo_bangke:
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
        'kiem_dem_thieu':fields.function(_thieu_thua, string='Kiểm đếm (Thiếu)',multi='sums',
                                    type='float', store={
                                                'nhap.ve.e.line':(lambda self, cr, uid, ids, c={}: ids, ['ve_e_theo_bangke','thuc_kiem'], 10),
                                            }),
        'kiem_dem_thua':fields.function(_thieu_thua, string='Kiểm đếm (Thừa)',multi='sums',
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
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
