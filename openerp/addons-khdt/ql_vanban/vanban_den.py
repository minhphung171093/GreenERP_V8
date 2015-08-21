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

from openerp import addons
import logging
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import tools
from openerp.addons.xlrd import open_workbook
from openerp import modules
import os
base_path = os.path.dirname(modules.get_module_path('ql_vanban'))
_logger = logging.getLogger(__name__)

class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {
        'nguoi_lanh_dao_id': fields.many2one('hr.employee','Tên người lãnh đạo'),
        'ma': fields.char('Mã', size=64),
    }
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_vanban/data/co_quan.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    ten_lanhdao = s.cell(row,0).value
                    ma = s.cell(row,1).value
                    ten_coquan = s.cell(row,2).value
                    danhmuc_ids = self.search(cr, 1, [('name','=',ten_coquan)])
                    if not danhmuc_ids:
                        nguoi_lanh_dao_ids = self.pool.get('hr.employee').search(cr, 1, [('name','=',ten_lanhdao)])
                        if nguoi_lanh_dao_ids:
                            self.create(cr, 1, {'name': ten_coquan,'nguoi_lanh_dao_id':nguoi_lanh_dao_ids[0],'ma':ma})
                            
res_company()

class cap_goi(osv.osv):
    _name = "cap.goi"
    _description = "Cap goi"
    _columns = {
        'name': fields.char('Tên cấp văn bản', size=64, required=True),
    }
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_vanban/data/cap_goi.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    ten = s.cell(row,0).value
                    danhmuc_ids = self.search(cr, 1, [('name','=',ten)])
                    if not danhmuc_ids:
                        self.create(cr, 1, {'name': ten})
                          
cap_goi()

class noi_phathanh(osv.osv):
    _name = "noi.phathanh"
    _description = "Noi phat hanh"
    _columns = {
        'name': fields.char('Tên đơn vị', size=64, required=True),
        'ky_hieu': fields.char('Ký hiệu', size=64, required=True),
        'ghi_chu': fields.text('Ghi chú'),
    }
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_vanban/data/noi_phat_hanh.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    ky_hieu = s.cell(row,0).value
                    ten = s.cell(row,1).value
                    ghi_chu = s.cell(row,2).value
                    danhmuc_ids = self.search(cr, 1, [('ky_hieu','=',ky_hieu)])
                    if not danhmuc_ids:
                        self.create(cr, 1, {'name': ten,'ky_hieu':ky_hieu,'ghi_chu':ghi_chu})
noi_phathanh()

class loai_sovanban(osv.osv):
    _name = "loai.sovanban"
    _description = "Loai so van ban"
    _columns = {
        'name': fields.char('Tên loại sổ văn bản', size=64, required=True),
        'ky_hieu': fields.char('Ký hiệu', size=64, required=True),
    }
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_vanban/data/loai_so_van_ban.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    ten = s.cell(row,0).value
                    ky_hieu = s.cell(row,1).value
                    danhmuc_ids = self.search(cr, 1, [('ky_hieu','=',ky_hieu)])
                    if not danhmuc_ids:
                        self.create(cr, 1, {'name': ten,'ky_hieu':ky_hieu})
                        
loai_sovanban()

class so_vanban(osv.osv):
    _name = "so.vanban"
    _description = "So van ban"
    _columns = {
        'name': fields.char('Loại sổ văn bản', size=64, required=True),
        'co_quan_id': fields.many2one('res.company','Cơ quan', required=True),
        'ngay_tao': fields.date('Ngày tạo'),
        'nam': fields.integer('Năm'),
        'so_hien_tai': fields.integer('Số hiện tại'),
    }
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_vanban/data/so_van_ban.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    loai = s.cell(row,0).value
                    co_quan = s.cell(row,1).value
                    ngay_tao = s.cell(row,2).value
                    nam = s.cell(row,3).value
                    so_hien_tai = s.cell(row,4).value
                    danhmuc_ids = self.search(cr, 1, [('name','=',loai)])
                    if not danhmuc_ids:
                        co_quan_ids = self.pool.get('res.company').search(cr, 1, [('name','=',co_quan)])
                        if co_quan_ids:
                            self.create(cr, 1, {'name': loai,'co_quan':co_quan_ids[0],'ngay_tao':ngay_tao,'nam':nam,'so_hien_tai':so_hien_tai})
                        
so_vanban()

class loai_vanban(osv.osv):
    _name = "loai.vanban"
    _description = "Loai van ban"
    _columns = {
        'name': fields.char('Tên loại văn bản', size=64, required=True),
        'ky_hieu': fields.char('Ký hiệu', size=64, required=True),
    }
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_vanban/data/loai_van_ban.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    ten = s.cell(row,0).value
                    ky_hieu = s.cell(row,1).value
                    danhmuc_ids = self.search(cr, 1, [('ky_hieu','=',ky_hieu)])
                    if not danhmuc_ids:
                        self.create(cr, 1, {'name': ten,'ky_hieu':ky_hieu})
                        
loai_vanban()

class do_mat(osv.osv):
    _name = "do.mat"
    _description = "Do mat"
    _order = "thu_tu"
    _columns = {
        'name': fields.char('Tên độ khẩn', size=64, required=True),
        'ma': fields.char('Mã độ khẩn', size=64, required=True),
        'thu_tu': fields.integer('Thứ tự ưu tiên sắp xếp', required=True),
    }
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_vanban/data/do_mat.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    ten = s.cell(row,0).value
                    ma = s.cell(row,1).value
                    thu_tu = s.cell(row,2).value
                    danhmuc_ids = self.search(cr, 1, [('ma','=',ma)])
                    if not danhmuc_ids:
                        self.create(cr, 1, {'name': ten,'ma':ma,'thu_tu':thu_tu})
                        
do_mat()

class do_khan(osv.osv):
    _name = "do.khan"
    _description = "Do khan"
    _columns = {
        'name': fields.char('Tên độ khẩn', size=64, required=True),
        'ma': fields.char('Mã độ khẩn', size=64, required=True),
    }
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_vanban/data/do_khan.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    ten = s.cell(row,0).value
                    ma = s.cell(row,1).value
                    danhmuc_ids = self.search(cr, 1, [('ma','=',ma)])
                    if not danhmuc_ids:
                        self.create(cr, 1, {'name': ten,'ma':ma})
                        
do_khan()

class hr_employee_category(osv.osv):
    _inherit = "hr.employee.category"
    _columns = {
        'ma': fields.char('Mã', size=64),
        'mota': fields.char('Mô tả', size=128),
    }
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_vanban/data/chuc_vu.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    ma = s.cell(row,0).value
                    ten = s.cell(row,1).value
                    mota = s.cell(row,2).value
                    danhmuc_ids = self.search(cr, 1, [('ma','=',ma)])
                    if not danhmuc_ids:
                        self.create(cr, 1, {'name': ten,'ma':ma,'mota':mota})
         
hr_employee_category()

class linh_vuc(osv.osv):
    _name = "linh.vuc"
    _description = "Linh vuc"
    _columns = {
        'name': fields.char('Tên', size=64, required=True),
    }
linh_vuc()

class so_vanban_noibo(osv.osv):
    _name = "so.vanban.noibo"
    _description = "So van ban noi bo"
    _columns = {
        'name': fields.char('Tên sổ văn bản nội bộ', size=64, required=True),
        'ky_hieu': fields.char('Mã sổ văn bản nội bộ', size=64, required=True),
        'mota': fields.char('Mô tả sổ văn bản nội bộ', size=128),
        'loai_vb_nb_ids': fields.many2many('loai.vanban.noibo','so_loai_vanban_noibo_ref','so_id','loai_id','Cấu hình loại văn bản nội bộ'),
        'phong_ban_ids': fields.many2many('hr.department','so_phongban_vanban_noibo_ref','so_id','hr_department_id','Cấu hình phòng ban'),
    }
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_vanban/data/so_van_ban_noi_bo.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    ky_hieu = s.cell(row,0).value
                    ten = s.cell(row,1).value
                    mota = s.cell(row,2).value
                    danhmuc_ids = self.search(cr, 1, [('ky_hieu','=',ky_hieu)])
                    if not danhmuc_ids:
                        self.create(cr, 1, {'name': ten,'ky_hieu':ky_hieu,'mota':mota})
         
so_vanban_noibo()

class loai_vanban_noibo(osv.osv):
    _name = "loai.vanban.noibo"
    _description = "Loai van ban noi bo"
    _columns = {
        'name': fields.char('Tên loại văn bản nội bộ', size=64, required=True),
        'ky_hieu': fields.char('Ký hiệu loại văn bản nội bộ', size=64, required=True),
        'mota': fields.char('Mô tả loại văn bản nội bộ', size=128),
    }
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_vanban/data/loai_van_ban_noi_bo.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    ky_hieu = s.cell(row,0).value
                    ten = s.cell(row,1).value
                    mota = s.cell(row,2).value
                    danhmuc_ids = self.search(cr, 1, [('ky_hieu','=',ky_hieu)])
                    if not danhmuc_ids:
                        self.create(cr, 1, {'name': ten,'ky_hieu':ky_hieu,'mota':mota})
         
loai_vanban_noibo()

class vanban_den(osv.osv):
    _name = "vanban.den"
    _description = "Van ban den"
    _columns = {
        'name': fields.char('Số ký hiệu gốc', size=64, required=True),
        'so_vanban_id': fields.many2one('so.vanban','Sổ văn bản'),
        'so_den_theo_so': fields.char('Số đến theo sổ', size=64),
        'linh_vuc_id': fields.many2one('linh.vuc','Lĩnh vực'),
        'ngay_den': fields.date('Ngày đến'),
        'ngay_phat_hanh': fields.date('Ngày phát hành', required=True),
        'donvi_saoy': fields.char('Đơn vị phát hành', size=64),
        'nguoi_ky_id': fields.many2one('hr.employee','Người ký'),
        'do_khan_id': fields.many2one('do.khan','Độ khẩn'),
        'so_to': fields.char('Số tờ', size=64),
        'trich_yeu': fields.text('Trích yếu', required=True),
        'loai_vanban_id': fields.many2one('loai.vanban','Loại văn bản'),
        'vanban_qppl': fields.boolean('Văn bản QPPL'),
        'cap_goi_id': fields.many2one('cap.goi','Cấp gởi'),
        'noi_phathanh_id': fields.many2one('noi.phathanh','Nơi phát hành', required=True),
        'khac': fields.char('Khác', size=64),
        'so_vanban_di_phucdap': fields.char('Số văn bản đi phúc đáp', size=64),
        'do_mat_id': fields.many2one('do.mat','Độ mật'),
        'hoso_lines': fields.one2many('ir.attachment','vanban_den_id','Tập tin đính kèm',required=True),
        'state': fields.selection([('moitao','Mới Tạo'),('dangxuly','Đang xử lý'),('daxuly','Đã xử lý')], 'Tình trạng'),
    }
    
    _defaults = {
        'state': 'moitao',
    }
    
    def create(self, cr, uid, vals, context=None):
        if 'hoso_lines' in vals and len(vals['hoso_lines'])==0:
            raise osv.except_osv(_('Cảnh báo!'),
                            _('Vui lòng đính kèm tập tin!')) 
        return super(vanban_den,self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(vanban_den,self).write(cr, uid, ids, vals, context)
        for line in self.browse(cr, uid, ids):
            if len(line.hoso_lines)==0:
                raise osv.except_osv(_('Cảnh báo!'),
                                _('Vui lòng đính kèm tập tin!')) 
        return new_write
    
vanban_den()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
