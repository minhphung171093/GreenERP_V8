# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from mmap import mmap,ACCESS_READ
from openerp.addons.xlrd import open_workbook

import os
from openerp import modules
base_path = os.path.dirname(modules.get_module_path('ql_duan_dautu'))

class cocau_dautu(osv.osv):
    _name = "cocau.dautu"
    _description = "Co cau dau tu"
    
    _columns = {
        'name' :fields.char('Tên', size=128, required=True),
    }
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_duan_dautu/data/CoCauDauTu.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    val0 = s.cell(row,0).value
                    danhmuc_ids = self.search(cr, 1, [('name','=',val0)])
                    if not danhmuc_ids:
                        self.create(cr, 1, {'name': val0})
cocau_dautu()

class duan_danhmuc(osv.osv):
    _name = "duan.danhmuc"
    _description = "Danh Muc Du An"
    _order = "stt"
    
    _columns = {
        'name' :fields.char('Danh Muc', size=128, required=True),
        'stt' : fields.char('STT', size=64, required=True),
        'danhmuc_cha': fields.many2one('duan.danhmuc', 'Thuộc Danh Mục Cha'),
    }
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_duan_dautu/data/DanhMucDuAn.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    val0 = s.cell(row,0).value
                    val1 = s.cell(row,1).value
                    val2 = s.cell(row,2).value
                    danhmuc_ids = self.search(cr, 1, [('name','=',val1)])
                    if not danhmuc_ids:
                        danhmuc_cha_ids = self.search(cr, 1, [('name','=',val2)])
                        if danhmuc_cha_ids:
                            self.create(cr, 1, {'name': val1,'stt':val0,'danhmuc_cha':danhmuc_cha_ids[0]})
                        else:
                            self.create(cr, 1, {'name': val1,'stt':val0})
duan_danhmuc()

class duan_nhom(osv.osv):
    _name = "duan.nhom"
    _description = "Nhom Du An"
    
    _columns = {
        'name' :fields.char('Tên nhóm', size=128, required=True),
    }
    
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_duan_dautu/data/NhomDuAn.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    val0 = s.cell(row,0).value
                    nhom_ids = self.search(cr, 1, [('name','=',val0)])
                    if not nhom_ids:
                        self.create(cr, 1, {'name': val0})
duan_nhom()

class duan_nanglucthietke(osv.osv):
    _name = "duan.nanglucthietke"
    _description = "Nang Luc Thiet Ke"
    
    _columns = {
        'name' :fields.char('Tên', size=128, required=True),
    }
    
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_duan_dautu/data/NangLucThietKe.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    val0 = s.cell(row,0).value
                    nanglucthietke_ids = self.search(cr, 1, [('name','=',val0)])
                    if not nanglucthietke_ids:
                        self.create(cr, 1, {'name': val0})
    
duan_nanglucthietke()

class duan_giaidoan(osv.osv):
    _name = "duan.giaidoan"
    _description = "Du An Giai Doan"
    _order = 'stt'
    _columns = {
        'name' :fields.char('Tên', size=128, required=True),
        'stt': fields.integer('STT', required=True),
        'giaidoan_cha': fields.many2one('duan.giaidoan', 'Thuộc giai đoạn cha'),
    }
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_duan_dautu/data/GiaiDoanDuAn.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    val0 = s.cell(row,0).value
                    val1 = s.cell(row,1).value
                    val2 = s.cell(row,2).value
                    giaidoan_ids = self.search(cr, 1, [('name','=',val1)])
                    if not giaidoan_ids:
                        giaidoan_cha_ids = self.search(cr, 1, [('name','=',val2)])
                        if giaidoan_cha_ids:
                            self.create(cr, 1, {'stt': val0,'name':val1,'giaidoan_cha':giaidoan_cha_ids[0]})
                        else:
                            self.create(cr, 1, {'stt': val0,'name':val1})
duan_giaidoan()

class danhmuc_nguonvon(osv.osv):
    _name = "danhmuc.nguonvon"
    _description = "Nguon Von"
    
    def _amount_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        duan_dautu_thuchien_obj = self.pool.get('duan.dautu.thuchien')
        kehoach_thuchien_obj = self.pool.get('kehoach.thuchien')
        for nguonvon in self.browse(cr, uid, ids, context=context):
            res[nguonvon.id] = {
                'kehoach_daunam': 0.0,
                'kehoach_dieuchinh': 0.0,
                'kehoach_dieuhoa': 0.0,
                'sotien_conlai': 0.0,
            }
            kehoach_daunam = 0.0
            kehoach_dieuchinh = 0.0
            kehoach_dieuhoa = 0.0
            vondi = 0.0
            vonden = 0.0
            nguon_von_ids = self.pool.get('nguon.von').search(cr, uid, [('id','=',nguonvon.nguon_von_id.id)])
            duan_dautu_thuchien_ids = duan_dautu_thuchien_obj.search(cr, uid, [('nam','=',nguonvon.nam)])
            for duan_dautu_thuchien in duan_dautu_thuchien_obj.browse(cr, uid, duan_dautu_thuchien_ids):
#                 
#                 for thuchien in duan_dautu_thuchien.kehoach_thuchien_lines:
#                     if thuchien.nguonvon_id.id in nguon_von_ids:
#                         kehoach_daunam += thuchien.sotien
                
                kehoach_thuchien_ids = kehoach_thuchien_obj.search(cr, uid, [('duan_dautu_thuchien_id','=',duan_dautu_thuchien.id)])
                for kehoach_thuchien in kehoach_thuchien_obj.browse(cr,uid,kehoach_thuchien_ids):
                    if kehoach_thuchien.nguonvon_id.id in nguon_von_ids:
                        kehoach_dieuchinh += kehoach_thuchien.sotien
                
                sql = '''
                    select * from kehoach_dieuchinh where duan_dautu_thuchien_id =%s and name = 0
                '''%(duan_dautu_thuchien.id)
                cr.execute(sql)
                kehoach_dieuchinh_ids = [row[0] for row in cr.fetchall()]
                if kehoach_dieuchinh_ids:
                    for line in self.pool.get('kehoach.dieuchinh').browse(cr, uid, kehoach_dieuchinh_ids):
                        for dieuchinh in line.kehoach_thuchien_line:
                            if dieuchinh.nguonvon_id.id in nguon_von_ids:
                                kehoach_daunam += dieuchinh.sotien
                else:
                    kehoach_thuchien_ids = kehoach_thuchien_obj.search(cr, uid, [('duan_dautu_thuchien_id','=',duan_dautu_thuchien.id)])
                    for kehoach_thuchien in kehoach_thuchien_obj.browse(cr,uid,kehoach_thuchien_ids):
                        if kehoach_thuchien.nguonvon_id.id in nguon_von_ids:
                            kehoach_daunam += kehoach_thuchien.sotien
                
                for line in duan_dautu_thuchien.chuyenvon_den_duan_khac_lines:
                    if line.nguonvon_id.id in nguon_von_ids:
                        vondi += line.sotien
                        
                for line in duan_dautu_thuchien.von_den_tu_duan_khac_lines:
                    if line.nguonvon_id.id in nguon_von_ids:
                        vonden += line.sotien
                
                sql = '''
                    select * from kehoach_dieuchinh where duan_dautu_thuchien_id =%s and name in (select max(name) from kehoach_dieuchinh where duan_dautu_thuchien_id =%s)
                '''%(duan_dautu_thuchien.id,duan_dautu_thuchien.id)
                cr.execute(sql)
                kehoach_dieuchinh_ids = [row[0] for row in cr.fetchall()]
                for line in self.pool.get('kehoach.dieuchinh').browse(cr, uid, kehoach_dieuchinh_ids):
                    for dieuchinh in line.kehoach_thuchien_line:
                        if dieuchinh.nguonvon_id.id in nguon_von_ids:
                            kehoach_dieuhoa += dieuchinh.sotien
                
            res[nguonvon.id]['kehoach_daunam'] = kehoach_daunam
            res[nguonvon.id]['kehoach_dieuchinh'] = kehoach_dieuchinh + vonden - vondi
            res[nguonvon.id]['kehoach_dieuhoa'] = kehoach_dieuhoa  + vonden - vondi
            res[nguonvon.id]['sotien_conlai'] = nguonvon.sotien - res[nguonvon.id]['kehoach_dieuchinh']
        return res
    
    def _get_kehoach_thuchien(self, cr, uid, ids, context=None):
        result = {}
        duan_dautu_thuchien_obj = self.pool.get('duan.dautu.thuchien')
        for line in self.browse(cr, uid, ids, context=context):
            duan_dautu_thuchien_ids = duan_dautu_thuchien_obj.search(cr, uid, [('id','=',line.duan_dautu_thuchien_id.id)])
            for duan_dautu_thuchien in duan_dautu_thuchien_obj.browse(cr, uid, duan_dautu_thuchien_ids, context=context):
                danhmuc_nguonvon_ids = self.pool.get('danhmuc.nguonvon').search(cr, uid, [('nguon_von_id','=',line.nguonvon_id.id),('nam','=',duan_dautu_thuchien.nam)])
                for danhmuc_nguonvon in danhmuc_nguonvon_ids:
                    result[danhmuc_nguonvon] = True
        return result.keys()
    
    def _get_duan_dautu_thuchien(self, cr, uid, ids, context=None):
        result = {}
        danhmuc_nguonvon_obj = self.pool.get('danhmuc.nguonvon')
        kehoach_thuchien_obj = self.pool.get('kehoach.thuchien')
        for duan_dautu_thuchien in self.browse(cr, uid, ids):
            kehoach_thuchien_ids = kehoach_thuchien_obj.search(cr, uid, [('duan_dautu_thuchien_id','=',duan_dautu_thuchien.id)])
            for kehoach_thuchien in kehoach_thuchien_obj.browse(cr, uid, kehoach_thuchien_ids):
                danhmuc_nguonvon_ids = danhmuc_nguonvon_obj.search(cr, uid, [('nam','=',duan_dautu_thuchien.nam),('nguon_von_id','=',kehoach_thuchien.nguonvon_id.id)])
                for line in danhmuc_nguonvon_ids:
                    result[line] = True
        return result.keys()
    
    def _get_chuyenvon_den_duan_khac(self, cr, uid, ids, context=None):
        result = {}
        duan_dautu_thuchien_obj = self.pool.get('duan.dautu.thuchien')
        for line in self.browse(cr, uid, ids, context=context):
            duan_dautu_thuchien_ids = duan_dautu_thuchien_obj.search(cr, uid, [('id','=',line.duan_thuhien_id.id)])
            for duan_dautu_thuchien in duan_dautu_thuchien_obj.browse(cr, uid, duan_dautu_thuchien_ids, context=context):
                danhmuc_nguonvon_ids = self.pool.get('danhmuc.nguonvon').search(cr, uid, [('nguon_von_id','=',line.nguonvon_id.id),('nam','=',duan_dautu_thuchien.nam)])
                for danhmuc_nguonvon in danhmuc_nguonvon_ids:
                    result[danhmuc_nguonvon] = True
        return result.keys()
    
    def _get_duan_dautu(self, cr, uid, ids, context=None):
        result = {}
        duan_dautu_thuchien_obj = self.pool.get('duan.dautu.thuchien')
        danhmuc_nguonvon_obj = self.pool.get('danhmuc.nguonvon')
        kehoach_thuchien_obj = self.pool.get('kehoach.thuchien')
        for duan_dautu in self.browse(cr, uid, ids):
            duan_dautu_thuchien_ids = duan_dautu_thuchien_obj.search(cr, uid, [('duan_dautu_id','=',duan_dautu.id)])
            for duan_dautu_thuchien in duan_dautu_thuchien_obj.browse(cr, uid, duan_dautu_thuchien_ids):
                kehoach_thuchien_ids = kehoach_thuchien_obj.search(cr, uid, [('duan_dautu_thuchien_id','=',duan_dautu_thuchien.id)])
                for kehoach_thuchien in kehoach_thuchien_obj.browse(cr, uid, kehoach_thuchien_ids):
                    danhmuc_nguonvon_ids = danhmuc_nguonvon_obj.search(cr, uid, [('nam','=',duan_dautu_thuchien.nam),('nguon_von_id','=',kehoach_thuchien.nguonvon_id.id)])
                    for line in danhmuc_nguonvon_ids:
                        result[line] = True
        return result.keys()
    
    _columns = {
        'nguon_von_id' :fields.many2one('nguon.von','Nguồn vốn ', required=True, ondelete='cascade', readonly=True, states={'moi': [('readonly', False)]}),
        'nguoithuchien_id': fields.many2one('hr.employee', 'Người thực hiện', required=False, states={'moi': [('readonly', False)]}),
        'ngaybatdau' :fields.date('Ngày bắt đầu', required=True, readonly=True, states={'moi': [('readonly', False)]}),
        'ngayketthuc' :fields.date('Ngày kết thúc', required=True, readonly=True, states={'moi': [('readonly', False)]}),
        'nam': fields.char('Năm', size=5, required=True),
        
        'sotien': fields.float('Tổng nguồn', digits=(16,0), required=True, readonly=True, states={'moi': [('readonly', False)]}),
        
        
        'kehoach_daunam': fields.function(_amount_total, string='Kế hoạch đầu năm', digits=(16,0),
                store={
                    'danhmuc.nguonvon': (lambda self, cr, uid, ids, c={}: ids, ['sotien'], 10),
                    'kehoach.thuchien': (_get_kehoach_thuchien, ['sotien','nguonvon_id'], 20),
#                     'kehoach.dieuchinh': (_get_kehoach_thuchien, ['kehoach_thuchien_line'], 20),
                    'duan.dautu.thuchien': (_get_duan_dautu_thuchien, ['kehoach_thuchien_lines','duan_dautu_id'], 20),
                    'duan.dautu': (_get_duan_dautu, ['ke_hoach_von'], 20),
                   },
                                          multi='sums'),
        'kehoach_dieuchinh': fields.function(_amount_total, string='Kế hoạch đã duyệt (kỳ gần nhất)', digits=(16,0),
                store={
                    'danhmuc.nguonvon': (lambda self, cr, uid, ids, c={}: ids, ['sotien'], 10),
                    'kehoach.thuchien': (_get_kehoach_thuchien, ['sotien','nguonvon_id'], 30),
#                     'kehoach.dieuchinh': (_get_kehoach_thuchien, ['kehoach_thuchien_line'], 20),
                    'duan.dautu.thuchien': (_get_duan_dautu_thuchien, ['kehoach_dieuchinh_line','duan_dautu_id'], 30),
                    'duan.dautu': (_get_duan_dautu, ['ke_hoach_von'], 30),
                   },
                                             multi='sums'),
        'kehoach_dieuhoa': fields.function(_amount_total, string='Kế hoạch cập nhật', digits=(16,0),
                store={
                    'danhmuc.nguonvon': (lambda self, cr, uid, ids, c={}: ids, ['sotien'], 10),
                    'kehoach.thuchien': (_get_kehoach_thuchien, ['sotien','nguonvon_id'], 20),
#                     'kehoach.dieuchinh': (_get_kehoach_thuchien, ['kehoach_thuchien_line'], 20),
                    'duan.dautu.thuchien': (_get_duan_dautu_thuchien, ['kehoach_thuchien_lines','duan_dautu_id','chuyenvon_den_duan_khac_lines','von_den_tu_duan_khac_lines','kehoach_dieuchinh_line'], 20),
                    'duan.dautu': (_get_duan_dautu, ['ke_hoach_von'], 20),
#                     'chuyenvon.den.duan.khac': (_get_chuyenvon_den_duan_khac, ['sotien','duan_thuhien_den_id'], 10),
                   },
                                           multi='sums'),
        'sotien_conlai': fields.function(_amount_total, string='Số tiền còn lại', digits=(16,0),
                store={
                    'danhmuc.nguonvon': (lambda self, cr, uid, ids, c={}: ids, ['sotien'], 10),
                    'kehoach.thuchien': (_get_kehoach_thuchien, ['sotien','nguonvon_id'], 20),
#                     'kehoach.dieuchinh': (_get_kehoach_thuchien, ['kehoach_thuchien_line'], 20),
                    'duan.dautu.thuchien': (_get_duan_dautu_thuchien, ['kehoach_thuchien_lines','duan_dautu_id','chuyenvon_den_duan_khac_lines','von_den_tu_duan_khac_lines','kehoach_dieuchinh_line'], 20),
                    'duan.dautu': (_get_duan_dautu, ['ke_hoach_von'], 20),
                   },
                                         multi='sums'),
                
        'currency_id': fields.many2one('res.currency', 'Tiền Tệ'),
        
        'ghichu': fields.text('Ghi chú'),
        'state': fields.selection([
            ('moi', 'Mới tạo'),
            ('dangsudung', 'Đang sử dụng'),
            ('hoanthanh', 'Đã hoàn thành'),
            ], 'Status', readonly=True)
    }
    
    def _default_employee(self, cr, uid, context=None):
        emp_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)], context=context)
        return emp_ids and emp_ids[0] or False
    
    def _get_default_currency(self, cr, uid, context=None):
        currency_ids = self.pool.get('res.currency').search(cr, uid, [('name','=','VND')], context=context)
        return currency_ids and currency_ids[0] or False
    
    _defaults = {
         'state': 'moi',
         'ngaybatdau': time.strftime('%Y-01-01'),
         'ngayketthuc': time.strftime('%Y-12-31'),
         'nguoithuchien_id': _default_employee,
         'currency_id': _get_default_currency,
         'nam': time.strftime('%Y'),
     }
    
#     def _check_nam(self, cr, uid, ids):
#         for danhmuc_nguonvon in self.browse(cr, uid, ids):
#             danhmuc_nguonvon_ids = self.search(cr, uid, [('id','<>',danhmuc_nguonvon.id), ('nam', '=',danhmuc_nguonvon.name)])
#             if danhmuc_nguonvon_ids:
#                 return False
#         return True
#     _constraints = [
#         (_check_nam, '!', ['Năm']),
#     ]
    
danhmuc_nguonvon()

class nguon_von(osv.osv):
    _name = "nguon.von"
    _description = "Nguon Von"
    
    def _amount_total(self, cr, uid, ids, field_name, arg, context=None):
        context = context or {}
        res = {}
        for nguonvon in self.browse(cr, uid, ids, context=context):
            res[nguonvon.id] = {
                'sotien': 0.0,
                'kehoach_daunam': 0.0,
                'kehoach_dieuchinh': 0.0,
                'kehoach_dieuhoa': 0.0,
                'sotien_conlai': 0.0,
            }
            nam = context.get('nam_nguonvon',False) or time.strftime('%Y')
            kehoach_daunam = 0.0
            sotien = 0.0
            kehoach_dieuchinh = 0.0
            kehoach_dieuhoa = 0.0
            sotien_conlai = 0.0
            for danhmuc_nguonvon in nguonvon.danhmuc_nguonvon_lines:
                if danhmuc_nguonvon.nam == nam:
                    sotien += danhmuc_nguonvon.sotien
                    kehoach_daunam += danhmuc_nguonvon.kehoach_daunam
                    kehoach_dieuchinh += danhmuc_nguonvon.kehoach_dieuchinh
                    kehoach_dieuhoa += danhmuc_nguonvon.kehoach_dieuhoa
                    sotien_conlai += danhmuc_nguonvon.sotien_conlai
            res[nguonvon.id]['sotien'] = sotien
            res[nguonvon.id]['kehoach_daunam'] = kehoach_daunam
            res[nguonvon.id]['kehoach_dieuchinh'] = kehoach_dieuchinh
            res[nguonvon.id]['kehoach_dieuhoa'] = kehoach_dieuhoa
            res[nguonvon.id]['sotien_conlai'] = sotien_conlai
        return res
    
    def _get_danhmuc_nguonvon(self, cr, uid, ids, context=None):
        result = {}
        duan_dautu_thuchien_obj = self.pool.get('duan.dautu.thuchien')
        for line in self.browse(cr, uid, ids, context=context):
            result[line.nguon_von_id.id] = True
        return result.keys()
    
    def _get_kehoach_thuchien(self, cr, uid, ids, context=None):
        result = {}
        duan_dautu_thuchien_obj = self.pool.get('duan.dautu.thuchien')
        danhmuc_nguonvon_obj = self.pool.get('danhmuc.nguonvon')
        for kehoach_thuchien in self.browse(cr, uid, ids):
            duan_dautu_thuchien_ids = duan_dautu_thuchien_obj.search(cr, uid, [('id','=',kehoach_thuchien.duan_dautu_thuchien_id.id)])
            for duan_thuchien in duan_dautu_thuchien_obj.browse(cr, uid, duan_dautu_thuchien_ids):
                danhmuc_nguonvon_ids = danhmuc_nguonvon_obj.search(cr, uid, [('nam','=',duan_thuchien.nam),('nguon_von_id','=',kehoach_thuchien.nguonvon_id.id)])
                for line in danhmuc_nguonvon_obj.browse(cr, uid, danhmuc_nguonvon_ids):
                    result[line.nguon_von_id.id] = True
        return result.keys()
    
    def _get_duan_dautu_thuchien(self, cr, uid, ids, context=None):
        result = {}
        danhmuc_nguonvon_obj = self.pool.get('danhmuc.nguonvon')
        kehoach_thuchien_obj = self.pool.get('kehoach.thuchien')
        for duan_dautu_thuchien in self.browse(cr, uid, ids):
            kehoach_thuchien_ids = kehoach_thuchien_obj.search(cr, uid, [('duan_dautu_thuchien_id','=',duan_dautu_thuchien.id)])
            for kehoach_thuchien in kehoach_thuchien_obj.browse(cr, uid, kehoach_thuchien_ids):
                danhmuc_nguonvon_ids = danhmuc_nguonvon_obj.search(cr, uid, [('nam','=',duan_dautu_thuchien.nam),('nguon_von_id','=',kehoach_thuchien.nguonvon_id.id)])
                for line in danhmuc_nguonvon_obj.browse(cr, uid, danhmuc_nguonvon_ids):
                    result[line.nguon_von_id.id] = True
        return result.keys()
    
    def _get_duan_dautu(self, cr, uid, ids, context=None):
        result = {}
        duan_dautu_thuchien_obj = self.pool.get('duan.dautu.thuchien')
        danhmuc_nguonvon_obj = self.pool.get('danhmuc.nguonvon')
        kehoach_thuchien_obj = self.pool.get('kehoach.thuchien')
        for duan_dautu in self.browse(cr, uid, ids):
            duan_dautu_thuchien_ids = duan_dautu_thuchien_obj.search(cr, uid, [('duan_dautu_id','=',duan_dautu.id)])
            for duan_dautu_thuchien in duan_dautu_thuchien_obj.browse(cr, uid, duan_dautu_thuchien_ids):
                kehoach_thuchien_ids = kehoach_thuchien_obj.search(cr, uid, [('duan_dautu_thuchien_id','=',duan_dautu_thuchien.id)])
                for kehoach_thuchien in kehoach_thuchien_obj.browse(cr, uid, kehoach_thuchien_ids):
                    danhmuc_nguonvon_ids = danhmuc_nguonvon_obj.search(cr, uid, [('nam','=',duan_dautu_thuchien.nam),('nguon_von_id','=',kehoach_thuchien.nguonvon_id.id)])
                    for line in danhmuc_nguonvon_obj.browse(cr, uid, danhmuc_nguonvon_ids):
                        result[line.nguon_von_id.id] = True
        return result.keys()
    
    def _compute_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        nam = context.get('nam_nguonvon',False) or time.strftime('%Y')
        for nguonvon in self.browse(cr, uid, ids, context=context):
            res[nguonvon.id] = {
                'sotien': 0.0,
                'kehoach_daunam': 0.0,
                'kehoach_dieuchinh': 0.0,
                'kehoach_dieuhoa': 0.0,
                'sotien_conlai': 0.0,
            }
            nguonvon_ids = ''
            child_of_ids = self.search(cr, uid, [('parent_id','child_of',nguonvon.id)])
            sql = '''
                SELECT CASE WHEN sum(sotien)!= 0 THEN sum(sotien) ELSE 0 END AS sotien,
                    CASE WHEN sum(kehoach_daunam)!= 0 THEN sum(kehoach_daunam) ELSE 0 END AS kehoach_daunam,
                    CASE WHEN sum(kehoach_dieuchinh)!= 0 THEN sum(kehoach_dieuchinh) ELSE 0 END AS kehoach_dieuchinh,
                    CASE WHEN sum(kehoach_dieuhoa)!= 0 THEN sum(kehoach_dieuhoa) ELSE 0 END AS kehoach_dieuhoa,
                    CASE WHEN sum(sotien_conlai)!= 0 THEN sum(sotien_conlai) ELSE 0 END AS sotien_conlai
                FROM danhmuc_nguonvon
                WHERE nam = '%(nam)s' AND (nguon_von_id = %(nguonvon)s
                    OR nguon_von_id in (%(nguonvon_ids)s))
            '''%({'nam':nam,
                  'nguonvon':nguonvon.id,
                  'nguonvon_ids':','.join(map(str, child_of_ids))})
            cr.execute(sql)
            total = cr.dictfetchone()
            res[nguonvon.id]['sotien'] = total['sotien']
            res[nguonvon.id]['kehoach_daunam'] = total['kehoach_daunam']
            res[nguonvon.id]['kehoach_dieuchinh'] = total['kehoach_dieuchinh']
            res[nguonvon.id]['kehoach_dieuhoa'] = total['kehoach_dieuhoa']
            res[nguonvon.id]['sotien_conlai'] = total['sotien_conlai']
        self.write(cr, uid, ids, {'nam':nam})
        return res
    
    def _get_child_ids(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            if record.child_parent_ids:
                result[record.id] = [x.id for x in record.child_parent_ids]
            else:
                result[record.id] = []
        return result
    
    _columns = {
        'name' :fields.char('Tên nguồn vốn', size=128, required=True),
        'nam' :fields.char('Năm', size=5),
        'parent_id' :fields.many2one('nguon.von','Nguồn vốn cha',domain="[('loai','=','xem')]"),
        'company_id' :fields.many2one('res.company','Cơ quan'),
        'child_parent_ids': fields.one2many('nguon.von','parent_id','Children'),
        'child_id': fields.function(_get_child_ids, type='many2many', relation="nguon.von", string="Child nguồn vốn"),
        'loai': fields.selection([('xem','Xem'),('binhthuong','Bình thường')], 'Loại'),
        'danhmuc_nguonvon_lines' :fields.one2many('danhmuc.nguonvon','nguon_von_id','Chi tiết nguồn vốn'),
        'sotien': fields.function(_compute_total, string='Tổng nguồn', digits=(16,0),multi='sums'),
#         'sotien': fields.function(_amount_total, string='Tổng nguồn', digits=(16,0),
#                 store={
#                     'nguon.von': (lambda self, cr, uid, ids, c={}: ids, ['danhmuc_nguonvon_lines'], 10),
#                     'danhmuc.nguonvon': (_get_danhmuc_nguonvon, ['sotien'], 20),
#                    },multi='sums'),
#         'sotien_capphat': fields.function(_amount_total, string='Số tiền cấp phát', digits=(16,0),
#                 store={
#                     'nguon.von': (lambda self, cr, uid, ids, c={}: ids, ['danhmuc_nguonvon_lines'], 10),
#                     'kehoach.thuchien': (_get_kehoach_thuchien, ['sotien'], 20),
#                     'duan.dautu.thuchien': (_get_duan_dautu_thuchien, ['kehoach_thuchien_lines'], 10),
#                     'duan.dautu': (_get_duan_dautu, ['ke_hoach_von'], 20),
#                    },multi='sums'),
#         'sotien_conlai': fields.function(_amount_total, string='Số tiền còn lại', digits=(16,0),
#                 store={
#                     'nguon.von': (lambda self, cr, uid, ids, c={}: ids, ['danhmuc_nguonvon_lines'], 10),
#                     'kehoach.thuchien': (_get_kehoach_thuchien, ['sotien'], 20),
#                     'duan.dautu.thuchien': (_get_duan_dautu_thuchien, ['kehoach_thuchien_lines'], 10),
#                     'duan.dautu': (_get_duan_dautu, ['ke_hoach_von'], 20),
#                    },multi='sums'),
        'kehoach_daunam': fields.function(_compute_total, string='Kế hoạch đầu năm', digits=(16,0),multi='sums'),
#         'kehoach_daunam': fields.function(_amount_total, string='Kế hoạch đầu năm', digits=(16,0),
#                 store={
#                     'nguon.von': (lambda self, cr, uid, ids, c={}: ids, ['danhmuc_nguonvon_lines'], 10),
#                     'kehoach.thuchien': (_get_kehoach_thuchien, ['sotien','nguonvon_id'], 10),
#                     'duan.dautu.thuchien': (_get_duan_dautu_thuchien, ['kehoach_thuchien_lines','duan_dautu_id'], 10),
#                     'duan.dautu': (_get_duan_dautu, ['ke_hoach_von'], 10),
#                    },multi='sums'),
        'kehoach_dieuchinh': fields.function(_compute_total, string='Kế hoạch đã duyệt (kỳ gần nhất)', digits=(16,0),multi='sums'),
#         'kehoach_dieuchinh': fields.function(_amount_total, string='Kế hoạch điều chỉnh', digits=(16,0),
#                 store={
#                     'danhmuc.nguonvon': (lambda self, cr, uid, ids, c={}: ids, ['sotien'], 10),
#                     'kehoach.dieuchinh': (_get_kehoach_thuchien, ['sotien','nguonvon_id'], 10),
#                     'duan.dautu.thuchien': (_get_duan_dautu_thuchien, ['kehoach_dieuchinh_line','duan_dautu_id'], 10),
#                     'duan.dautu': (_get_duan_dautu, ['ke_hoach_von'], 10),
#                    },multi='sums'),
        'kehoach_dieuhoa': fields.function(_compute_total, string='Kế hoạch cập nhật', digits=(16,0),multi='sums'),
#         'kehoach_dieuhoa': fields.function(_amount_total, string='Kế hoạch điều hòa', digits=(16,0),
#                 store={
#                     'danhmuc.nguonvon': (lambda self, cr, uid, ids, c={}: ids, ['sotien'], 10),
#                     'kehoach.thuchien': (_get_kehoach_thuchien, ['sotien','nguonvon_id'], 10),
#                     'kehoach.dieuchinh': (_get_kehoach_thuchien, ['sotien','nguonvon_id'], 10),
#                     'duan.dautu.thuchien': (_get_duan_dautu_thuchien, ['kehoach_thuchien_lines','duan_dautu_id','chuyenvon_den_duan_khac_lines','von_den_tu_duan_khac_lines','kehoach_dieuchinh_line'], 10),
#                     'duan.dautu': (_get_duan_dautu, ['ke_hoach_von'], 10),
# #                     'chuyenvon.den.duan.khac': (_get_chuyenvon_den_duan_khac, ['sotien','duan_thuhien_den_id'], 10),
#                    },multi='sums'),
        'sotien_conlai': fields.function(_compute_total, string='Số tiền còn lại', digits=(16,0),multi='sums'),
#         'sotien_conlai': fields.function(_amount_total, string='Số tiền còn lại', digits=(16,0),
#                 store={
#                     'danhmuc.nguonvon': (lambda self, cr, uid, ids, c={}: ids, ['sotien'], 10),
#                     'kehoach.thuchien': (_get_kehoach_thuchien, ['sotien','nguonvon_id'], 10),
#                     'kehoach.dieuchinh': (_get_kehoach_thuchien, ['sotien','nguonvon_id'], 10),
#                     'duan.dautu.thuchien': (_get_duan_dautu_thuchien, ['kehoach_thuchien_lines','duan_dautu_id','chuyenvon_den_duan_khac_lines','von_den_tu_duan_khac_lines','kehoach_dieuchinh_line'], 10),
#                     'duan.dautu': (_get_duan_dautu, ['ke_hoach_von'], 10),
#                    },multi='sums'),
    }
    _defaults={
          'loai': 'binhthuong',
          'company_id':lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'nguon.von', context=c),
    }
#     def init(self, cr):
#         wb = open_workbook(base_path + '/ql_duan_dautu/data/NguonVon.xls')
#         for s in wb.sheets():
#             if (s.name =='Sheet1'):
#                 for row in range(1,s.nrows):
#                     val0 = s.cell(row,0).value
#                     von_ids = self.search(cr, 1, [('name','=',val0)])
#                     if not von_ids:
#                         self.create(cr, 1, {'name': val0})
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_nguonvon_of_duan')==False:
            args += [('id','=',-1)]
        if context.get('search_nguonvon_of_duan'):
            duan_dautu_id = context.get('search_nguonvon_of_duan')
            sql = ''' select nguonvon_id from duan_tongmucdautu where duan_dautu_id=%s'''%(duan_dautu_id)
            cr.execute(sql)
            nguon_von_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',nguon_von_ids)]
        if context.get('search_nguonvon_of_duan_thuchien')==False:
            args += [('id','=',-1)]
        if context.get('search_nguonvon_of_duan_thuchien'):
            duan_thuchien_id = context.get('search_nguonvon_of_duan_thuchien')
            sql = ''' select nguonvon_id from kehoach_thuchien where duan_dautu_thuchien_id=%s'''%(duan_thuchien_id)
            cr.execute(sql)
            nguon_von_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',nguon_von_ids)]
        return super(nguon_von, self).search(cr, uid, args, offset, limit, order, context, count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
        
nguon_von()

class hinhthuc_dautu(osv.osv):
    _name = "hinhthuc.dautu"
    _description = "Hinh thuc dau tu"
    
    _columns = {
        'name' :fields.char('Tên hình thức đầu tư', size=128, required=True),
    }
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_duan_dautu/data/HinhThucDauTu.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    val0 = s.cell(row,0).value
                    hinhthuc_ids = self.search(cr, 1, [('name','=',val0)])
                    if not hinhthuc_ids:
                        self.create(cr, 1, {'name': val0})
    
hinhthuc_dautu()

class phuongthuc_dautu(osv.osv):
    _name = "phuongthuc.dautu"
    _description = "Phuong thuc dau tu"
    
    _columns = {
        'name' :fields.char('Tên phương thức đầu tư', size=128, required=True),
    }
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_duan_dautu/data/PhuongThucDauTu.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    val0 = s.cell(row,0).value
                    hinhthuc_ids = self.search(cr, 1, [('name','=',val0)])
                    if not hinhthuc_ids:
                        self.create(cr, 1, {'name': val0})
    
phuongthuc_dautu()

class nha_dau_tu(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'phan_he': fields.selection([('hosodautu','Hồ sơ đầu tư'),('duandautu','Dự án đầu tư')], 'Phân Hệ'),
    }
    
nha_dau_tu()

class lan_thamdinh(osv.osv):
    _name = "lan.thamdinh"
    _columns = {
        'name': fields.integer('Lần', readonly=True),
        'duan_dautu_id': fields.many2one('duan.dautu','Dự án đầu tư',ondelete='cascade'),
        'qddautu_thamdinh_ids': fields.many2many('vanban.den', 'qddautu_thamdinh_vanbanden_ref', 'qddautu_thamdinh_id', 'vanbanden_id','Thẩm định đầu tư'),
        'qddautu_thamdinh_chinhthuc_id': fields.many2one('vanban.den', 'Văn bản thẩm định chính thức',required=True),
        'noiphathanh_id': fields.related('qddautu_thamdinh_chinhthuc_id', 'noi_phathanh_id', type='many2one', relation='noi.phathanh', string='Nơi phát hành', readonly=True),
    }
    
    def unlink(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            update_ids = self.search(cr, uid,[('duan_dautu_id','=',line.duan_dautu_id.id),('name','>',line.name)])
            if update_ids:
                cr.execute("UPDATE lan_thamdinh SET name=name-1 WHERE id in %s",(tuple(update_ids),))
        return super(lan_thamdinh, self).unlink(cr, uid, ids, context)  
    
    def create(self, cr, uid, vals, context=None):
#         if 'name' not in vals:
#             vals.append({'name':1})
        vals['name'] = len(self.search(cr, uid,[('duan_dautu_id', '=', vals['duan_dautu_id'])])) + 1
        return super(lan_thamdinh, self).create(cr, uid, vals, context)
lan_thamdinh()

class quyetdinh_dautu(osv.osv):
    _name = "quyetdinh.dautu"
    
    def _compute_tongmuc_dautu(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        giaidoan_ids = []
        for duan in self.browse(cr, uid, ids, context=context):
            res[duan.id] = 0.0
            for line in duan.nguon_von_ids:
                res[duan.id] += line.sotien
        return res
    
    def _get_duan_dautu_from_nguonvon(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('duan.tongmucdautu').browse(cr, uid, ids, context=context):
            result[line.duan_dautu_id.id] = True
        return result.keys()
    
    _columns = {
        'duan_dautu_id': fields.many2one('duan.dautu','Dự án đầu tư',ondelete='cascade'),
        'dautu_soquyetdinh_id': fields.many2one('vanban.den','SQĐ Đầu tư',required=True),
        'dautu_ngay':fields.date('Ngày Đâu Tư',required=True,),
        'tongmuc_dautu': fields.function(_compute_tongmuc_dautu, type='float', digits=(16,0), string='Tổng mức đầu tư',
                store={
                    'quyetdinh.dautu': (lambda self, cr, uid, ids, c={}: ids, ['nguon_von_ids'], 10),
                    'duan.tongmucdautu': (_get_duan_dautu_from_nguonvon, ['sotien'], 10),
                   }),
        'nguon_von_ids': fields.one2many('duan.tongmucdautu','quyetdinh_dautu_id', 'Nguồn vốn'),
    }
    _defaults = {
                 'dautu_ngay': time.strftime('%Y-%m-%d'),
    }
    
    def create(self, cr, uid, vals, context=None):
        duan_tongmucdautu_obj = self.pool.get('duan.tongmucdautu')
        tongmuc_dautu_ids = duan_tongmucdautu_obj.search(cr, uid, [('duan_dautu_id','=',vals['duan_dautu_id'])])
        duan_tongmucdautu_obj.unlink(cr, uid, tongmuc_dautu_ids)
        for nguonvon in vals['nguon_von_ids']:
            duan_tongmucdautu_obj.create(cr, uid, {'duan_dautu_id':vals['duan_dautu_id'],'nguonvon_id': nguonvon[2]['nguonvon_id'],'sotien': nguonvon[2]['sotien']})
        return super(quyetdinh_dautu, self).create(cr, uid, vals, context)
    def write(self, cr, uid, ids, vals, context=None):
        super(quyetdinh_dautu, self).write(cr, uid, ids, vals, context=context)
        duan_tongmucdautu_obj = self.pool.get('duan.tongmucdautu')
        quyetdinhdautu = self.browse(cr, uid, ids)[0]
        duan_dautu_id = quyetdinhdautu.duan_dautu_id.id
        qd_dautu_ids = self.search(cr, uid, [('duan_dautu_id','=',duan_dautu_id)],limit=1,order='id desc')
        if 'nguon_von_ids' in vals and qd_dautu_ids==ids:
            tongmuc_dautu_ids = duan_tongmucdautu_obj.search(cr, uid, [('duan_dautu_id','=',duan_dautu_id)])
            duan_tongmucdautu_obj.unlink(cr, uid, tongmuc_dautu_ids)
            for nguonvon in quyetdinhdautu.nguon_von_ids:
                duan_tongmucdautu_obj.create(cr, uid, {'duan_dautu_id':duan_dautu_id,'nguonvon_id': nguonvon.nguonvon_id.id,'sotien': nguonvon.sotien})
        return True
    def unlink(self, cr, uid, ids, context=None):
        duan_tongmucdautu_obj = self.pool.get('duan.tongmucdautu')
        quyetdinhdautu_ids = self.search(cr, uid, [('id','not in',ids)],limit=1,order='id desc')
        quyetdinhdautu = self.browse(cr, uid, ids)[0]
        duan_dautu_id = quyetdinhdautu.duan_dautu_id.id
        tongmuc_dautu_ids = duan_tongmucdautu_obj.search(cr, uid, [('duan_dautu_id','=',duan_dautu_id)])
        duan_tongmucdautu_obj.unlink(cr, uid, tongmuc_dautu_ids)
        if quyetdinhdautu_ids:
            quyetdinhdautu = self.browse(cr, uid, quyetdinhdautu_ids)[0]
            for nguonvon in quyetdinhdautu.nguon_von_ids:
                duan_tongmucdautu_obj.create(cr, uid, {'duan_dautu_id':duan_dautu_id,'nguonvon_id': nguonvon.nguonvon_id.id,'sotien': nguonvon.sotien})
        return super(quyetdinh_dautu, self).unlink(cr, uid, ids, context=context)
quyetdinh_dautu()

class pheduyet_tdt(osv.osv):
    _name = "pheduyet.tdt"
    _columns = {
        'duan_dautu_id': fields.many2one('duan.dautu','Dự án đầu tư',ondelete='cascade'),
        'pheduyet_tdt_soquyetdinh_id': fields.many2one('vanban.den','SQĐ phê duyệt TDT',required=True),
        'pheduyet_tdt_ngay':fields.date('Ngày phê duyệt TDT',required=True,),
        'pheduyet_tdt_tongdutoan':fields.float('Tông Dự Toán', digits=(16,0), required=True,),
    }
    _defaults = {
                 'pheduyet_tdt_ngay': time.strftime('%Y-%m-%d'),
    }
pheduyet_tdt()

class linhvuc_dauthau(osv.osv):
    _name = "linhvuc.dauthau"
    _columns = {
        'name': fields.char('Tên',size=256,required=True),
    }
linhvuc_dauthau()

class hinhthuc_luachon_nhathau(osv.osv):
    _name = "hinhthuc.luachon.nhathau"
    _columns = {
        'name': fields.char('Tên',size=256,required=True),
    }
hinhthuc_luachon_nhathau()

class pheduyet_kqdt(osv.osv):
    _name = "pheduyet.kqdt"
    _columns = {
        'name': fields.char('Tên gói thầu',size=256,required=True),
        'giaidoan_id': fields.many2one('duan.giaidoan','Giai đoạn'),
        'linhvuc_dauthau_id': fields.many2one('linhvuc.dauthau','Lĩnh vực đấu thầu',required=True),
        'hinhthuc_luachon_nhathau_id': fields.many2one('hinhthuc.luachon.nhathau','Hình thức lựa chọn nhà thầu',required=True),
        'duan_dautu_id': fields.many2one('duan.dautu','Dự án đầu tư',ondelete='cascade'),
        'pheduyet_kqdt_soquyetdinh_id': fields.many2one('vanban.den','SQĐ phê duyệt KQĐT',required=True),
        'pheduyet_kqdt_ngay':fields.date('Ngày phê duyệt KQĐT',required=True,),
        'pheduyet_giagoithau':fields.float('Giá gói thầu', digits=(16,0), required=True,),
        'pheduyet_giatrungthau':fields.float('Giá trúng thầu', digits=(16,0), required=True,),
    }
    _defaults = {
                 'pheduyet_kqdt_ngay': time.strftime('%Y-%m-%d'),
    }
pheduyet_kqdt()

class tiendo_duan(osv.osv):
    _name = "tiendo.duan"
    _columns = {
        'name': fields.text('Tiến độ',required=True),
        'duan_dautu_id': fields.many2one('duan.dautu','Dự án đầu tư',ondelete='cascade'),
        'ngay':fields.date('Ngày',required=True,),
        'hinh1': fields.binary('Hình ảnh 1'),
        'hinh2': fields.binary('Hình ảnh 2'),
        'hinh3': fields.binary('Hình ảnh 3'),
    }
    _defaults = {
         'ngay': time.strftime('%Y-%m-%d'),
    }
tiendo_duan()

class duan_dautu(osv.osv):
    _name = "duan.dautu"
#     _order = "ngaykhoicong"
    
    def _get_giaidoan(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        giaidoan_ids = []
        for duan in self.browse(cr, uid, ids, context=context):
            res[duan.id] = False
            for thuchien in duan.ke_hoach_von:
                if thuchien.giai_doan_id:
                    giaidoan_ids.append(thuchien.giai_doan_id.id)
            if giaidoan_ids:
                sql ='''select id from duan_giaidoan where id in (%s) order by stt desc'''%(','.join(map(str, giaidoan_ids)))
                cr.execute(sql)
                giaidoan_new_ids = [x[0] for x in cr.fetchall()]
                res[duan.id] = giaidoan_new_ids and giaidoan_new_ids[0] or False
                self.write(cr, uid, duan.id, {'giai_doan_now_id':giaidoan_new_ids and giaidoan_new_ids[0] or False}, context)
            giaidoan_ids = []
        return res
    
    def _get_duan_dautu_thuchien(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('duan.dautu.thuchien').browse(cr, uid, ids, context=context):
            result[line.duan_dautu_id.id] = True
        return result.keys()
    
    def _compute_tongmuc_dautu(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        giaidoan_ids = []
        for duan in self.browse(cr, uid, ids, context=context):
            res[duan.id] = 0.0
            for line in duan.nguon_von_ids:
                res[duan.id] += line.sotien
        return res
    
    def _get_duan_dautu_from_nguonvon(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('duan.tongmucdautu').browse(cr, uid, ids, context=context):
            result[line.duan_dautu_id.id] = True
        return result.keys()
    
    _columns = {
        'name' :fields.text('Tên dự án', required=True,),
        'ma_duan' :fields.char('Mã dự án', required=False, size=1024),
        'nha_dau_tu_id': fields.many2one('res.partner', 'Chủ đầu tư', required=True, domain="[('phan_he','=','duandautu')]"),
        'linhvuc_id':fields.many2one('duan.danhmuc','Lĩnh vực đầu tư', domain="[('danhmuc_cha','=',False)]", required=True),
        'danhmuc_id':fields.many2one('duan.danhmuc','Ngành', domain="[('danhmuc_cha','=',linhvuc_id)]", required=True),
        'nhom_id':fields.many2one('duan.nhom','Thuộc nhóm ', required=False,),
        'quoc_gia_id': fields.many2one('res.country','Quốc gia'),
        'tinh_tp_id': fields.many2one('res.country.state','Tỉnh/TP', domain="[('country_id','=',quoc_gia_id)]"),
        'quan_huyen_id': fields.many2one('quan.huyen','Quận/Huyện', domain="[('state_id','=',tinh_tp_id)]"),
        'lien_diaban_ids': fields.many2many('quan.huyen','liendiaban_quanhuyen_ref','liendiaban_id','quanhuyen_id',string='Liên địa bàn', domain="[('state_id','=',tinh_tp_id),('id','!=',quan_huyen_id)]"),
        'dia_chi': fields.char('Địa chỉ', size=128),
        'quymo_duan': fields.text('Quy mô'),
        'tiendo_duan_line': fields.one2many('tiendo.duan', 'duan_dautu_id', 'Tiến độ'),
        'hinhthuc_id':fields.many2one('hinhthuc.dautu','Hình thức đầu tư', required=True),
        'phuongthuc_id':fields.many2one('phuongthuc.dautu','Phương thức đầu tư', required=True),
        
        'nanglucthietke':fields.many2one('duan.nanglucthietke','Năng lực thiết kế', required=False,),
        'giai_doan_now_id': fields.many2one('duan.giaidoan','Giai đoạn', required=False,),
        'giai_doan_id': fields.function(_get_giaidoan, type='many2one', relation='duan.giaidoan', string='Giai đoạn',
                store={
                    'duan.dautu': (lambda self, cr, uid, ids, c={}: ids, ['ke_hoach_von'], 10),
                    'duan.dautu.thuchien': (_get_duan_dautu_thuchien, ['giai_doan_id'], 10),
                   }),
        'ngaykhoicong':fields.date('Ngày khởi công',required=False,),
        'ngayhoanthanh':fields.date('Ngày hoàn thành',required=False,),
        'namkhoicong':fields.char('Năm khởi công',size=5,required=False,),
        'namhoanthanh':fields.char('Năm hoàn thành',size=5,required=False,),
        
        'tongmuc_dautu': fields.function(_compute_tongmuc_dautu, type='float', digits=(16,0), string='Tổng mức đầu tư',
                store={
                    'duan.dautu': (lambda self, cr, uid, ids, c={}: ids, ['nguon_von_ids'], 10),
                    'duan.tongmucdautu': (_get_duan_dautu_from_nguonvon, ['sotien'], 10),
                   }),
                
        'von_oda_currency_id': fields.many2one('res.currency', 'Tiền Tệ Vốn ODA'),
        'nguon_von_ids': fields.one2many('duan.tongmucdautu','duan_dautu_id', 'Nguồn vốn'),
        'nguonvon_id': fields.related('nguon_von_ids','nguonvon_id', relation='nguon.von',type='many2one',string="Nguồn vốn",store=False),
        'cocaudautu_lines': fields.one2many('duan.cocaudautu','duan_dautu_id', 'Cơ cấu đầu tư'),
        
        'thamdinh_dautu_lines':fields.one2many('lan.thamdinh', 'duan_dautu_id', 'Thẩm định đầu tư'),
        
        'quyetdinh_dautu_lines':fields.one2many('quyetdinh.dautu', 'duan_dautu_id', 'SQĐ Đầu tư'),
        
        'pheduyet_tdt_lines':fields.one2many('pheduyet.tdt', 'duan_dautu_id', 'Tông Dự Toán'),
        
        'pheduyet_kqdt_thamdinh_ids': fields.many2many('vanban.den', 'pheduyet_kqdt_thamdinh_vanbanden_ref', 'pheduyet_kqdt_thamdinh_id', 'vanbanden_id','Kế hoạch đấu thầu'),
        'vanban_phaply_ids': fields.many2many('vanban.den', 'vanban_phaply_vanbanden_ref', 'vanban_phaply_id', 'vanbanden_id','Văn bản pháp lý'),
        
        'baocao_giamsat_ids': fields.many2many('vanban.den', 'baocao_giamsat_vanbanden_ref', 'baocao_giamsat_id', 'vanbanden_id','Báo cáo giám sát'),

        'pheduyet_kqdt_lines':fields.one2many('pheduyet.kqdt', 'duan_dautu_id', 'SQĐ phê duyệt KQĐT'),
        
        'ke_hoach_von':fields.one2many('duan.dautu.thuchien', 'duan_dautu_id', 'Kế hoạch vốn'),
        'ghichu':fields.text('Ghi Chú',size=128, required=False,),
        'lichsu_thaydoi': fields.one2many('dadt.lichsu', 'duan_dautu_id', 'Lịch sử thay đổi',readonly=True),
        'write_date': fields.date('Ngày điều chỉnh', readonly=True),
        'write_uid': fields.many2one('res.users','Người thực hiện', readonly=True),
        'so_lan_thay_doi': fields.integer('Số lần thay đổi', readonly=True),
#         'ghichu1':fields.text('Ghi Chú',size=128, required=False,),

        'state': fields.selection([
            ('draft', 'Mới tạo'),
            ('done', 'Đã hoàn thành'),
            ], 'Status', readonly=True),
        
        'nam_luy_ke': fields.char('Năm lũy kế (Đã cấp phát)', size=5),
        'sotien_luy_ke': fields.float('Số tiền lũy kế (Đã cấp phát)', digits=(16,0)),
        'company_id' :fields.many2one('res.company','Cơ quan'),
    }
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            args+=['|',('name','ilike',name),('ma_duan','ilike',name)]
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
    
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
                    ids = [ids]
        reads = self.read(cr, uid, ids, ['name', 'ma_duan'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['ma_duan']:
                name = record['ma_duan'] + ' - ' + name
            res.append((record['id'], name))
        return res
    
    def onchange_linhvuc_id(self, cr, uid, ids, context=None):
        return {'value': {'danhmuc_id': False}}
    
    def _get_default_currency(self, cr, uid, context=None):
        currency_ids = self.pool.get('res.currency').search(cr, uid, [('name','=','VND')], context=context)
        return currency_ids and currency_ids[0] or False
    
    def _get_default_country(self, cr, uid, context=None):
        country_ids = self.pool.get('res.country').search(cr, uid, [('code','=','VN')], context=context)
        return country_ids and country_ids[0] or False
    
    def _get_tinh_tp(self, cr, uid, context=None):
        property_pool = self.pool.get('admin.property')
        default_tinh_tp_gcndt = False
        property_obj = property_pool._get_project_property_by_name(cr, uid, 'default_tinh_tp_gcndt') or None
        if property_obj:
            default_tinh_tp_gcndt = property_obj.value
        country_ids = self._get_default_country(cr, uid, context)
        if country_ids:
            tinh_tp_ids = self.pool.get('res.country.state').search(cr, uid, [('name','=',default_tinh_tp_gcndt),('country_id','=',country_ids)])
        return tinh_tp_ids and tinh_tp_ids[0] or False
    
    def _get_default_giai_doan(self, cr, uid, context=None):
        giai_doan_ids = self.pool.get('duan.giaidoan').search(cr, uid, [], context=context)
        return giai_doan_ids and giai_doan_ids[0] or False
    
    def _get_default_linhvuc(self, cr, uid, context=None):
        danhmuc_ids = self.pool.get('duan.danhmuc').search(cr, uid, [('danhmuc_cha','=',False)], context=context)
        return danhmuc_ids and danhmuc_ids[0] or False
    
    def _get_default_hinhthuc(self, cr, uid, context=None):
        hinhthuc_ids = self.pool.get('hinhthuc.dautu').search(cr, uid, [], context=context)
        return hinhthuc_ids and hinhthuc_ids[0] or False
    
    def _get_default_phuongthuc(self, cr, uid, context=None):
        phuongthuc_ids = self.pool.get('phuongthuc.dautu').search(cr, uid, [('name','=','-')], context=context)
        if not phuongthuc_ids:
            phuongthuc_ids = self.pool.get('phuongthuc.dautu').search(cr, uid, [], context=context)
        return phuongthuc_ids and phuongthuc_ids[0] or False
    
    _defaults = {
         'state': 'draft',
         'von_oda_currency_id':_get_default_currency,
         'tinh_tp_id': _get_tinh_tp,
         'quoc_gia_id': _get_default_country,
#          'giai_doan_id': _get_default_giai_doan,
         'linhvuc_id': _get_default_linhvuc,
         'hinhthuc_id': _get_default_hinhthuc,
         'phuongthuc_id': _get_default_phuongthuc,
         'ngaykhoicong': time.strftime('%Y-%m-%d'),
         'company_id':lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'duan.dautu', context=c),
     }
    
    def hoan_thanh(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'done'})
    
    def create(self, cr, uid, vals, context=None):
        if not vals['ke_hoach_von']:
            if vals['namkhoicong']==False:
                vals_thuchien={
                    'giai_doan_id': self._get_default_giai_doan(cr, uid, context),
                    'nam': time.strftime('%Y'),
                }
            else:
                vals_thuchien={
                    'nam': vals['namkhoicong'],
                    'giai_doan_id': self._get_default_giai_doan(cr, uid, context),
                }
            vals.update({'ke_hoach_von':[(0, 0, vals_thuchien)]})
        return super(duan_dautu, self).create(cr, uid, vals, context)
    
#     def write(self, cr, uid, ids, vals, context=None):
#         if context is None:
#             context = {}
#         values = {}
#         dadt = self.browse(cr, uid, ids[0])
#         so_lan_thay_doi = dadt.so_lan_thay_doi
#         sql = '''insert into dadt_lichsu(duan_dautu_id,tenduan,nha_dau_tu_id,danhmuc_id,giai_doan_id,ngaykhoicong,state,so_lan_thay_doi)
#                 values(%(duan_dautu_id)s,'%(name)s',%(nha_dau_tu_id)s,%(danhmuc_id)s,%(giai_doan_id)s,'%(ngaykhoicong)s','%(state)s',%(so_lan_thay_doi)s)'''
#         for key in ['name','nha_dau_tu_id','danhmuc_id','giai_doan_id','ngaykhoicong','state']:
#             if vals.has_key(key):
#                 if key in ['nha_dau_tu_id','danhmuc_id','giai_doan_id']:
#                     values[key] = dadt[key].id or "Null"
#                 else:
#                     values[key] = dadt[key] or "Null"
#             else:
#                 values[key] = "Null"
#         values['duan_dautu_id'] = ids[0]
#         values['so_lan_thay_doi'] = dadt.so_lan_thay_doi
#         sql = sql%values
#         sql = sql.replace("'Null'",'Null')
#         cr.execute(sql)
#         vals['so_lan_thay_doi'] = so_lan_thay_doi+1
#         return super(duan_dautu, self).write(cr, uid, ids, vals, context=context)
    
duan_dautu()

class dadt_lichsu(osv.osv):
    _name = "dadt.lichsu"
    _description = "Lich Su Thay Doi"
    _columns = {
        'duan_dautu_id': fields.many2one('duan.dautu','Dự án đầu tư',ondelete='cascade'),
        'tenduan': fields.char('Tên dự án'),
        'nha_dau_tu_id': fields.many2one('res.partner', 'Nhà đầu tư', readonly=True),
        'danhmuc_id':fields.many2one('duan.danhmuc','Danh muc', readonly=True),
        'giai_doan_id': fields.many2one('duan.giaidoan','Giai đoạn', readonly=True),
        'ngaykhoicong':fields.date('Ngày khỏi công',readonly=True,),
        
        'so_lan_thay_doi': fields.integer('Số lần thay đổi'),
        'write_date': fields.date('Ngày điều chỉnh'),
        'write_uid': fields.many2one('res.users','Người thực hiện'),
        'state': fields.selection([
            ('draft', 'Mới tạo'),
            ('done', 'Đã hoàn thành'),
            ], 'Status', readonly=True)
    }
dadt_lichsu()

class duan_cocaudautu(osv.osv):
    _name = "duan.cocaudautu"
    _description = "Tong muc dau tu du an"
     
    _columns = {
        'duan_dautu_id': fields.many2one('duan.dautu', 'Dự án đầu tư', ondelete='cascade'),
        'cocaudautu_id': fields.many2one('cocau.dautu', 'Cơ cấu đầu tư', required=True),
        'sotien': fields.float('Số tiền', digits=(16,0)),
    }
     
duan_cocaudautu()

class duan_tongmucdautu(osv.osv):
    _name = "duan.tongmucdautu"
    _description = "Tong muc dau tu du an"
     
    _columns = {
        'duan_dautu_id': fields.many2one('duan.dautu', 'Dự án đầu tư', ondelete='cascade'),
        'quyetdinh_dautu_id': fields.many2one('quyetdinh.dautu', 'Quyết định đầu tư', ondelete='cascade'),
        'nguonvon_id': fields.many2one('nguon.von', 'Nguồn vốn', required=True, domain="[('loai','=','binhthuong')]"),
        'sotien': fields.float('Số tiền', digits=(16,0)),
    }
     
duan_tongmucdautu()

class kehoach_thuchien(osv.osv):
    _name = "kehoach.thuchien"
    _description = "Ke hoach thuc hien"
     
    _columns = {
        'duan_dautu_thuchien_id': fields.many2one('duan.dautu.thuchien', 'Dự án đầu tư thực hiện', ondelete='cascade'),
        'kehoach_dieuchinh_id': fields.many2one('kehoach.dieuchinh', 'Kế hoạch điều chỉnh', ondelete='cascade'),
        'nguonvon_id': fields.many2one('nguon.von', 'Nguồn vốn', required=True, domain="[('loai','=','binhthuong')]"),
        'sotien': fields.float('Số tiền', digits=(16,0)),
    }
    
    def create(self, cr, uid, vals, context=None):
        nguonvon_obj = self.pool.get('danhmuc.nguonvon')
        if 'duan_dautu_thuchien_id' in vals:
            duan_thuchien = self.pool.get('duan.dautu.thuchien').browse(cr, uid, vals['duan_dautu_thuchien_id'])
            nguonvon_ids = nguonvon_obj.search(cr, uid,[('nam','=',duan_thuchien.nam),('nguon_von_id', '=', vals['nguonvon_id'])])
            for nguonvon in nguonvon_obj.browse(cr, uid, nguonvon_ids):
                sotien_conlai=nguonvon.sotien_conlai
                if vals['sotien']>nguonvon.sotien_conlai:
                    raise osv.except_osv(_('Cảnh báo!'),
                                _('Nguồn vốn không đủ để cấp phát!'))
        return super(kehoach_thuchien, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        for capphat in self.browse(cr, uid, ids):
            sotien_capphat = capphat.sotien
            if capphat.duan_dautu_thuchien_id:
                duan_dautu_thuchien_id = capphat.duan_dautu_thuchien_id.id
                nguonvon_obj = self.pool.get('danhmuc.nguonvon')
                duan_thuchien = self.pool.get('duan.dautu.thuchien').browse(cr, uid, duan_dautu_thuchien_id)
                if 'nguonvon_id' in vals:
                    nguonvon_ids = nguonvon_obj.search(cr, uid,[('nam','=',duan_thuchien.nam),('nguon_von_id', '=', vals['nguonvon_id'])])
                    for nguonvon in nguonvon_obj.browse(cr, uid, nguonvon_ids):
                        if 'sotien' in vals:
                            if (vals['sotien']-sotien_capphat)>nguonvon.sotien_conlai:
                                raise osv.except_osv(_('Cảnh báo!'),
                                            _('Nguồn vốn không đủ để cấp phát!'))
                        else:
                            if sotien_capphat>nguonvon.sotien_conlai:
                                raise osv.except_osv(_('Cảnh báo!'),
                                            _('Nguồn vốn không đủ để cấp phát!'))
                else:
                    nguonvon_ids = nguonvon_obj.search(cr, uid,[('nam','=',duan_thuchien.nam),('nguon_von_id', '=', capphat.nguonvon_id.id)])
                    for nguonvon in nguonvon_obj.browse(cr, uid, nguonvon_ids):
                        if 'sotien' in vals:
                            if (vals['sotien']-sotien_capphat)>nguonvon.sotien_conlai:
                                raise osv.except_osv(_('Cảnh báo!'),
                                            _('Nguồn vốn không đủ để cấp phát!'))
        return super(kehoach_thuchien, self).write(cr, uid, ids, vals, context=context)
    
kehoach_thuchien()
 
class chuyenvon_den_duan_khac(osv.osv):
    _name = "chuyenvon.den.duan.khac"
    _description = "Chuyen von den du an khac"
    _columns = {
        'duan_from_id': fields.many2one('duan.dautu','Từ dự án'),
        'duan_to_id': fields.many2one('duan.dautu','Đến dự án',required=True, domain="[('id','!=',duan_from_id)]"),
        'sotien': fields.float('Số tiền',required=True, digits=(16,0)),
        'duan_thuhien_id': fields.many2one('duan.dautu.thuchien','Kế hoạch vốn', ondelete='cascade'),
        'nguonvon_id': fields.many2one('nguon.von','Nguồn vốn',required=True),
        'duan_thuhien_den_id': fields.many2one('duan.dautu.thuchien','Kế hoạch vốn',required=True),
        'ngay':fields.date('Ngày'),
        'vanban_phaply_id': fields.many2one('vanban.den','Văn bản pháp lý'),
    }
    
    def _get_default_duan_from(self, cr, uid, context=None):
        return context.get('duan_dautu_id')
    
    def create(self, cr, uid, vals, context=None):
        duan_thuchien_obj = self.pool.get('duan.dautu.thuchien')
        duan_thuchien_ids = duan_thuchien_obj.search(cr, uid,[('id', '=', vals['duan_thuhien_id'])])
        for duan_thuchien in duan_thuchien_obj.browse(cr, uid, duan_thuchien_ids):
            if vals['sotien']>duan_thuchien.kehoach_dieuhoa:
                raise osv.except_osv(_('Cảnh báo!'),
                            _('Nguồn vốn không đủ để chuyển đến dự án khác!'))
        return super(chuyenvon_den_duan_khac, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'sotien' in vals:
            duan_thuchien_obj = self.pool.get('duan.dautu.thuchien')
            for chuyenvon in self.browse(cr,uid, ids):
                duan_thuchien_ids = duan_thuchien_obj.search(cr, uid,[('id', '=', chuyenvon.duan_thuhien_id.id)])
                for duan_thuchien in duan_thuchien_obj.browse(cr, uid, duan_thuchien_ids):
                    if (vals['sotien']-chuyenvon.sotien)>duan_thuchien.kehoach_dieuhoa:
                        raise osv.except_osv(_('Cảnh báo!'),
                                    _('Nguồn vốn không đủ để chuyển đến dự án khác!'))
        return super(chuyenvon_den_duan_khac, self).write(cr, uid, ids, vals, context=context)
    
    _defaults = {
                 'duan_from_id': _get_default_duan_from,
                 'ngay': time.strftime('%Y-%m-%d'),
                 }
chuyenvon_den_duan_khac()

class kehoach_dieuchinh(osv.osv):
    _name = "kehoach.dieuchinh"
    _order = 'name desc'
    def _compute_kehoach_thuchien(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for dieuchinh in self.browse(cr, uid, ids, context=context):
            res[dieuchinh.id] = {
                'kehoach_thuchien': 0.0,
            }
            kehoach_thuchien = 0.0
            for line in dieuchinh.kehoach_thuchien_line:
                kehoach_thuchien += line.sotien
            res[dieuchinh.id]['kehoach_thuchien'] = kehoach_thuchien
        return res
    
    def _get_kehoach_thuchien_from_nguonvon(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('kehoach.thuchien').browse(cr, uid, ids, context=context):
            result[line.kehoach_dieuchinh_id.id] = True
        return result.keys()
    
    _columns = {
        'name': fields.integer('Lần', readonly=True),
        'duan_dautu_thuchien_id': fields.many2one('duan.dautu.thuchien','Dự án đầu tư thực hiện',ondelete='cascade'),
        'ngay': fields.date('Ngày',required=True),
        'duyet': fields.boolean('Đã duyệt'),
        'kehoach_thuchien': fields.function(_compute_kehoach_thuchien, type='float', digits=(16,0), string='Kế hoạch đầu năm',
                store={
                    'kehoach.dieuchinh': (lambda self, cr, uid, ids, c={}: ids, ['kehoach_thuchien_line'], 10),
                    'kehoach.thuchien': (_get_kehoach_thuchien_from_nguonvon, ['nguonvon_id','sotien'], 10),
                   },
                   multi='kehoach_thuchien'),
        'kehoach_thuchien_line': fields.one2many('kehoach.thuchien', 'kehoach_dieuchinh_id', 'Kế hoạch thực hiện'),
    }
    
    def duyet(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'duyet':True})
        
    def unlink(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            update_ids = self.search(cr, uid,[('duan_dautu_thuchien_id','=',line.duan_dautu_thuchien_id.id),('name','>',line.name)])
            if update_ids:
                cr.execute("UPDATE kehoach_dieuchinh SET name=name-1 WHERE id in %s",(tuple(update_ids),))
        return super(kehoach_dieuchinh, self).unlink(cr, uid, ids, context)  
     
    def create(self, cr, uid, vals, context=None):
        vals['name'] = len(self.search(cr, uid,[('duan_dautu_thuchien_id', '=', vals['duan_dautu_thuchien_id'])])) + 1
        kehoach_thuchien_obj = self.pool.get('kehoach.thuchien')
        duan_thuchien = self.pool.get('duan.dautu.thuchien').browse(cr, uid, vals['duan_dautu_thuchien_id'])
        if vals['name'] == 1:
            if duan_thuchien.kehoach_thuchien_lines:
                ngay = time.strftime('%Y-%m-%d')
                sql = '''
                    insert into kehoach_dieuchinh(name,duan_dautu_thuchien_id,ngay,duyet) values (%s,%s,'%s','%s')
                '''%(0,duan_thuchien.id,ngay,'t')
                cr.execute(sql)
                sql = '''
                    select id from kehoach_dieuchinh where name=%s and duan_dautu_thuchien_id=%s and ngay ='%s' order by id limit 1
                '''%(0,duan_thuchien.id,ngay)
                cr.execute(sql)
                kehoach_id = cr.dictfetchall()[0]['id']
                for thuchien in duan_thuchien.kehoach_thuchien_lines:
                    kehoach_thuchien_obj.create(cr, uid, {'kehoach_dieuchinh_id':kehoach_id,'nguonvon_id':thuchien.nguonvon_id.id,'sotien':thuchien.sotien})
                self.pool.get('duan.dautu.thuchien').write(cr,uid,duan_thuchien.id,{'duyet':True})
        if vals['name'] > 1:
            vals['name'] -= 1
        if vals['duyet']:
            kehoach_thuchien_ids = kehoach_thuchien_obj.search(cr, uid, [('duan_dautu_thuchien_id','=',vals['duan_dautu_thuchien_id'])])
            kehoach_thuchien_obj.unlink(cr, uid, kehoach_thuchien_ids)
            for nguonvon in vals['kehoach_thuchien_line']:
                duan_tongmucdautu_obj.create(cr, uid, {'duan_dautu_thuchien_id':vals['duan_dautu_thuchien_id'],'nguonvon_id': nguonvon[2]['nguonvon_id'],'sotien': nguonvon[2]['sotien']})
        return super(kehoach_dieuchinh, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        super(kehoach_dieuchinh, self).write(cr, uid, ids, vals, context=context)
        kehoach_thuchien_obj = self.pool.get('kehoach.thuchien')
        kehoach = self.browse(cr, uid, ids)[0]
        duan_dautu_thuchien_id = kehoach.duan_dautu_thuchien_id.id
        kehoach_ids = self.search(cr, uid, [('duan_dautu_thuchien_id','=',duan_dautu_thuchien_id)],limit=1,order='id desc')
        if 'duyet' in vals and kehoach_ids==ids:
            kehoach_thuchien_ids = kehoach_thuchien_obj.search(cr, uid, [('duan_dautu_thuchien_id','=',duan_dautu_thuchien_id)])
            kehoach_thuchien_obj.unlink(cr, uid, kehoach_thuchien_ids)
            for nguonvon in kehoach.kehoach_thuchien_line:
                kehoach_thuchien_obj.create(cr, uid, {'duan_dautu_thuchien_id':duan_dautu_thuchien_id,'nguonvon_id': nguonvon.nguonvon_id.id,'sotien': nguonvon.sotien})
        return True
    
    _defaults={
        'ngay': time.strftime('%Y-%m-%d'),
        'name': 1,
    }
kehoach_dieuchinh()

class duan_dautu_thuchien(osv.osv):
    _name = "duan.dautu.thuchien"
    _description = "Qua Trinh Thuc Hien"
    
    def _amount_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for thuchien in self.browse(cr, uid, ids, context=context):
            res[thuchien.id] = {
                'sotien_capphat': 0.0,
                'khoiluong_thuchien': 0.0,
                'khoiluong_hoanthanh': 0.0,
                'khoiluong_nghiemthu': 0.0,
            }
            sotien_capphat = 0.0
            khoiluong_thuchien = 0.0
            khoiluong_hoanthanh = 0.0
            khoiluong_nghiemthu = 0.0
            for line in thuchien.thuchien_chitiet:
                sotien_capphat = line.sotien
                khoiluong_thuchien = line.khoiluong_thuchien
                khoiluong_hoanthanh = line.khoiluong_hoanthanh
                khoiluong_nghiemthu = line.khoiluong_nghiemthu
            res[thuchien.id]['sotien_capphat'] = sotien_capphat
            res[thuchien.id]['khoiluong_thuchien'] = khoiluong_thuchien
            res[thuchien.id]['khoiluong_hoanthanh'] = khoiluong_hoanthanh
            res[thuchien.id]['khoiluong_nghiemthu'] = khoiluong_nghiemthu
        return res
    
    def _get_duan_dautu_thuchien_chitiet(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('duan.dautu.thuchien.chitiet').browse(cr, uid, ids, context=context):
            result[line.duan_dautu_thuchien_id.id] = True
        return result.keys()
    
    def _when_changing_danhmucid_from_duan(self, cr, uid, ids, context=None):
        result = {}
        duan_dautu_thuchien_ids = self.pool.get('duan.dautu.thuchien').search(cr, uid, [('duan_dautu_id','in',ids)], context=context)
        for duan_dautu_thuchien_id in duan_dautu_thuchien_ids:
            result[duan_dautu_thuchien_id] = True
        return result.keys()
    
    def _compute_kehoach_thuchien(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for duan_thuchien in self.browse(cr, uid, ids, context=context):
            res[duan_thuchien.id] = {
                'kehoach_daunam': 0.0,
#                 'kehoach_thuchien': 0.0,
                'kehoach_dieuhoa': 0.0,
                'kehoach_daduyet_gannhat': 0.0,
            }
            kehoach_daunam = kehoach_thuchien = kehoach_daduyet_gannhat = vondi = vonden = dieuchinh = 0.0
            for line in duan_thuchien.kehoach_thuchien_lines:
                kehoach_thuchien += line.sotien
                
            sql = '''
                select * from kehoach_dieuchinh where duan_dautu_thuchien_id =%s and name = 0
            '''%(duan_thuchien.id)
            cr.execute(sql)
            kehoach_dieuchinh_ids = [row[0] for row in cr.fetchall()]
            if kehoach_dieuchinh_ids:
                for line in self.pool.get('kehoach.dieuchinh').browse(cr, uid, kehoach_dieuchinh_ids):
                    kehoach_daunam += line.kehoach_thuchien
            else:
                kehoach_daunam = kehoach_thuchien
                
            for line in duan_thuchien.chuyenvon_den_duan_khac_lines:
                vondi += line.sotien
                
            for line in duan_thuchien.von_den_tu_duan_khac_lines:
                vonden += line.sotien
            
#             for line in duan_thuchien.kehoach_thuchien_lines:
#                 kehoach_daduyet_gannhat += line.sotien
            if duan_thuchien.kehoach_dieuchinh_line:
                sql = '''
                    select * from kehoach_dieuchinh where duan_dautu_thuchien_id =%s and name in (select max(name) from kehoach_dieuchinh where duan_dautu_thuchien_id =%s)
                '''%(duan_thuchien.id,duan_thuchien.id)
                cr.execute(sql)
                kehoach_dieuchinh_ids = [row[0] for row in cr.fetchall()]
                for line in self.pool.get('kehoach.dieuchinh').browse(cr, uid, kehoach_dieuchinh_ids):
                    dieuchinh = line.kehoach_thuchien
            else:
                for line in duan_thuchien.kehoach_thuchien_lines:
                    dieuchinh += line.sotien
                dieuchinh
            res[duan_thuchien.id]['kehoach_daduyet_gannhat'] = kehoach_thuchien + vonden - vondi
            res[duan_thuchien.id]['kehoach_daunam'] = kehoach_daunam
            res[duan_thuchien.id]['kehoach_dieuhoa'] = dieuchinh + vonden - vondi
        return res
    
    def _get_kehoach_thuchien_from_nguonvon(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('kehoach.thuchien').browse(cr, uid, ids, context=context):
            result[line.duan_dautu_thuchien_id.id] = True
        kehoach_dieuchinh_obj = self.pool.get('kehoach.dieuchinh')
        for thuchien in self.browse(cr, uid, ids):
            kehoach_dieuchinh_ids = kehoach_dieuchinh_obj.search(cr, uid, [('id','=',thuchien.kehoach_dieuchinh_id.id)], context=context)
            for line in kehoach_dieuchinh_obj.browse(cr, uid, kehoach_dieuchinh_ids, context=context):
                result[line.duan_dautu_thuchien_id.id] = True
        return result.keys()
    
    def _get_kehoach_dieuchinh_from_dieuchinh(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('kehoach.dieuchinh').browse(cr, uid, ids, context=context):
            result[line.duan_dautu_thuchien_id.id] = True
        return result.keys()
    
    def _get_duan_thuchien_from_thuchien(self, cr, uid, ids, context=None):
        result = {}
        kehoach_dieuchinh_obj = self.pool.get('kehoach.dieuchinh')
        for thuchien in self.browse(cr, uid, ids):
            kehoach_dieuchinh_ids = kehoach_dieuchinh_obj.search(cr, uid, [('id','=',thuchien.kehoach_dieuchinh_id.id)], context=context)
            for line in kehoach_dieuchinh_obj.browse(cr, uid, kehoach_dieuchinh_ids, context=context):
                result[line.duan_dautu_thuchien_id.id] = True
        return result.keys()
    
#     def _get_kehoach_dieuchinh_from_nguonvon(self, cr, uid, ids, context=None):
#         result = {}
#         for line in self.pool.get('kehoach.dieuchinh').browse(cr, uid, ids, context=context):
#             result[line.duan_dautu_thuchien_id.id] = True
#         return result.keys()
#     
    def _get_chuyenvon_den_duan_khac(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('chuyenvon.den.duan.khac').browse(cr, uid, ids, context=context):
            result[line.duan_thuhien_id.id] = True
            result[line.duan_thuhien_den_id.id] = True
        return result.keys()
    
    def _compute_tongmuc_dautu(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for duan in self.browse(cr, uid, ids, context=context):
            res[duan.id] = {
                'tongmuc_dautu': duan.duan_dautu_id.tongmuc_dautu,
            }
        return res
    
    def _get_duan_dautu_from_duan_thuchien(self, cr, uid, ids, context=None):
        result = {}
        duan_dautu_thuchien_ids = self.pool.get('duan.dautu.thuchien').search(cr, uid, [('duan_dautu_id','in',ids)], context=context)
        for duan_dautu_thuchien_id in duan_dautu_thuchien_ids:
            result[duan_dautu_thuchien_id] = True
        return result.keys()
    
    def _compute_tong_dutoan(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for duan in self.browse(cr, uid, ids, context=context):
            res[duan.id] = {
                'tong_dutoan': 0.0,
            }
            tongdu_toan = 0.0
            for tongdutoan in duan.duan_dautu_id.pheduyet_tdt_lines:
                tongdu_toan += tongdutoan.pheduyet_tdt_tongdutoan
            res[duan.id]['tong_dutoan'] = tongdu_toan
        return res
    
    def _compute_luyke_capphat_namtruoc(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for duan in self.browse(cr, uid, ids, context=context):
            res[duan.id] = {
                'luyke_capphat_namtruoc': 0.0,
            }
            luyke_capphat_namtruoc = 0.0
            duan_thuchien_ids = self.search(cr, uid, [('id','!=',duan.id),('duan_dautu_id','=',duan.duan_dautu_id.id),('nam','<',duan.nam)])
            for duan_thuchien in self.browse(cr, uid, duan_thuchien_ids):
                luyke_capphat_namtruoc += duan_thuchien.sotien_capphat
            res[duan.id]['luyke_capphat_namtruoc'] = luyke_capphat_namtruoc
            if duan.duan_dautu_id.nam_luy_ke and duan.duan_dautu_id.nam_luy_ke < duan.nam:
                res[duan.id]['luyke_capphat_namtruoc'] += duan.duan_dautu_id.sotien_luy_ke
        return res
    
    def _compute_sotien_con_cothe_capphat(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        property_pool = self.pool.get('admin.property')
        phantram = 0
        property_obj = property_pool._get_project_property_by_name(cr, uid, 'default_phantram_sotien_cothe_botrivon') or None
        phantram = int(property_obj.value)
        for duan in self.browse(cr, uid, ids, context=context):
            if duan.tong_dutoan==0:
                res[duan.id] = (duan.tongmuc_dautu*phantram/100)-duan.luyke_capphat_namtruoc-duan.sotien_capphat
            else:
                res[duan.id] = duan.tong_dutoan-duan.luyke_capphat_namtruoc-duan.sotien_capphat
        return res
    
    def _compute_kehoach_daduyet_gannhat(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for duan in self.browse(cr, uid, ids, context=context):
#             nam = int(duan.nam)-1
#             duan_thuchien_ids = self.search(cr, uid, [('id','!=',duan.id),('duan_dautu_id','=',duan.duan_dautu_id.id),('nam','=',str(nam))])
#             kehoach_daduyet_gannhat = 0
#             for duan_thuchien in self.browse(cr, uid, ids):
#                 kehoach_daduyet_gannhat = duan_thuchien.kehoach_dieuhoa
#             res[duan.id] = kehoach_daduyet_gannhat
            res[duan.id] = duan.kehoach_dieuhoa
        return res
    
    _columns = {
        'nam': fields.char('Năm', size=5, required=True),
        'duyet': fields.boolean('Đã duyệt'),
        'nguoithuchien_id': fields.many2one('hr.employee', 'Người thực hiện', required=True),
        'duan_dautu_id': fields.many2one('duan.dautu', 'Dự án đầu tư', ondelete='cascade'),
        'danhmuc_id': fields.related('duan_dautu_id', 'danhmuc_id', type='many2one', relation='duan.danhmuc', string='Ngành', readonly=True,
                                     store={
                'duan.dautu.thuchien': (lambda self, cr, uid, ids, c={}: ids, ['duan_dautu_id'], 10),
                'duan.dautu': (_when_changing_danhmucid_from_duan, ['danhmuc_id'], 10),
            }),
        'linhvuc_id': fields.related('duan_dautu_id', 'linhvuc_id', type='many2one', relation='duan.danhmuc', string='Lĩnh vực', readonly=True,
                                     store={
                'duan.dautu.thuchien': (lambda self, cr, uid, ids, c={}: ids, ['duan_dautu_id'], 10),
                'duan.dautu': (_when_changing_danhmucid_from_duan, ['linhvuc_id'], 10),
            }),
        'nhom_id': fields.related('duan_dautu_id', 'nhom_id', type='many2one', relation='duan.nhom', string='Nhóm', readonly=True,
                                     store={
                'duan.dautu.thuchien': (lambda self, cr, uid, ids, c={}: ids, ['duan_dautu_id'], 10),
                'duan.dautu': (_when_changing_danhmucid_from_duan, ['nhom_id'], 10),
            }),
        'tinh_tp_id': fields.related('duan_dautu_id', 'tinh_tp_id', type='many2one', relation='res.country.state', string='Tỉnh/TP', readonly=True,
                                     store={
                'duan.dautu.thuchien': (lambda self, cr, uid, ids, c={}: ids, ['duan_dautu_id'], 10),
                'duan.dautu': (_when_changing_danhmucid_from_duan, ['tinh_tp_id'], 10),
            }),
        'quan_huyen_id': fields.related('duan_dautu_id', 'quan_huyen_id', type='many2one', relation='quan.huyen', string='Quận huyện', readonly=True,
                                     store={
                'duan.dautu.thuchien': (lambda self, cr, uid, ids, c={}: ids, ['duan_dautu_id'], 10),
                'duan.dautu': (_when_changing_danhmucid_from_duan, ['quan_huyen_id'], 10),
            }),
        'tongmuc_dautu': fields.function(_compute_tongmuc_dautu, type='float', digits=(16,0), string='Tổng mức đầu tư',
                                     store={
                    'duan.dautu.thuchien': (lambda self, cr, uid, ids, c={}: ids, ['duan_dautu_id'], 10),
                    'duan.dautu': (_get_duan_dautu_from_duan_thuchien, ['nguon_von_ids','quyetdinh_dautu_lines'], 10),
                   },
                   multi='tongmuc_dautu'),
        'tong_dutoan': fields.function(_compute_tong_dutoan, type='float', digits=(16,0), string='Tổng dự toán',
                                     store={
                    'duan.dautu.thuchien': (lambda self, cr, uid, ids, c={}: ids, ['duan_dautu_id'], 10),
                    'duan.dautu': (_get_duan_dautu_from_duan_thuchien, ['pheduyet_tdt_lines'], 10),
                   },
                   multi='tong_dutoan'),
        'luyke_capphat_namtruoc': fields.function(_compute_luyke_capphat_namtruoc, type='float', digits=(16,0), string='Lũy kế cấp phát (cuối năm trước)',
                                     store={
                    'duan.dautu.thuchien': (lambda self, cr, uid, ids, c={}: ids, ['thuchien_chitiet','duan_dautu_id'], 10),
                    'duan.dautu.thuchien.chitiet': (_get_duan_dautu_thuchien_chitiet, ['sotien'], 10),
                    'duan.dautu': (_get_duan_dautu_from_duan_thuchien, ['nam_luy_ke','sotien_luy_ke'], 10),
                   },
                   multi='luyke_capphat_namtruoc'),
#         'kehoach_daduyet_gannhat': fields.function(_compute_kehoach_daduyet_gannhat, type='float', digits=(16,0), string='Kế khoạch đã duyệt (kỳ gần nhất)'),
        'kehoach_daduyet_gannhat': fields.function(_compute_kehoach_thuchien, type='float', digits=(16,0), string='Kế khoạch đã duyệt (kỳ gần nhất)',
            store={
                'duan.dautu.thuchien': (lambda self, cr, uid, ids, c={}: ids, ['kehoach_thuchien_lines','chuyenvon_den_duan_khac_lines','von_den_tu_duan_khac_lines','kehoach_dieuchinh_line','duan_dautu_id'], 10),
                'kehoach.thuchien': (_get_kehoach_thuchien_from_nguonvon, ['sotien','nguonvon_id'], 20),
                'chuyenvon.den.duan.khac': (_get_chuyenvon_den_duan_khac, ['sotien','duan_thuhien_den_id'], 20),
            },
            multi='kehoach_thuchien'),
        'kehoach_daunam': fields.function(_compute_kehoach_thuchien, type='float', digits=(16,0), string='Kế hoạch đầu năm',
                store={
                    'duan.dautu.thuchien': (lambda self, cr, uid, ids, c={}: ids, ['kehoach_dieuchinh_line','duan_dautu_id'], 10),
                    'kehoach.dieuchinh': (_get_kehoach_dieuchinh_from_dieuchinh, ['kehoach_thuchien_line'], 10),
#                     'kehoach.thuchien': (_get_duan_thuchien_from_thuchien, ['nguonvon_id','sotien'], 10),
                    'kehoach.thuchien': (_get_kehoach_thuchien_from_nguonvon, ['nguonvon_id','sotien'], 10),
                   },
                   multi='kehoach_thuchien'),
#         'kehoach_thuchien': fields.function(_compute_kehoach_thuchien, type='float', digits=(16,0), string='Kế hoạch đầu năm',
#                 store={
#                     'duan.dautu.thuchien': (lambda self, cr, uid, ids, c={}: ids, ['kehoach_thuchien_lines','duan_dautu_id'], 10),
#                     'kehoach.thuchien': (_get_kehoach_thuchien_from_nguonvon, ['nguonvon_id','sotien'], 10),
#                    },
#                    multi='kehoach_thuchien'),
        'kehoach_dieuhoa': fields.function(_compute_kehoach_thuchien, type='float', digits=(16,0), string='Kế hoạch cập nhật',
            store={
                'duan.dautu.thuchien': (lambda self, cr, uid, ids, c={}: ids, ['kehoach_thuchien_lines','chuyenvon_den_duan_khac_lines','von_den_tu_duan_khac_lines','kehoach_dieuchinh_line','duan_dautu_id'], 20),
                'kehoach.dieuchinh': (_get_kehoach_dieuchinh_from_dieuchinh, ['kehoach_thuchien_line'], 20),
                'kehoach.thuchien': (_get_kehoach_thuchien_from_nguonvon, ['sotien','nguonvon_id'], 20),
#                 'kehoach.thuchien': (_get_duan_thuchien_from_thuchien, ['nguonvon_id','sotien'], 20),
                'chuyenvon.den.duan.khac': (_get_chuyenvon_den_duan_khac, ['sotien','duan_thuhien_den_id'], 20),
            },
            multi='kehoach_thuchien'),
        
        'currency_id': fields.many2one('res.currency', 'Tiền Tệ'),
        
        'sotien_capphat': fields.function(_amount_total, string='Giá trị cấp phát', digits=(16,0),
            store={
                'duan.dautu.thuchien': (lambda self, cr, uid, ids, c={}: ids, ['thuchien_chitiet','duan_dautu_id'], 10),
                'duan.dautu.thuchien.chitiet': (_get_duan_dautu_thuchien_chitiet, ['sotien'], 10),
            },
            multi='sums', track_visibility='always'),
        'khoiluong_thuchien': fields.function(_amount_total, string='Khối lượng thực hiện', digits=(16,0),
            store={
                'duan.dautu.thuchien': (lambda self, cr, uid, ids, c={}: ids, ['thuchien_chitiet','duan_dautu_id'], 10),
                'duan.dautu.thuchien.chitiet': (_get_duan_dautu_thuchien_chitiet, ['khoiluong_thuchien'], 10),
            },
            multi='sums', track_visibility='always'),
        'khoiluong_hoanthanh': fields.function(_amount_total, string='Khối lượng hoàn thành', digits=(16,0),
            store={
                'duan.dautu.thuchien': (lambda self, cr, uid, ids, c={}: ids, ['thuchien_chitiet','duan_dautu_id'], 10),
                'duan.dautu.thuchien.chitiet': (_get_duan_dautu_thuchien_chitiet, ['khoiluong_hoanthanh'], 10),
            },
            multi='sums', track_visibility='always'),
        'khoiluong_nghiemthu': fields.function(_amount_total, string='Khối lượng nghiệm thu', digits=(16,0),
            store={
                'duan.dautu.thuchien': (lambda self, cr, uid, ids, c={}: ids, ['thuchien_chitiet','duan_dautu_id'], 10),
                'duan.dautu.thuchien.chitiet': (_get_duan_dautu_thuchien_chitiet, ['khoiluong_nghiemthu'], 10),
            },
            multi='sums', track_visibility='always'),
        'sotien_con_cothe_capphat': fields.function(_compute_sotien_con_cothe_capphat, type='float', digits=(16,0), string='Số tiền còn có thể bố trí vốn', help='Nếu có tổng dự toán thì Số tiền còn có thể bố trí vốn = tổng dự toán - Lũy kế cấp phát (cuối năm trước) - Số tiền cấp phát. Nếu không có tổng dự toán thì Số tiền còn có thể bố trí vốn = 90%(Kế hoạch đầu năm) - Lũy kế cấp phát (cuối năm trước) - Số tiền cấp phát',
             store={
                    'duan.dautu.thuchien': (lambda self, cr, uid, ids, c={}: ids, ['duan_dautu_id','thuchien_chitiet'], 30),
                    'duan.dautu': (_get_duan_dautu_from_duan_thuchien, ['nguon_von_ids','pheduyet_tdt_lines'], 30),
                    'duan.dautu.thuchien.chitiet': (_get_duan_dautu_thuchien_chitiet, ['sotien'], 30),
                   }),
        'noidung': fields.text('Nội dung'),
        
        'thuchien_chitiet': fields.one2many('duan.dautu.thuchien.chitiet', 'duan_dautu_thuchien_id', 'Chi tiết thực hiện'),
        'chuyenvon_den_duan_khac_lines': fields.one2many('chuyenvon.den.duan.khac', 'duan_thuhien_id', 'Chuyển vốn đến dự án khác'),
        'von_den_tu_duan_khac_lines': fields.one2many('chuyenvon.den.duan.khac', 'duan_thuhien_den_id', 'Vốn đến từ dự án khác'),
        'giai_doan_id': fields.many2one('duan.giaidoan','Giai đoạn', required=True,domain="[('giaidoan_cha','!=',False)]"),
        'giaidoan_cha': fields.related('giai_doan_id','giaidoan_cha', type='many2one', relation='duan.giaidoan', string='Giai đoạn cha',store=True),
        'quan_huyen_id': fields.related('duan_dautu_id','quan_huyen_id', type='many2one', relation='quan.huyen', string='Địa bàn',store=True),
        'nha_dau_tu_id': fields.related('duan_dautu_id','nha_dau_tu_id', type='many2one', relation='res.partner', string='Chủ đầu tư'),
        'ten_viet_tat': fields.related('nha_dau_tu_id','ten_viet_tat', type='char', string='Chủ đầu tư',store=True),
        'kehoach_thuchien_lines': fields.one2many('kehoach.thuchien', 'duan_dautu_thuchien_id', 'Kế hoạch thực hiện'),
        'nguonvon_id': fields.related('kehoach_thuchien_lines','nguonvon_id', relation='nguon.von',type='many2one',string="Nguồn vốn",store=False),
        'kehoach_dieuchinh_line': fields.one2many('kehoach.dieuchinh', 'duan_dautu_thuchien_id', 'Kế hoạch điều chỉnh'),
        'chudautu_dexuat': fields.float('Chủ đầu tư đề xuất', digits=(16,0)),
        'uoc_thuchien': fields.float('Ước thực hiện', digits=(16,0)),
    }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
#         if context.get('search_nguonvon_of_duan'):
        if context.get('search_thuchien_of_duan')==False:
            args += [('id','=',-1)]
        if context.get('search_thuchien_of_duan'):
            duan_dautu_id = context.get('search_thuchien_of_duan')
            sql = ''' select id from duan_dautu_thuchien where duan_dautu_id=%s'''%(duan_dautu_id)
            cr.execute(sql)
            thuchien_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',thuchien_ids)]
            
        if context.get('search_thuchien_den_of_duan')==False:
            args += [('id','=',-1)]
        if context.get('search_thuchien_den_of_duan'):
            duan_dautu_den_id = context.get('search_thuchien_den_of_duan')
            sql = ''' select id from duan_dautu_thuchien where duan_dautu_id=%s'''%(duan_dautu_den_id)
            cr.execute(sql)
            thuchien_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',thuchien_ids)]
        if context.get('search_nguonvon_id'):
            nguonvon = self.pool.get('nguon.von').browse(cr, uid, context.get('search_nguonvon_id'))
            child_of_ids = self.pool.get('nguon.von').search(cr, uid, [('parent_id','child_of',context.get('search_nguonvon_id'))])
            sql = '''
                SELECT id FROM duan_dautu_thuchien WHERE nam = '%s'
                    AND id in (SELECT duan_dautu_thuchien_id FROM kehoach_thuchien WHERE nguonvon_id in (%s))
            '''%(nguonvon.nam,','.join(map(str, child_of_ids)))
            cr.execute(sql)
            thuchien_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',thuchien_ids)]
        if context.get('search_kehoachvon_theonguonvon'):
            child_of_ids = self.pool.get('nguon.von').search(cr, uid, [('parent_id','child_of',context.get('search_kehoachvon_theonguonvon'))])
            sql = '''
                SELECT id FROM duan_dautu_thuchien WHERE nam = '%s'
                    AND id in (SELECT duan_dautu_thuchien_id FROM kehoach_thuchien WHERE nguonvon_id in (%s))
            '''%(time.strftime('%Y'),','.join(map(str, child_of_ids)))
            cr.execute(sql)
            thuchien_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',thuchien_ids)]
        return super(duan_dautu_thuchien, self).search(cr, uid, args, offset, limit, order, context, count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
    
    def name_get(self, cr, user, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        result = self.browse(cr, user, ids, context=context)
        res = []
        for rs in result:
            name = "%s-%s" % (rs.nam,rs.giai_doan_id.name)
            res += [(rs.id, name)]
        return res
    
    def _default_employee(self, cr, uid, context=None):
        emp_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)], context=context)
        return emp_ids and emp_ids[0] or False
    
    def _get_default_currency(self, cr, uid, context=None):
        currency_ids = self.pool.get('res.currency').search(cr, uid, [('name','=','VND')], context=context)
        return currency_ids and currency_ids[0] or False
    
    _defaults = {
                 'nam': time.strftime('%Y'),
                 'nguoithuchien_id': _default_employee,
                 'currency_id': _get_default_currency,
                 }
     
duan_dautu_thuchien()
 
class duan_dautu_thuchien_chitiet(osv.osv):
    _name = "duan.dautu.thuchien.chitiet"
    _description = "Chi Tiet Thuc Hien"
    
    def _when_changing_danhmucid_from_duan(self, cr, uid, ids, context=None):
        result = {}
        duan_dautu_thuchien_chitiet_ids = self.pool.get('duan.dautu.thuchien.chitiet').search(cr, uid, [('duan_dautu_id','in',ids)], context=context)
        for duan_dautu_thuchien_chitiet_id in duan_dautu_thuchien_chitiet_ids:
            result[duan_dautu_thuchien_chitiet_id] = True
        return result.keys()
    
    def _when_changing_kehoachvon(self, cr, uid, ids, context=None):
        result = {}
        duan_dautu_thuchien_chitiet_ids = self.pool.get('duan.dautu.thuchien.chitiet').search(cr, uid, [('duan_dautu_thuchien_id','in',ids)], context=context)
        for duan_dautu_thuchien_chitiet_id in duan_dautu_thuchien_chitiet_ids:
            result[duan_dautu_thuchien_chitiet_id] = True
        return result.keys()
    
    _columns = {
        'ngay' :fields.date('Ngày', required=True),
        
        'sotien': fields.float('Giá trị cấp phát', digits=(16,0), required=True),
        'khoiluong_thuchien': fields.float('Khối lượng thực hiện', digits=(16,0), required=True),
        'khoiluong_hoanthanh': fields.float('Khối lượng hoàn thành', digits=(16,0), required=True),
        'khoiluong_nghiemthu': fields.float('Khối lượng nghiệm thu', digits=(16,0), required=False),
        'nguoithuchien_id': fields.many2one('hr.employee', 'Người thực hiện', required=True),
        'noidung': fields.text('Nội dung'),
        'duan_dautu_thuchien_id': fields.many2one('duan.dautu.thuchien', 'Kế hoạch năm', ondelete='cascade', required=True),
        'duan_dautu_id': fields.many2one('duan.dautu', 'Dự án'),
        
        'danhmuc_id': fields.related('duan_dautu_id', 'danhmuc_id', type='many2one', relation='duan.danhmuc', string='Ngành', readonly=True,
                                     store={
                'duan.dautu': (_when_changing_danhmucid_from_duan, ['danhmuc_id'], 10),
            }),
        'linhvuc_id': fields.related('duan_dautu_id', 'linhvuc_id', type='many2one', relation='duan.danhmuc', string='Lĩnh vực', readonly=True,
                                     store={
                'duan.dautu': (_when_changing_danhmucid_from_duan, ['linhvuc_id'], 10),
            }),
        'nam': fields.related('duan_dautu_thuchien_id', 'nam', type='char', string='Năm', readonly=True,
                                     store={
                'duan.dautu.thuchien': (_when_changing_kehoachvon, ['nam'], 10),
            }),
        'giai_doan_id': fields.related('duan_dautu_thuchien_id', 'giai_doan_id', type='many2one', relation='duan.giaidoan', string='Giai đoạn', readonly=True,
                                     store={
                'duan.dautu.thuchien': (_when_changing_kehoachvon, ['giai_doan_id'], 10),
            }),
    }
    
    def create(self, cr, uid, vals, context=None):
        dadt_thuchien_obj = self.pool.get('duan.dautu.thuchien')
        dadt_thuchien_id = dadt_thuchien_obj.search(cr, uid, [('id','=',vals['duan_dautu_thuchien_id'])])
        dadt_thuchien = dadt_thuchien_obj.browse(cr, uid, dadt_thuchien_id)[0]
        vals.update({'duan_dautu_id': dadt_thuchien.duan_dautu_id.id})
        return super(duan_dautu_thuchien_chitiet, self).create(cr, uid, vals, context)
    
    def _default_employee(self, cr, uid, context=None):
        emp_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)], context=context)
        return emp_ids and emp_ids[0] or False
     
    _defaults = {
                 'nguoithuchien_id': _default_employee,
                 'ngay': time.strftime('%Y-%m-%d'),
                 }
     
duan_dautu_thuchien_chitiet()

class khdt_nam(osv.osv):
    _name = "khdt.nam"
    _columns = {
        'name': fields.char('Năm', required=True, size=5),
    }
    
khdt_nam()

class khdt_truong_dulieu(osv.osv):
    _name = "khdt.truong.dulieu"
    _columns = {
        'name': fields.char('Trường dữ liệu', required=True, size=1024),
    }
    
khdt_truong_dulieu()
