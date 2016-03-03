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
                    sql = '''
                        select sove_sau_dc from dieuchinh_line where phanphoi_line_id = %s
                    '''%(line.id)
                    cr.execute(sql)
                    ve_dc = cr.fetchone()
                    if ve_dc:
                        ve_kytruoc = ve_dc[0]
                    else:
                        ve_kytruoc = line.sove_kynay
                    mang.append((0,0,{
                                      'daily_id': line.daily_id.id,
                                      'ten_daily': line.ten_daily,
                                      'socay_kytruoc': line.socay_kynay,
                                      'sove_kytruoc': ve_kytruoc,
                                      'phanphoi_line_kytruoc_id': line.id,
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
            res[tg.id]=tg.socay_kynay-tg.socay_kytruoc
        return res
    
    _columns = {
        'phanphoi_tt_id': fields.many2one('phanphoi.truyenthong','Phân phối truyền thống', ondelete='cascade'),
        'ten_daily': fields.char('Tên Đại Lý',size = 1024, required = True),
        'daily_id': fields.many2one('dai.ly','Đại lý', required = True),
        'socay_kytruoc': fields.float('Số cây kỳ trước',digits=(16,0)),
        'sove_kytruoc': fields.float('Số vé kỳ trước',digits=(16,0)),
        'socay_kynay': fields.float('Số cây kỳ này',digits=(16,0)),
        'sove_kynay': fields.float('Số vé kỳ này',digits=(16,0)),
        'phanphoi_line_kytruoc_id': fields.many2one('phanphoi.tt.line','Phan phoi line ky truoc'),
        'tang_giam':fields.function(_tang_giam, string='Tăng, giảm (cây)', digits=(16,0),
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
    
    def _check_daily_id(self, cr, uid, ids, context=None):
        for dl in self.browse(cr, uid, ids, context=context):
            dl_ids = self.search(cr,uid,[('id','!=',dl.id),('daily_id','=',dl.daily_id.id),('phanphoi_tt_id','=',dl.phanphoi_tt_id.id)])
            if dl_ids:
                return False
#                 raise osv.except_osv(_('Warning!'),_('Bạn không được chọn trùng đại lý trong cùng một kỳ vé!'))
        return True
         
    _constraints = [
        (_check_daily_id, 'Bạn không được chọn trùng đại lý trong cùng một kỳ vé!', ['daily_id']),
    ]
    
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
                'tong_ve_pp': 0,
                'tong_ve_dc': 0,
                'tong_ve_sau_dc': 0,
            }
            val1 = 0
            val2 = 0
            for line in dc.dieuchinh_line:
                val1 += line.sove_duocduyet
                val2 += line.sove_dc
            res[dc.id]['tong_ve_pp'] = val1
            res[dc.id]['tong_ve_dc'] = val2
            res[dc.id]['tong_ve_sau_dc'] = val1+val2
        return res
    
    def total_amount_all(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for dc in self.browse(cr,uid,ids,context=context):
            res[dc.id] = {
                'total_ve_pp': 0,
                'total_ve_dc': 0,
                'total_ve_sau_dc': 0,
            }
            sql = '''
                select case when sum(sove_kynay)!=0 then sum(sove_kynay) else 0 end tong_ve_pp
                from phanphoi_tt_line where phanphoi_tt_id in (select id from phanphoi_truyenthong where ky_ve_id=%s and loai_ve_id=%s and ngay_ph='%s')
            '''%(dc.ky_ve_id.id, dc.loai_ve_id.id, dc.ngay_ph)
            cr.execute(sql)
            val1 = cr.fetchone()[0]
            val2 = 0
            for line in dc.dieuchinh_line:
                val2 += line.sove_dc
            res[dc.id]['total_ve_pp'] = val1
            res[dc.id]['total_ve_dc'] = val2
            res[dc.id]['total_ve_sau_dc'] = val1+val2
        return res
    
    _columns = {
        'ky_ve_id': fields.many2one('ky.ve','Kỳ vé',required = True),
        'loai_ve_id': fields.many2one('loai.ve','Loại vé',required = True),
        'ngay_ph': fields.date('Ngày phát hành',required = True),
        'ngay_dc': fields.date('Ngày điều chỉnh',required = True),
        'dieuchinh_line': fields.one2many('dieuchinh.line','dieuchinh_id','Dieu Chinh line'),
        'tong_ve_pp': fields.function(amount_all, multi='sums',string='Tổng số vé được duyệt',type='float',digits=(16,0),
                                         store={
                'dieuchinh.phanphoi.ve': (lambda self, cr, uid, ids, c={}: ids, ['dieuchinh_line'], 10),
                'dieuchinh.line': (_get_dieuchinh, ['sove_duocduyet', 'sove_dc'], 10)}),
        'tong_ve_dc': fields.function(amount_all, multi='sums',string='Tổng số vé điều chỉnh',type='float',digits=(16,0),
                                      store={
                'dieuchinh.phanphoi.ve': (lambda self, cr, uid, ids, c={}: ids, ['dieuchinh_line'], 10),
                'dieuchinh.line': (_get_dieuchinh, ['sove_duocduyet', 'sove_dc'], 10)}),
        'tong_ve_sau_dc': fields.function(amount_all, multi='sums',string='Tổng số vé sau điều chỉnh',type='float',digits=(16,0),
                                        store={
                'dieuchinh.phanphoi.ve': (lambda self, cr, uid, ids, c={}: ids, ['dieuchinh_line'], 10),
                'dieuchinh.line': (_get_dieuchinh, ['sove_duocduyet', 'sove_dc'], 10)}),
                
        'total_ve_pp': fields.function(total_amount_all, multi='sums',string='Tổng số vé phân phối theo KH',type='float',digits=(16,0),
                                         store=True),
        'total_ve_dc': fields.function(total_amount_all, multi='sums',string='Số vé điều chỉnh so với kế hoạch',type='float',digits=(16,0),
                                      store=True),
        'total_ve_sau_dc': fields.function(total_amount_all, multi='sums',string='Tổng số vé sau điều chỉnh',type='float',digits=(16,0),
                                        store=True),
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
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
#         for line in self.browse(cr, uid, ids, context=context):
#             context.update({'active_ids': [line.id]})
        datas = {'ids': ids}
        datas['model'] = 'dieuchinh.phanphoi.ve'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'dieuchinh_kehoach_pp_ve_report', 'datas': datas}
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
        'daily_id': fields.many2one('dai.ly','Đại lý', required = True),
        'phanphoi_line_id': fields.many2one('phanphoi.tt.line','Phan Phoi Line'),
        'sove_duocduyet': fields.float('Số vé được duyệt', readonly=True,digits=(16,0)),
        'sove_dc': fields.float('Số vé điều chỉnh',digits=(16,0)),
        'sove_sau_dc':fields.function(_total_ve, string='Số vé sau điều chỉnh',digits=(16,0),
                                    type='float', store={
                                                'dieuchinh.line':(lambda self, cr, uid, ids, c={}: ids, ['sove_duocduyet','sove_dc'], 10),
                                            }),
                }
    
    def _check_daily_id(self, cr, uid, ids, context=None):
        for dl in self.browse(cr, uid, ids, context=context):
            dl_ids = self.search(cr,uid,[('id','!=',dl.id),('daily_id','=',dl.daily_id.id),('dieuchinh_id','=',dl.dieuchinh_id.id)])
            if dl_ids:
                return False
#                 raise osv.except_osv(_('Warning!'),_('Bạn không được chọn trùng đại lý trong cùng một kỳ vé!'))
        return True
         
    _constraints = [
        (_check_daily_id, 'Bạn không được chọn trùng đại lý trong cùng một kỳ vé!', ['daily_id']),
    ]
    
    def onchange_daily_dc_id(self, cr, uid, ids, daily_id=False, ky_ve_id=False):
        vals = {}
        if daily_id and ky_ve_id:
            daily = self.pool.get('dai.ly').browse(cr,uid,daily_id)
            sql = '''
                select sove_kynay,id from phanphoi_tt_line where daily_id = %s and phanphoi_tt_id in (select id from phanphoi_truyenthong where ky_ve_id = %s)
            '''%(daily_id, ky_ve_id)
            cr.execute(sql)
            ve = cr.fetchone()
            vals = {'ten_daily':daily.ten,
                    'sove_duocduyet': ve[0],
                    'phanphoi_line_id': ve[1],
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
#     def _check_sl_ve_e(self, cr, uid, ids, context=None):
#         for sl in self.browse(cr, uid, ids, context=context):
#             val1 = 0
#             val2 = 0
#             sql='''
#                 select sove_sau_dc from dieuchinh_line where daily_id=%s 
#                     and dieuchinh_id in (select id from dieuchinh_phanphoi_ve where ky_ve_id = %s and loai_ve_id = %s)
#             '''%(sl.daily_id.id,sl.nhap_ve_e_id.ky_ve_id.id,sl.nhap_ve_e_id.loai_ve_id.id)
#             cr.execute(sql)
#             val1 = cr.fetchone()
#             if val1:
#                 sql='''
#                     select sum(ve_e_theo_bangke) as tong_ve_e from nhap_ve_e_line where daily_id=%s 
#                         and nhap_ve_e_id in (select id from nhap_ve_e where ky_ve_id = %s and loai_ve_id = %s)
#                 '''%(sl.daily_id.id,sl.nhap_ve_e_id.ky_ve_id.id,sl.nhap_ve_e_id.loai_ve_id.id)
#                 cr.execute(sql)
#                 val2 = cr.fetchone()
#                 if val2 and val1<val2:
#                     raise osv.except_osv(_('Warning!'),_(' Tổng số lượng vé ế nhập vào không được lớn hơn số lượng vé đã được điều chỉnh !'))
#                     return False
#         return True
#         
#     _constraints = [
#         (_check_sl_ve_e, 'Identical Data', []),
#     ]  
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
        've_e_theo_bangke': fields.float('Số vé ế theo bảng kê',digits=(16,0)),
        'thuc_kiem': fields.float('Thực kiểm',digits=(16,0)),
        'phanphoi_line_id': fields.many2one('phanphoi.tt.line','Phan Phoi Line'),
        'kiem_dem_thieu':fields.function(_thieu_thua, string='Kiểm đếm (Thiếu)',multi='sums',digits=(16,0),
                                    type='float', store={
                                                'nhap.ve.e.line':(lambda self, cr, uid, ids, c={}: ids, ['ve_e_theo_bangke','thuc_kiem'], 10),
                                            }),
        'kiem_dem_thua':fields.function(_thieu_thua, string='Kiểm đếm (Thừa)',multi='sums',digits=(16,0),
                                    type='float', store={
                                                'nhap.ve.e.line':(lambda self, cr, uid, ids, c={}: ids, ['ve_e_theo_bangke','thuc_kiem'], 10),
                                            }),
        'ghi_chu':fields.char('Ghi chú',size = 1024),
                }
    
    def _check_ve_e_theo_bangke(self, cr, uid, ids, context=None):
        for sl in self.browse(cr, uid, ids, context=context):
            pp = 0
            dieu_chinh = 0
            ve_e = 0
            sql='''
                select sove_sau_dc from dieuchinh_line where daily_id=%s 
                    and dieuchinh_id in (select id from dieuchinh_phanphoi_ve where ky_ve_id = %s and loai_ve_id = %s)
            '''%(sl.daily_id.id,sl.nhap_ve_e_id.ky_ve_id.id,sl.nhap_ve_e_id.loai_ve_id.id)
            cr.execute(sql)
            dieu_chinh = cr.fetchone()
            if dieu_chinh > 0:
                sql='''
                    select sum(ve_e_theo_bangke) as tong_ve_e from nhap_ve_e_line where daily_id=%s 
                        and nhap_ve_e_id in (select id from nhap_ve_e where ky_ve_id = %s and loai_ve_id = %s)
                '''%(sl.daily_id.id,sl.nhap_ve_e_id.ky_ve_id.id,sl.nhap_ve_e_id.loai_ve_id.id)
                cr.execute(sql)
                ve_e = cr.fetchone()
                if ve_e and dieu_chinh<ve_e:
                    raise osv.except_osv(_('Cảnh Báo!'),_(' Tổng số lượng vé ế nhập vào không được lớn hơn số lượng vé đã được điều chỉnh của đại lý %s !')%(sl.daily_id.name,))
                    return False
            else:
                sql='''
                    select sove_kynay from phanphoi_tt_line where daily_id=%s 
                        and phanphoi_tt_id in (select id from phanphoi_truyenthong where ky_ve_id = %s and loai_ve_id = %s)
                '''%(sl.daily_id.id,sl.nhap_ve_e_id.ky_ve_id.id,sl.nhap_ve_e_id.loai_ve_id.id)
                cr.execute(sql)
                pp = cr.fetchone()
                if pp > 0:
                    sql='''
                        select sum(ve_e_theo_bangke) as tong_ve_e from nhap_ve_e_line where daily_id=%s 
                            and nhap_ve_e_id in (select id from nhap_ve_e where ky_ve_id = %s and loai_ve_id = %s)
                    '''%(sl.daily_id.id,sl.nhap_ve_e_id.ky_ve_id.id,sl.nhap_ve_e_id.loai_ve_id.id)
                    cr.execute(sql)
                    ve_e = cr.fetchone()
                    if ve_e and pp<ve_e:
                        raise osv.except_osv(_('Cảnh Báo!'),_(' Tổng số lượng vé ế nhập vào không được lớn hơn số lượng vé đã được phân phối của đại lý %s !')%(sl.daily_id.name,))
                        return False
        return True
         
    _constraints = [
        (_check_ve_e_theo_bangke, '', ['ve_e_theo_bangke']),
    ]     
    def onchange_daily_id(self, cr, uid, ids, daily_id=False, ky_ve_id=False):
        vals = {}
        if daily_id and ky_ve_id:
            daily = self.pool.get('dai.ly').browse(cr,uid,daily_id)
            sql = '''
                select id from phanphoi_tt_line where daily_id = %s and phanphoi_tt_id in (select id from phanphoi_truyenthong where ky_ve_id = %s)
            '''%(daily_id, ky_ve_id)
            cr.execute(sql)
            ve = cr.fetchone()
            vals = {'ten_daily':daily.ten,
                    'ma_khu_vuc':daily.tinh_tp_id.name,
                    'phanphoi_line_id': ve[0],
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
        'tong_so_ve_in':fields.function(_tinh_tong_so_ve_in, string='Tổng số vé in trong tháng',digits=(16,0),
                                    type='float', store={
                                                'kh.in.ve.tt': (lambda self, cr, uid, ids, c={}: ids, ['kh_in_ve_tt_line'], 10),         
                                                'kh.in.ve.tt.line':(_get_order, ['sl_ve_in'], 10),
                                            }),
        'tong_so_dot_in':fields.function(_tinh_tong_so_dot_in, string='Tổng số đợt in',digits=(16,0),
                                    type='float', store={
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
        'sl_ve_in': fields.float('Số lượng vé in (vé)',digits=(16,0)),
                }
    def onchange_ky_ve_id(self, cr, uid, ids, ky_ve_id=False):
        vals = {}
        if ky_ve_id :
            ky_ve = self.pool.get('ky.ve').browse(cr,uid,ky_ve_id)
            vals = {'ngay_mo_thuong':ky_ve.ngay_mo_thuong,
                }
        return {'value': vals}  
kh_in_ve_tt_line()

# class kh_in_ve_tu_chon(osv.osv):
#     _name = "kh.in.ve.tu.chon"
# 
# #     def _tinh_tong_so_ve_in(self, cr, uid, ids, name, arg, context=None):
# #         res = {}
# #         for tg in self.browse(cr,uid,ids):
# # #             res[tg.id] = {
# # #                 'tong_so_ve_in': 0.0,
# # #             }
# #             val1=0
# #             for line in tg.kh_in_ve_tt_line:
# #                 val1+=line.sl_ve_in
# #             res[tg.id]=val1    
# #         return res
# #     def _tinh_tong_so_dot_in(self, cr, uid, ids, name, arg, context=None):
# #         res = {}
# #         for tg in self.browse(cr,uid,ids):
# #             sql='''
# #                 select COUNT(id) from kh_in_ve_tt_line where kh_in_ve_tt_id=%s
# #             '''%(tg.id)
# #             cr.execute(sql)
# #             val1 = cr.fetchone()[0]
# #             res[tg.id]=val1    
# #         return res
# #     def _get_order(self, cr, uid, ids, context=None):
# #         result = {}
# #         for line in self.pool.get('kh.in.ve.tt.line').browse(cr, uid, ids, context=context):
# #             result[line.kh_in_ve_tt_id.id] = True
# #         return result.keys()
#     _columns = {
#         'name':fields.char('Đợt',size = 2,required=True),
#         'year':fields.char('Năm',size = 4,required=True),
#         'thoigian_giaohang': fields.date('Thời gian giao hàng',required = True),
#         'noi_dung_khac':fields.char('Các nội dung khác',size = 1024),
#         
#         'kh_in_ve_tu_chon_line': fields.one2many('kh.in.ve.tu.chon.line','kh_in_ve_tu_chon_id','Nhap ve e line'),
#                 }
# kh_in_ve_tu_chon()
# class kh_in_ve_tu_chon_line(osv.osv):
#     _name = "kh.in.ve.tu.chon.line"
#     _columns = {
#         'kh_in_ve_tu_chon_id': fields.many2one('kh.in.ve.tt','Kế hoạch in tt', ondelete='cascade'),
#         'loai_ve_id': fields.many2one('loai.ve','Mệnh giá',required = True),
#         'ky_hieu': fields.char('Ký hiệu',size = 1024,required=True),
#         'seri': fields.char('Ký hiệu',size = 1024),
#         'so_luong': fields.float('Số lượng đặt in',digits=(16,0)),
#                 }
# 
# kh_in_ve_tu_chon_line()

class doanhthu_theo_loaihinh(osv.osv):
    _name = "doanhthu.theo.loaihinh"
    _columns = {
        'year': fields.selection([(num, str(num)) for num in range(2013, 2050)], 'Năm', required = True),
        'loai_hinh_id': fields.many2one('loai.hinh','Loại hình',required = True),
        'dt_theo_loaihinh_line': fields.one2many('dt.theo.loaihinh.line','doanh_thu_id','Doanh thu line'),
                }
    def onchange_loai_hinh_id(self, cr, uid, ids, loai_hinh_id=False):
        vals = {}
        dt_line = []
        if loai_hinh_id:
            loai_hinh = self.pool.get('loai.hinh').browse(cr,uid,loai_hinh_id)
            for line in loai_hinh.loai_hinh_line:
                dt_line.append((0,0,{
                                     'chi_tieu_id':line.id,
                                     }))
            vals = {'dt_theo_loaihinh_line':dt_line,
                }
        return {'value': vals}  
doanhthu_theo_loaihinh()

class dt_theo_loaihinh_line(osv.osv):
    _name = "dt.theo.loaihinh.line"
    
    def _ty_le(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            val1=''
            val2=''
            res[line.id] = {
                'tyle': 0,
                'tyle_phandau': 0,
            }
            if line.chi_tieu_id.is_ty_le == True:
                val1 = float(line.thuchien_namtruoc) and float(line.kehoach_namnay)*100/float(line.thuchien_namtruoc) or 0
                val1 = round(val1,0)
                val2 = float(line.thuchien_namtruoc) and float(line.phan_dau)*100/float(line.thuchien_namtruoc) or 0
                val2 = round(val2,0)
            res[line.id]['tyle'] = val1
            res[line.id]['tyle_phandau'] = val2
        return res
    _columns = {
        'doanh_thu_id': fields.many2one('doanhthu.theo.loaihinh','Chi tiết', ondelete='cascade'),
        'chi_tieu_id': fields.many2one('loai.hinh.line','Chỉ tiêu', required = True),
        'kehoach_namtruoc': fields.float('Kế hoạch năm trước',digits=(16,0)),
        'thuchien_namtruoc': fields.float('Thực hiện năm trước',digits=(16,0)),
        'kehoach_namnay': fields.float('Kế hoạch năm nay',digits=(16,0)),
#         'tyle': fields.float('Tỷ lệ so thực hiện năm trước'),
        'tyle':fields.function(_ty_le, string='Tỷ lệ so thực hiện năm trước(%)', type='char',
                                    multi='sums'),
        'phan_dau': fields.float('Kế hoạch phấn đấu năm nay',digits=(16,0)),
#         'tyle_phandau': fields.float('Tỷ lệ so thực hiện năm trước'),
        'tyle_phandau':fields.function(_ty_le, string='Tỷ lệ so thực hiện năm trước(%)', type='char',
                                    multi='sums'),
                }
    
dt_theo_loaihinh_line()

class nhap_ve(osv.osv):
    _name = "nhap.ve"
    _columns = {
        'name':fields.char('Đợt',size = 64,required=True),
        'ngay_nhap': fields.date('Ngày nhập',required = True),
#         'thoigian_giaohang': fields.date('Thời gian giao hàng',required = True),
        'noi_dung_khac':fields.char('Các nội dung khác',size = 1024),
        'nhap_ve_line': fields.one2many('nhap.ve.line','nhap_ve_id','Nhap ve line'),
                }
nhap_ve()
class nhap_ve_line(osv.osv):
    _name = "nhap.ve.line"
    _columns = {
        'nhap_ve_id': fields.many2one('nhap.ve','Nhập vé', ondelete='cascade'),
        'loai_ve_id': fields.many2one('loai.ve','Loại vé',required = True),
        'thanh_tien': fields.float('Thành tiền',readonly=True,digits=(16,0)),
        'so_luong': fields.float('Số lượng',digits=(16,0)),
        'ky_hieu': fields.char('Ký hiệu',size = 1024,required=True),
        'seri': fields.char('Seri',size = 1024),
                }
    def onchange_thanh_tien(self, cr, uid, ids, loai_ve_id=False,so_luong=False):
        vals = {}
        dt_line = []
        if loai_ve_id and so_luong:
            loai_ve = self.pool.get('loai.ve').browse(cr,uid,loai_ve_id)
            thanh_tien = loai_ve.gia_tri * so_luong
            vals = {'thanh_tien':thanh_tien,
                }
        return {'value': vals}  
nhap_ve_line()

class xuat_ve(osv.osv):
    _name = "xuat.ve"
    _columns = {
        'name': fields.date('Ngày xuất',required = True),
        'xuat_ve_line': fields.one2many('xuat.ve.line','xuat_ve_id','Xuat ve line'),
                }
xuat_ve()
class xuat_ve_line(osv.osv):
    _name = "xuat.ve.line"
    _columns = {
        'xuat_ve_id': fields.many2one('xuat.ve','Xuất vé', ondelete='cascade'),
        'loai_ve_id': fields.many2one('loai.ve','Loại vé',required = True),
        'thanh_tien': fields.float('Thành tiền',readonly=True,digits=(16,0)),
        'so_luong': fields.float('Số lượng',digits=(16,0)),
                }
    def onchange_thanh_tien(self, cr, uid, ids, loai_ve_id=False,so_luong=False):
        vals = {}
        dt_line = []
        if loai_ve_id and so_luong:
            loai_ve = self.pool.get('loai.ve').browse(cr,uid,loai_ve_id)
            thanh_tien = loai_ve.gia_tri * so_luong
            vals = {'thanh_tien':thanh_tien,
                }
        return {'value': vals}  
xuat_ve_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
