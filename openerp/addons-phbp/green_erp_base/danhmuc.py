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

class dai_ly(osv.osv):
    _name = "dai.ly"
    _columns = {
        'name': fields.char('Mã Đại Lý',size = 1024, required = True),
        'ten': fields.char('Tên Đại Lý',size = 1024, required = True),
        'tinh_tp_id': fields.many2one( 'tinh.tp','Tỉnh/Thành Phố', required = True),
#         'khu_vuc_id': fields.many2one( 'khu.vuc','Thuộc khu vực', required = True),
        'lat': fields.float(u'Latitude', digits=(9, 6)),
        'lng': fields.float(u'Longitude', digits=(9, 6)),
        'radius': fields.float(u'Radius', digits=(9, 16)),
        'map': fields.dummy(),
        'points': fields.text('Points'), 
        'mo_ta': fields.text('Mo ta'),
                }
    
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        reads = self.read(cr, uid, ids, ['name','ten'], context)
   
        for record in reads:
            name = record['name'] + '-' +'['+record['ten']+']'
            res.append((record['id'], name))
        return res  
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_dai_ly'):
            if context.get('ky_ve_id') and context.get('loai_ve_id'):
                sql = '''
                    select daily_id from phanphoi_tt_line
                    where phanphoi_tt_id in (select id from phanphoi_truyenthong where ky_ve_id = %s and loai_ve_id = %s)
                '''%(context.get('ky_ve_id'), context.get('loai_ve_id'))
                cr.execute(sql)
                dai_ly_ids = [row[0] for row in cr.fetchall()]
                args += [('id','in',dai_ly_ids)]
            if not context.get('ky_ve_id') or not context.get('loai_ve_id'):
                dai_ly_ids = False
                args += [('id','in',dai_ly_ids)]
        return super(dai_ly, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
   
    def write_radius(self, cr, uid, id,active_model, vals, context=None):
        if vals.get('radius',False) and active_model=='rp.google.map':
            gg_map_obj = self.pool.get('rp.google.map')
            line = gg_map_obj.browse(cr, uid, int(id))
            vals.update(gg_map_obj.onchange_toado_bankinh( cr, uid, [], line.lat, line.lng, vals['radius'],context)['value'])
            gg_map_obj.write(cr, uid, [int(id)], vals, context)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
         
    def write_center(self, cr, uid, id,active_model, vals, context=None):
        if vals.get('center',False) and active_model=='rp.google.map':
            gg_map_obj = self.pool.get('rp.google.map')
            line = gg_map_obj.browse(cr, uid, int(id))
            vals.update(gg_map_obj.onchange_toado_bankinh( cr, uid, [], vals['center']['lat'], vals['center']['lng'], line.radius,context)['value'])
            vals.update({'lat':vals['center']['lat'],'lng':vals['center']['lng']})
            gg_map_obj.write(cr, uid, [int(id)], vals, context)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
     
    def haversine(self,lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        km = 6367 * c
        return km
    
dai_ly()

class khu_vuc(osv.osv):
    _name = "khu.vuc"
    _columns = {
        'name': fields.char('Mã Điểm trả ế',size = 1024, required = True),
        'ten': fields.char('Tên Điểm trả ế',size = 1024, required = True),
                }
khu_vuc()


# class quan_huyen(osv.osv):
#     _name = "quan.huyen"
#     _columns = {
#         'name': fields.char('Quận (huyện)',size = 1024, required = True),
#         'tinh_thanh_id':fields.many2one('tinh.tp','Thuộc Tỉnh/Thành phố', required = True),
#                 }
# quan_huyen()

class ky_ve(osv.osv):
    _name = "ky.ve"
    _columns = {
        'name': fields.char('Mã kỳ vé',size = 1024, required = True),
        'ngay_mo_thuong':fields.date('Ngày mở thưởng', required = True)
                }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_baocao_kyve'):
            sql = '''
                select id from ky_ve
                where id in (select ky_ve_id from phanphoi_truyenthong)
            '''
            cr.execute(sql)
            ky_ve_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',ky_ve_ids)]
        if context.get('search_ky_ve'):
            sql = '''
                select id from ky_ve
                where id not in (select ky_ve_id from phanphoi_truyenthong where ky_ve_id is not null)
            '''
            cr.execute(sql)
            ky_ve_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',ky_ve_ids)]
        if context.get('search_ky_ve_dieuchinh'):
            sql = '''
                select id from ky_ve
                where id in (select ky_ve_id from phanphoi_truyenthong)
            '''
            cr.execute(sql)
            ky_ve_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',ky_ve_ids)]
        if context.get('search_ky_ve_e'):
            sql = '''
                select id from ky_ve
                where id not in (select ky_ve_id from nhap_ve_e where ky_ve_id is not null) and id in (select ky_ve_id from phanphoi_truyenthong)
            '''
            cr.execute(sql)
            ky_ve_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',ky_ve_ids)]
        return super(ky_ve, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
ky_ve()

class loai_ve(osv.osv):
    _name = "loai.ve"
    _columns = {
        'name': fields.char('Loại vé',size = 1024, required = True),
        'gia_tri': fields.float('Gía trị', required = True),
                }
loai_ve()

class phan_loai(osv.osv):
    _name = "phan.loai"
    _columns = {
        'name': fields.char('Tên loại',size = 1024, required = True),
                }
phan_loai()

class loai_hinh(osv.osv):
    _name = "loai.hinh"
    _columns = {
        'name': fields.char('Tên',size = 1024, required = True),
        'doanh_thu': fields.selection([('xs','Xổ số'), ('ks','Khách sạn')], 'Doanh thu', required = True),
        'loai_hinh_line': fields.one2many('loai.hinh.line','loai_hinh_id','Loai hinh line'),
                }
#     def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
#         if context is None:
#             context = {}
#         if context.get('search_dai_ly'):
#             if context.get('ky_ve_id') and context.get('loai_ve_id'):
#                 sql = '''
#                     select daily_id from phanphoi_tt_line
#                     where phanphoi_tt_id in (select id from phanphoi_truyenthong where ky_ve_id = %s and loai_ve_id = %s)
#                 '''%(context.get('ky_ve_id'), context.get('loai_ve_id'))
#                 cr.execute(sql)
#                 dai_ly_ids = [row[0] for row in cr.fetchall()]
#                 args += [('id','in',dai_ly_ids)]
#         return super(dai_ly, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
#     def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
#        ids = self.search(cr, user, args, context=context, limit=limit)
#        return self.name_get(cr, user, ids, context=context)
loai_hinh()
class loai_hinh_line(osv.osv):
    _name = "loai.hinh.line"
    _columns = {
        'name': fields.char('Tên',size = 1024, required = True),
        'is_ty_le': fields.boolean('Có tính tỉ lệ'),
        'loai_hinh_id': fields.many2one('loai.hinh','Loại hình',ondelete="cascade"),
                }
loai_hinh_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
