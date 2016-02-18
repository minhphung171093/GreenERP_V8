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
        'tang_giam':fields.function(_tang_giam, string='Tăng, giảm (cây)',multi='sums',
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

class dieuchinh_phanphoi_ve(osv.osv):
    _name = "dieuchinh.phanphoi.ve"
    
    def _get_dieuchinh(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('dieuchinh.line').browse(cr, uid, ids, context=context):
            result[line.dieuchinh_id.id] = True
        return result.keys()
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        reads = self.read(cr, uid, ids, ['ky_ve_id'], context)
   
        for record in reads:
            name = (record['ky_ve_id'] or '')
            res.append((record['id'], name))
        return res   
    def amount_all(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for dc in self.browse(cr,uid,ids,context=context):
            res[dc.id] = {
                'tong_ve_pp': 0.0,
                'tong_ve_dc': 0.0,
                'tong_ve_sau_dc': 0.0,
            }
#             sql = '''
#                 select case when sum(sove_kynay)!=0 then sum(sove_kynay) else 0 end tong_ve_pp
#                 from phanphoi_tt_line where phanphoi_tt_id in (select id from phanphoi_truyenthong where ky_ve_id)
#             '''
            val1 = 0
            val2 = 0
            for line in dc.dieuchinh_line:
                val1 += line.sove_duocduyet
                val2 += line.sove_dc
            res[dc.id]['tong_ve_pp'] = val1
            res[dc.id]['tong_ve_dc'] = val2
            res[dc.id]['tong_ve_sau_dc'] = val1+val2
        return res
    
    _columns = {
        'ky_ve_id': fields.many2one('ky.ve','Kỳ vé',required = True),
        'loai_ve_id': fields.many2one('loai.ve','Loại vé',required = True),
        'ngay_ph': fields.date('Ngày phát hành',required = True),
        'dieuchinh_line': fields.one2many('dieuchinh.line','dieuchinh_id','Dieu Chinh line'),
        'tong_ve_pp': fields.function(amount_all, multi='sums',string='Tổng vé phân phối',
                                         store={
                'dieuchinh.phanphoi.ve': (lambda self, cr, uid, ids, c={}: ids, ['dieuchinh_line'], 10),
                'dieuchinh.line': (_get_dieuchinh, ['price_unit', 'sub_total', 'product_uom_qty', 'freight'], 10)}),
        'tong_ve_dc': fields.function(amount_all, multi='sums',string='Tổng vé điều chỉnh',
                                      store={
                'dieuchinh.phanphoi.ve': (lambda self, cr, uid, ids, c={}: ids, ['dieuchinh_line'], 10),
                'dieuchinh.line': (_get_dieuchinh, ['price_unit', 'sub_total', 'product_uom_qty', 'freight'], 10)}),
        'tong_ve_sau_dc': fields.function(amount_all, multi='sums',string='Tổng vé sau điều chỉnh',
                                        store={
                'dieuchinh.phanphoi.ve': (lambda self, cr, uid, ids, c={}: ids, ['dieuchinh_line'], 10),
                'dieuchinh.line': (_get_dieuchinh, ['price_unit', 'sub_total', 'product_uom_qty', 'freight'], 10)}),
                }
    
    def onchange_ky_ve(self, cr, uid, ids, ky_ve_id=False):
        vals = {}
        phanphoi_ids = []
        mang = []
        if ky_ve_id:
            sql = '''
                select ngay_ph from phanphoi_truyenthong where ky_ve_id = %s
            '''%(ky_ve_id)
            cr.execute(sql)
            ngay_ph = cr.fetchone()
            vals = {'ngay_ph':ngay_ph[0],
                }
        return {'value': vals} 
dieuchinh_phanphoi_ve()

class dieuchinh_line(osv.osv):
    _name = "dieuchinh.line"
    
    def _total_ve(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for dc in self.browse(cr,uid,ids):
            res[dc.id]=dc.sove_duocduyet+dc.sove_dc
        return res
    
    _columns = {
        'dieuchinh_id': fields.many2one('dieuchinh.phanphoi.ve','Dieu chinh phan phoi', ondelete='cascade'),
        'ten_daily': fields.char('Tên Đại Lý',size = 1024),
        'daily_id': fields.many2one('dai.ly','Đại lý'),
        'phanphoi_line_id': fields.many2one('phanphoi.tt.line','Phan Phoi Line'),
        'sove_duocduyet': fields.float('Số vé được duyệt', readonly=True),
        'sove_dc': fields.float('Số vé điều chỉnh'),
        'sove_sau_dc':fields.function(_total_ve, string='Tổng số vé sau điều chỉnh',multi='sums',
                                    type='float', store={
                                                'dieuchinh.line':(lambda self, cr, uid, ids, c={}: ids, ['sove_duocduyet','sove_dc'], 10),
                                            }),
                }
    
    def onchange_daily_id(self, cr, uid, ids, daily_id=False):
        vals = {}
        if daily_id :
            daily = self.pool.get('dai.ly').browse(cr,uid,daily_id)
            vals = {'ten_daily':daily.ten,
                }
        return {'value': vals}  
    
    
dieuchinh_line()

class nhap_ve_e(osv.osv):
    _name = "nhap.ve.e"
    _columns = {
        'ky_ve_id': fields.many2one('ky.ve','Kỳ vé',required = True),
        'loai_ve_id': fields.many2one('loai.ve','Loại vé',required = True),
        'ngay_mo_thuong': fields.date('Ngày mở thưởng'),
        'nhap_ve_e_line': fields.one2many('nhap.ve.e.line','nhap_ve_e_id','Nhap ve e line'),
                }
    def onchange_ky_ve_id(self, cr, uid, ids, ky_ve_id=False):
        vals = {}
        if ky_ve_id :
            ky_ve = self.pool.get('ky.ve').browse(cr,uid,ky_ve_id)
            vals = {'ngay_mo_thuong':ky_ve.ngay_mo_thuong,
                }
        return {'value': vals}  
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

class kh_in_ve_tt(osv.osv):
    _name = "kh.in.ve.tt"

    def _tinh_tong_so_ve_in(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for tg in self.browse(cr,uid,ids):
#             res[tg.id] = {
#                 'tong_so_ve_in': 0.0,
#             }
            val1=0
            for line in tg.kh_in_ve_tt_line:
                val1+=line.sl_ve_in
            res[tg.id]=val1    
        return res
    def _tinh_tong_so_dot_in(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for tg in self.browse(cr,uid,ids):
            sql='''
                select COUNT(id) from kh_in_ve_tt_line where kh_in_ve_tt_id=%s
            '''%(tg.id)
            cr.execute(sql)
            val1 = cr.fetchone()[0]
            res[tg.id]=val1    
        return res
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('kh.in.ve.tt.line').browse(cr, uid, ids, context=context):
            result[line.kh_in_ve_tt_id.id] = True
        return result.keys()
    _columns = {
        'name':fields.char('Tháng',size = 2,required=True),
        'year':fields.char('Năm',size = 4,required=True),
        'sl_in_moi_dot':fields.char('Số lượng vé in mỗi đợt',size = 1024),
        'loai_ve_id': fields.many2one('loai.ve','Loại vé',required = True),
        'tong_so_ve_in':fields.function(_tinh_tong_so_ve_in, string='Tổng số vé in trong tháng',
                                    type='integer', store={
                                                'kh.in.ve.tt': (lambda self, cr, uid, ids, c={}: ids, ['kh_in_ve_tt_line'], 10),         
                                                'kh.in.ve.tt.line':(_get_order, ['sl_ve_in'], 10),
                                            }),
        'tong_so_dot_in':fields.function(_tinh_tong_so_dot_in, string='Tổng số đợt in',
                                    type='integer', store={
                                                'kh.in.ve.tt': (lambda self, cr, uid, ids, c={}: ids, ['kh_in_ve_tt_line'], 10),         
                                                'kh.in.ve.tt.line':(_get_order, [], 10),
                                            }),
        'kich_co':fields.char('Kích cỡ',size = 1024),
        'kh_in_ve_tt_line': fields.one2many('kh.in.ve.tt.line','kh_in_ve_tt_id','Nhap ve e line'),
                }
kh_in_ve_tt()
class kh_in_ve_tt_line(osv.osv):
    _name = "kh.in.ve.tt.line"
    _columns = {
        'kh_in_ve_tt_id': fields.many2one('kh.in.ve.tt','Kế hoạch in tt', ondelete='cascade'),
        'ky_ve_id': fields.many2one('ky.ve','Kỳ vé',required = True),
        'ngay_mo_thuong': fields.date('Ngày mở số'),
        'ngay_nhan': fields.date('Ngày nhận',required = True),
        'sl_ve_in': fields.integer('Số lượng vé in (vé)'),
                }
    def onchange_ky_ve_id(self, cr, uid, ids, ky_ve_id=False):
        vals = {}
        if ky_ve_id :
            ky_ve = self.pool.get('ky.ve').browse(cr,uid,ky_ve_id)
            vals = {'ngay_mo_thuong':ky_ve.ngay_mo_thuong,
                }
        return {'value': vals}  
kh_in_ve_tt_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
