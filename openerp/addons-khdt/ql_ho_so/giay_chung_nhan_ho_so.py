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
_logger = logging.getLogger(__name__)
import os
from openerp import modules
import time
base_path = os.path.dirname(modules.get_module_path('ql_ho_so'))
class loai_ho_so(osv.osv):
    _name = "loai.ho.so"
    _description = "Loai Ho So"
    _columns = {
        'name': fields.char('Tên', size=256, required=True),
        'ma': fields.char('Mã', size=5, ),
        'dodai_ma': fields.char('Độ dài mã', size=5, ),
    }
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_ho_so/data/LoaiHoSo.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    val0 = s.cell(row,0).value
                    danhmuc_ids = self.search(cr, 1, [('name','=',val0)])
                    if not danhmuc_ids:
                        self.create(cr, 1, {'name': val0})
loai_ho_so()

class res_partner_category(osv.osv):
    _inherit = "res.partner.category"
    _columns={
        'ma': fields.char('Mã', size=5, required=True),
    }
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_ho_so/data/LoaiHinhDoanhNghiep.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    val0 = s.cell(row,0).value
                    val1 = s.cell(row,1).value
                    danhmuc_ids = self.search(cr, 1, [('name','=',val0)])
                    if not danhmuc_ids:
                        self.create(cr, 1, {'name': val0,'ma': val1})
res_partner_category()

class hinh_thuc_dau_tu(osv.osv):
    _name = "hinh.thuc.dau.tu"
    _description = "Hinh Thuc Dau Tu"
    _columns = {
        'name': fields.char('Hình Thức Đầu Tư', size=256, required=True),
        'ma': fields.char('Mã', size=5, required=True),
    }
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_ho_so/data/HinhThucDauTu.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    val0 = s.cell(row,0).value
                    val1 = s.cell(row,1).value
                    danhmuc_ids = self.search(cr, 1, [('name','=',val0)])
                    if not danhmuc_ids:
                        self.create(cr, 1, {'name': val0,'ma': val1})
hinh_thuc_dau_tu()

class nganh_nghe(osv.osv):
    _name = "nganh.nghe"
    _description = "Nganh Nghe"
    _columns = {
        'name': fields.char('Tên ngành', size=64, required=True),
        'ma_nganh': fields.char('Mã ngành', size=64, required=True),
    }
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_ho_so/data/NganhNghe.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    val0 = s.cell(row,0).value
                    val1 = s.cell(row,1).value
                    danhmuc_ids = self.search(cr, 1, [('ma_nganh','=',val1)])
                    if not danhmuc_ids:
                        self.create(cr, 1, {'name': val0,'ma_nganh': val1})
    
nganh_nghe()

class khu_vuc(osv.osv):
    _name = "khu.vuc"
    _description = "Khu vuc"
    _columns = {
        'name': fields.char('Tên khu vực', size=64, required=True),
        'country_id': fields.many2one('res.country', 'Country',required=True),
        'tinh_tp_id': fields.many2one('res.country.state', 'Tỉnh/TP', required=True, domain="[('country_id','=',country_id)]"),
    }
    
    def _get_default_country(self, cr, uid, context=None):
        country_ids = self.pool.get('res.country').search(cr, uid, [('code','=','VN')], context=context)
        return country_ids and country_ids[0] or False
    
    _defaults = {
        'country_id': _get_default_country,
    }
khu_vuc()

class giay_thanhlap(osv.osv):
    _name = "giay.thanhlap"
    _description = "Giay thanh lap"
    _columns = {
        'name': fields.char('Tên', size=256),
        'so': fields.char('Số', size=256),
        'ngay_cap': fields.date('Ngày cấp'),
        'partner_id': fields.many2one('res.partner', 'Nhà đầu tư', ondelete='cascade'),
    }
giay_thanhlap()

class nha_dau_tu(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'ngay_sinh': fields.date('Ngày sinh'),
        'quoc_tich': fields.many2one('res.country', 'Quốc tịch'),
        
        'giay_thanhlap_id': fields.one2many('giay.thanhlap','partner_id','Giấy thành lập'),
#         'giay_thanh_lap_so': fields.char('Giấy thành lập số', size=64),
#         'ngay_cap_phep_thanh_lap': fields.date('Ngày cấp'),
        'noi_cap_phep_thanh_lap': fields.char('Nơi cấp', size=64),
        
        'cmnd_ho_chieu': fields.selection([('cmnd','Chứng minh nhân dân'),('hc','Hộ chiếu')], 'CMND/Hộ chiếu'),
        'so_cmnd_hochieu': fields.char('Số', size=64),
        'ngay_cap_cmnd_hc': fields.date('Ngày cấp'),
        'noi_cap_cmnd_hc': fields.char('Nơi cấp', size=64),
        
        'gioitinh': fields.selection([('nam','Nam'),('nu','Nữ')], 'Giới tính'),
        
        'dia_chi_thuong_tru': fields.char('Địa chỉ thường trú', size=1024),
        'ten_viet_tat': fields.char('Tên viết tắt', size=2014),
        'phan_he': fields.selection([('hosodautu','Hồ sơ đầu tư')], 'Phân Hệ'),
    }
    
    def create(self, cr, uid, vals, context=None):
        if vals['is_company']==True:
            vals['title'] = False
            vals['function'] = False
            vals['ngay_sinh'] = False
            vals['quoc_tich'] = False
            vals['gioitinh'] = False
            vals['cmnd_ho_chieu'] = False
            vals['so_cmnd_hochieu'] = ''
            vals['ngay_cap_cmnd_hc'] = False
            vals['noi_cap_cmnd_hc'] = ''
        if vals['is_company']==False:
            vals['giay_thanh_lap_so'] = ''
            vals['ngay_cap_phep_thanh_lap'] = False
            vals['noi_cap_phep_thanh_lap'] = ''
        return super(nha_dau_tu, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'is_company' in vals:
            if vals['is_company']==True:
                self.write(cr, uid, ids, {
                    'ngay_sinh': False,
                    'quoc_tich': False,
                    'gioitinh': False,     
                    'cmnd_ho_chieu': False,
                    'so_cmnd_hochieu': '',
                    'ngay_cap_cmnd_hc': False,
                    'noi_cap_cmnd_hc': '',
                }, context=context)
            if vals['is_company']==False:
                self.write(cr, uid, ids, {
                    'giay_thanh_lap_so': '',
                    'ngay_cap_phep_thanh_lap': False,
                    'noi_cap_phep_thanh_lap': '',
                }, context=context)
        return super(nha_dau_tu, self).write(cr, uid, ids, vals, context=context)
    
    def _get_default_country(self, cr, uid, context=None):
        country_ids = self.pool.get('res.country').search(cr, uid, [('code','=','VN')], context=context)
        return country_ids and country_ids[0] or False
    
    _defaults = {
        'country_id': _get_default_country,
        'quoc_tich': _get_default_country,
        'cmnd_ho_chieu': 'cmnd',
        'is_company': True,
    }
    
nha_dau_tu()

class giay_chung_nhan(osv.osv):
    _name = "giay.chung.nhan"
    _description = "Giay chung nhan"
    _columns = {
        'name': fields.char('Tên', size=64, required=True),
        'ma': fields.char('Mã', size=5),
    }
    def init(self, cr):
        wb = open_workbook(base_path + '/ql_ho_so/data/GiayChungNhan.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    val0 = s.cell(row,0).value
                    danhmuc_ids = self.search(cr, 1, [('name','=',val0)])
                    if not danhmuc_ids:
                        self.create(cr, 1, {'name': val0})
giay_chung_nhan()

class can_cu_luat(osv.osv):
    _name = "can.cu.luat"
    _description = "Can cu luat"
    _columns = {
        'name': fields.text('Tên', required=True),
    }
    
can_cu_luat()

class nghiavu_nhadautu(osv.osv):
    _name = "nghiavu.nhadautu"
    _description = "Nghia vu cua nha dau tu"
    _columns = {
        'name': fields.text('Nội dung', required=True),
    }
    
nghiavu_nhadautu()

class giay_chung_nhan_dau_tu(osv.osv):
    _name = "giay.chung.nhan.dau.tu"
    _description = "Giay Chung Nhan Dau Tu"
    
    def name_get(self, cr, user, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        result = self.browse(cr, user, ids, context=context)
        res = []
        for rs in result:
            name = "%s" % (rs.ma_so)
            res += [(rs.id, name)]
        return res
    
    _columns = {
        'write_date': fields.date('Ngày điều chỉnh', readonly=True),
        'write_uid': fields.many2one('res.users','Người thực hiện', readonly=True),
        'so_lan_thay_doi': fields.integer('Số lần thay đổi', readonly=True),
        'dia_chi': fields.char('Địa chỉ', size=1024),
        'loai_ho_so': fields.many2one('loai.ho.so','Loại hồ sơ', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'loai_hinh_doanh_nghiep': fields.many2one('res.partner.category','Loại hình doanh nghiệp', required=False, readonly=True, states={'draft': [('readonly', False)]}),
        'hinh_thuc_dau_tu_id': fields.many2one('hinh.thuc.dau.tu','Hình thức đầu tư', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'chung_nhan_lan_dau': fields.date('Chứng nhận lần đầu', required=True),
        'ma_so': fields.char('Mã số', required=False, readonly=True, states={'draft': [('readonly', False)]}),
        'dinh_dang_cu': fields.boolean('Định dạng cũ'),
        'can_cu_luat_ids': fields.many2many('can.cu.luat', 'hosodautu_canculuat_ref', 'hosodautu_id', 'canculuat_id','Căn cứ pháp lý'),
        'nha_dau_tu': fields.many2many('res.partner','nha_dau_tu_rel', 'ho_so_id', 'partner_id', 'Nhà đầu tư', domain="[('phan_he','=','hosodautu')]"),
        'ten_tieng_viet': fields.char('Tên bằng tiếng việt', size=128),
        'ten_tieng_anh': fields.char('Tên bằng tiếng anh', size=128),
        'ten_viet_tat': fields.char('Tên viết tắt', size=64),
#         'doanh_nghiep': fields.text('Doanh nghiệp'),
#         'dia_chi_tru_so': fields.text('Địa chỉ'),
#         'nganh_nghe': fields.text('Ngành nghề'),
        'nganh_nghe_ids': fields.many2many('nganh.nghe', 'nganh_nghe_ho_so_rel', 'ho_so_id', 'nganh_nghe_id','Ngành nghề'),
        'von_dieu_le_vn': fields.float('Vốn điều lệ',digits=(16,0)),
        'von_dieu_le_vn_chu': fields.char('Vốn điều lệ', size=1024),
        'von_dieu_le_us': fields.float('Vốn điều lệ',digits=(16,0)),
        'von_dieu_le_us_chu': fields.char('Vốn điều lệ', size=1024),
        
        'von_phapdinh_vn': fields.float('Vốn pháp định',digits=(16,0)),
        'von_phapdinh_vn_chu': fields.char('Vốn pháp định', size=1024),
        'von_phapdinh_us': fields.float('Vốn pháp định',digits=(16,0)),
        'von_phapdinh_us_chu': fields.char('Vốn pháp định', size=1024),
        
        'nguoi_dai_dien_id': fields.many2one('res.partner','Người đại diện', domain="[('is_company','=',False),('phan_he','=','hosodautu')]"),
        'ten_du_an': fields.char('Tên dự án', size=1024),
        'dia_chi_du_an': fields.char('Địa điểm hiện thực dự án', size=1024),
        'dien_tich_dat_su_dung': fields.float('Diện tích đất sử dụng'),
        'muc_tieu_du_an': fields.char('Mục tiêu', size=1024),
        'quy_mo_du_an': fields.char('Quy mô', size=1024),
        'von_dau_tu_vn': fields.float('Vốn đầu tư',digits=(16,0)),
        'von_dau_tu_vn_chu': fields.char('Vốn đầu tư', size=1024),
        'von_dau_tu_us': fields.float('Vốn đầu tư',digits=(16,0)),
        'von_dau_tu_us_chu': fields.char('Vốn đầu tư', size=1024),
        'von_thuc_hien_vn': fields.float('Vốn thực hiện',digits=(16,0)),
        'von_thuc_hien_vn_chu': fields.char('Vốn thực hiện', size=1024),
        'von_thuc_hien_us': fields.float('Vốn thực hiện',digits=(16,0)),
        'von_thuc_hien_us_chu': fields.char('Vốn thực hiện', size=1024),
        'tien_do': fields.char('Tiến độ góp vốn', size=1024),
        'thoi_han_hoat_dong': fields.char('Thời hạn hoạt động của dự án', size=1024),
        'thoi_han_thue_nha_xuong': fields.char('Thời hạn thuê nhà xưởng để thực hiện dự án', size=1024),
        'tien_do_thuc_hien': fields.text('Tiến độ thực hiện dự án'),
        'dieu7': fields.char('7.', size=1024),
        'nghiavu_nhadautu_ids': fields.many2many('nghiavu.nhadautu','hosodautu_nghiavunhadautu_ref','hosodautu_id','nghiavunhadautu_id','Nghĩa vụ nhà đầu tư'),
        'dieu3': fields.text('Điều 3'),
        'dieu4': fields.text('Điều 4'),
        'vanban_dautu_ids': fields.many2many('vanban.den', 'vanban_dautu_vanbanden_ref', 'vanban_dautu_id', 'vanbanden_id','Văn bản đầu tư'),
        'giay_chung_nhan_id': fields.many2one('giay.chung.nhan','Giấy chứng nhận', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'quoc_gia': fields.many2one('res.country','Quốc gia'),
        'tinh_tp_id': fields.many2one('res.country.state','Tỉnh/TP', domain="[('country_id','=',quoc_gia)]"),
        'quan_huyen_id': fields.many2one('quan.huyen','Quận/Huyện', domain="[('state_id','=',tinh_tp_id)]"),
        'khu_vuc_id': fields.many2one('khu.vuc','Khu vực', domain="[('tinh_tp_id','=',tinh_tp_id)]"),
        'nganh_nghe_khac': fields.many2one('nganh.nghe','Ngành nghề'),
        'lich_su': fields.one2many('giay.chung.nhan.dau.tu', 'parent_id', 'Lịch sử thay đổi',readonly=True),
        'thu_hoi_lines': fields.one2many('thu.hoi.ho.so', 'gcndt_id', 'Lịch sử thu hồi',readonly=True),
        'state': fields.selection([('draft','Mới Tạo'),('refuse','Đã Thu Hồi'),('cancel','Hủy'),('done','Đã cấp')], 'Tình trạng'),
        'parent_id': fields.many2one('giay.chung.nhan.dau.tu','Giấy chứng nhận đầu tư gốc',ondelete='cascade'),
        
        'check_loai_ho_so': fields.boolean('Check Loai Ho So'),
    }
    
    def onchange_loaihoso(self, cr, uid, ids, loai_ho_so=False, context=None):
        res = {}
        if loai_ho_so:
            loai_hoso = self.pool.get('loai.ho.so').browse(cr, uid, loai_ho_so).name
            if loai_hoso=='Không gắn với thành lập doanh nghiệp/chi nhánh':
                res['value'] = {'check_loai_ho_so': True}
            else:
                res['value'] = {'check_loai_ho_so': False}
        return res
    
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
    
    def _get_default_loai_hoso(self, cr, uid, context=None):
        loai_hoso_ids = self.pool.get('loai.ho.so').search(cr, uid, [], context=context)
        return loai_hoso_ids and loai_hoso_ids[0] or False
    
    def _get_default_loai_hinh_doanh_nghiep(self, cr, uid, context=None):
        loai_ids = self.pool.get('res.partner.category').search(cr, uid, [], context=context)
        return loai_ids and loai_ids[0] or False
    
    def _get_default_hinhthuc_dautu(self, cr, uid, context=None):
        htdt_ids = self.pool.get('hinh.thuc.dau.tu').search(cr, uid, [], context=context)
        return htdt_ids and htdt_ids[0] or False
    
    def _get_default_gcn(self, cr, uid, context=None):
        gcn_ids = self.pool.get('giay.chung.nhan').search(cr, uid, [], context=context)
        return gcn_ids and gcn_ids[0] or False
    
    def _get_default_nganhnghe(self, cr, uid, context=None):
        nganhnghe_ids = self.pool.get('nganh.nghe').search(cr, uid, [], context=context)
        return nganhnghe_ids and nganhnghe_ids[0] or False
    
    _defaults = {
      'tinh_tp_id': _get_tinh_tp,
      'so_lan_thay_doi': 0,
      'state': 'draft',
      'quoc_gia': _get_default_country,
      'loai_ho_so': _get_default_loai_hoso,
      'loai_hinh_doanh_nghiep': _get_default_loai_hinh_doanh_nghiep,
      'hinh_thuc_dau_tu_id': _get_default_hinhthuc_dautu,
      'chung_nhan_lan_dau': time.strftime('%Y-%m-%d'),
      'giay_chung_nhan_id': _get_default_gcn,
      'nganh_nghe_khac': _get_default_nganhnghe,
      'dieu3': '''Giấy chứng nhận đầu tư được lập thành 02 (hai) bản gốc; một bản cấp cho Doanh nghiệp, một bản lưu tại Ủy ban nhân dân tỉnh Bình Dương.
''',
#       'can_cu_luat': '''Căn cứ Luật tổ chức Hội đồng nhân dân và Ủy ban nhân dân ngày 26 tháng 11 năm 2003;
# 
# Căn cứ Luật Đầu tư số 59/2005/QH11 và Luật Doanh nghiệp số 60/2005/QH11 được Quốc hội thông qua tháng 11 năm 2005; 
# 
# Căn cứ Nghị định số 108/2006/NĐ-CP ngày 22 tháng 9 năm 2006 quy định chi tiết và hướng dẫn một số điều của Luật Đầu tư;
# 
# Căn cứ Nghị định số 88/2006/NĐ-CP ngày 21 tháng 8 năm 2006 về đăng ký kinh doanh;
# 
# Căn cứ ý kiến của Bộ Kế hoạch và Đầu tư (công văn số 8728/BKH-ĐTNN ngày 12/11/2009), Bộ Tài chính (công văn số số 15654/BTC-QLN ngày 05/11/2009), Bộ Công thương (công văn số 8788/BCT-KH ngày 04/9/2009);
# 
# Xét Bản đề nghị cấp Giấy chứng nhận đầu tư và hồ sơ của GUOCOLAND VIETNAM (S) PTE., LTD (Singapore) do ông PEH YEOW BENG LAWRENCE; quốc tịch Singapore làm đại diện nộp ngày 17 tháng 7 năm 2009 và Phụ lục sửa đổi, bổ sung nộp ngày 08 tháng 12 năm 2009, ngày 09 tháng 12 năm 2009;'''
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        for gcndt in self.browse(cr, uid, ids):
            if gcndt.parent_id:
                raise osv.except_osv(_('Cảnh báo!'),
                            _('Không thể chỉnh sửa hồ sơ cũ!'))
        return super(giay_chung_nhan_dau_tu, self).write(cr, uid, ids, vals, context=context)
    
    def dieu_chinh(self, cr, uid, ids, context=None):
        copy_id = None
        default = {}
        for gcndt in self.browse(cr, uid, ids):
            gcndt_id = gcndt.id
            gcndt_ids = self.search(cr, uid, [('parent_id','=',gcndt_id)])
            default.update({
                    'parent_id':gcndt_id,
                    'so_lan_thay_doi':gcndt.so_lan_thay_doi,
                    'state': gcndt.state,
                    'tinh_tp_id': gcndt.tinh_tp_id.id,
                    'quoc_gia': gcndt.quoc_gia.id,
                    'loai_ho_so': gcndt.loai_ho_so.id,
                    'loai_hinh_doanh_nghiep': gcndt.loai_hinh_doanh_nghiep.id,
                    'hinh_thuc_dau_tu_id': gcndt.hinh_thuc_dau_tu_id.id,
                    'chung_nhan_lan_dau': gcndt.chung_nhan_lan_dau,
                    'giay_chung_nhan_id': gcndt.giay_chung_nhan_id.id,
                    'nganh_nghe_khac': gcndt.nganh_nghe_khac.id,
                    'dieu3': gcndt.dieu3,
                })
            if gcndt_ids:
                gcndt_id = gcndt_ids[-1]
            copy_id = self.copy(cr, uid, gcndt_id, default, context=context)
            if copy_id:
                self.write(cr, uid, [gcndt.id],{'so_lan_thay_doi':gcndt.so_lan_thay_doi+1})
                return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'giay.chung.nhan.dau.tu',
                    'res_id': gcndt.id,
                    'context': context,
                }
        return False
    
    def xem_dieu_chinh(self, cr, uid, ids, context=None):
        gcndt_ids = self.search(cr, uid, [('parent_id','in',ids)])
        gcndt_ids+=ids
        domain = [('id','in',gcndt_ids)]
        return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'giay.chung.nhan.dau.tu',
                    'res_id': gcndt_ids,
                    'domain':domain,
                    'context': context,
                }
    
    def print_gcndt_khonggan(self, cr, uid, ids, context=None):
        return self.pool['report'].get_action(cr, uid, ids, 'giay_chung_nhan_dau_tu_khong_gan_report', context=context)
        
    def print_gcndt_gan(self, cr, uid, ids, context=None):
        return self.pool['report'].get_action(cr, uid, ids, 'giay_chung_nhan_dau_tu_report', context=context)
    
    def print_to_trinh(self, cr, uid, ids, context=None):
        return self.pool['report'].get_action(cr, uid, ids, 'to_trinh_chung_nhan_dau_tu_report', context=context)
    
    def thu_hoi(self, cr, uid, ids, context=None):
        obj_model = self.pool.get('ir.model.data')
        model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','thu_hoi_ho_so_view_form')])
        resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
        return {
            'name': 'Thu hồi hồ sơ',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'thu.hoi.ho.so',
            'views': [(resource_id,'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }
        
    def cap(self, cr, uid, ids, context=None):
        maso = ''
        property_pool = self.pool.get('admin.property')
        default_tinh_tp_gcndt = False
        property_obj = property_pool._get_project_property_by_name(cr, uid, 'default_maso_gcndt') or None
        for gcndt in self.browse(cr, uid, ids):
            if not gcndt.ma_so:
                if property_obj:
                    default_maso_gcndt = property_obj.value
                    for gcndt in self.browse(cr, uid, ids):
                        if gcndt.loai_ho_so.dodai_ma=='11':
                            sequence = self.pool.get('ir.sequence').get(cr, uid, 'giay.chung.nhan.dau.tu')
                            maso=default_maso_gcndt+gcndt.loai_ho_so.ma+gcndt.giay_chung_nhan_id.ma+sequence
                        if gcndt.loai_ho_so.dodai_ma=='12':
                            sequence = self.pool.get('ir.sequence').get(cr, uid, 'giay.chung.nhan.dau.tu')
                            maso=default_maso_gcndt+gcndt.loai_ho_so.ma+gcndt.loai_hinh_doanh_nghiep.ma+gcndt.hinh_thuc_dau_tu_id.ma+'0'+sequence
                else:
                    raise osv.except_osv(_('Cảnh báo!'),
                                    _('Chưa định nghĩa mã cấp tỉnh!'))
                self.write(cr, uid, ids, {'ma_so':maso})
        return self.write(cr, uid, ids, {'state':'done'})
        
giay_chung_nhan_dau_tu()

class gcndt_lich_su(osv.osv):
    _name = "gcndt.lich.su"
    _description = "Lich Su Thay Doi"
    _columns = {
        'gcndt_id': fields.many2one('giay.chung.nhan.dau.tu','Giấy chứng nhận đầu tư',ondelete='cascade'),
        'ma_so': fields.char('Mã số'),
        'ten_tieng_viet': fields.char('Tên bằng tiếng việt', size=128),
        'chung_nhan_lan_dau': fields.date('Chứng nhận lần đầu'),
        'so_lan_thay_doi': fields.integer('Số lần thay đổi'),
        'write_date': fields.date('Ngày điều chỉnh'),
        'write_uid': fields.many2one('res.users','Người thực hiện'),
        'state': fields.selection([('draft','Mới Tạo'),('refuse','Đã Thu Hồi'),('cancel','Hủy'),('done','Đã cấp')], 'Tình trạng'),
    }
gcndt_lich_su()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
