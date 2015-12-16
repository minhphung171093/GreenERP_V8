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

import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression
from openerp.tools.translate import _
import time
from openerp.exceptions import except_orm, Warning, RedirectWarning
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class thungan_bai_giaoca(osv.osv):
    _name = "thungan.bai.giaoca"
    _columns = {
        'name': fields.char('Tên', size=1024, required=True),
    }
    
    def _check_name(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            object_ids = self.search(cr, uid, [('id','!=', line.id),('name','!=', False),('name','=', line.name)])
            if object_ids:
                return False
        return True

    _constraints = [
        (_check_name, 'Không được trùng mã đối tượng', ['name']),
    ]
    
thungan_bai_giaoca()

class dieuhanh_bai_giaoca(osv.osv):
    _name = "dieuhanh.bai.giaoca"
    _columns = {
        'name': fields.char('Tên', size=1024, required=True),
    }
    
    def _check_name(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            object_ids = self.search(cr, uid, [('id','!=', line.id),('name','!=', False),('name','=', line.name)])
            if object_ids:
                return False
        return True

    _constraints = [
        (_check_name, 'Không được trùng tên', ['name']),
    ]
    
dieuhanh_bai_giaoca()

class loai_doi_tuong(osv.osv):
    _name = "loai.doi.tuong"
    _columns = {
        'name': fields.char('Tên', size=1024, required=True),
    }
loai_doi_tuong()

class loai_cong_no(osv.osv):
    _name = "loai.cong.no"
    _columns = {
        'name': fields.char('Tên', size=1024, required=True),
        'code': fields.char('Mã', size=1024),
    }

    def init(self, cr):
        cr.execute('''update ir_model_data set noupdate='f' where model='loai.cong.no' and module='mlg_arap_account'; ''')
    
loai_cong_no()

class loai_ky_quy(osv.osv):
    _name = "loai.ky.quy"
    _columns = {
        'name': fields.char('Tên', size=1024, required=True),
        'description': fields.char('Mô tả', size=1024),
    }
    
    def _check_name(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            object_ids = self.search(cr, uid, [('id','!=', line.id),('name','!=', False),('name','=', line.name)])
            if object_ids:
                return False
        return True

    _constraints = [
        (_check_name, 'Không được trùng tên', ['name']),
    ]
    
loai_ky_quy()

class loai_vi_pham(osv.osv):
    _name = "loai.vi.pham"
    _columns = {
        'name': fields.char('Tên', size=1024, required=True),
        'description': fields.char('Mô tả', size=1024),
    }
    
    def _check_name(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            object_ids = self.search(cr, uid, [('id','!=', line.id),('name','!=', False),('name','=', line.name)])
            if object_ids:
                return False
        return True

    _constraints = [
        (_check_name, 'Không được trùng tên', ['name']),
    ]
    
loai_vi_pham()

class loai_tam_ung(osv.osv):
    _name = "loai.tam.ung"
    _columns = {
        'name': fields.char('Tên', size=1024, required=True),
    }
    
    def _check_name(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            object_ids = self.search(cr, uid, [('id','!=', line.id),('name','!=', False),('name','=', line.name)])
            if object_ids:
                return False
        return True

    _constraints = [
        (_check_name, 'Không được trùng tên', ['name']),
    ]
    
loai_tam_ung()

class bai_giaoca(osv.osv):
    _name = "bai.giaoca"
    _columns = {
        'name': fields.char('Tên bãi giao ca', size=1024, required=True),
        'code': fields.char('Mã bãi giao ca', size=1024, required=True),
        'thungan_id': fields.many2one('thungan.bai.giaoca', 'Thu ngân bãi giao ca', required=False),
        'dieuhanh_id': fields.many2one('dieuhanh.bai.giaoca', 'Điều hành bãi giao ca', required=False),
        'account_id': fields.many2one('account.account', 'Đội xe', required=True),
    }
    
    def _check_code(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            object_ids = self.search(cr, uid, [('id','!=', line.id),('code','!=', False),('code','=', line.code)])
            if object_ids:
                return False
        return True

    _constraints = [
        (_check_code, 'Không được trùng mã', ['code']),
    ]
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        if not name:
            ids = self.search(cr, user, args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [('code',operator,name)] + args, limit=limit, context=context)
            
        return self.name_get(cr, user, ids, context=context)
    
bai_giaoca()

class bien_so_xe(osv.osv):
    _name = "bien.so.xe"
    _columns = {
        'name': fields.char('Tên', size=1024, required=True),
        'bai_giaoca_id': fields.many2one('bai.giaoca','Bãi giao ca'),
    }
    
    def _check_name(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            object_ids = self.search(cr, uid, [('id','!=', line.id),('name','!=', False),('name','=', line.name)])
            if object_ids:
                return False
        return True

    _constraints = [
        (_check_name, 'Không được trùng tên', ['name']),
    ]
    
#     def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
#         if context is None:
#             context = {}
#         if context.get('cong_no_thu', False) and context.get('partner_id', False) and context.get('chinhanh_ndt_id', False):
#             sql = '''
#                 select bsx_id from chinhanh_bien_so_xe_ref where chinhanh_id in (select id from chi_nhanh_line where chinhanh_id=%s and partner_id=%s)
#             '''%(context['chinhanh_ndt_id'],context['partner_id'])
#             cr.execute(sql)
#             bsx_ids = [r[0] for r in cr.fetchall()]
#             args += [('id','in',bsx_ids)]
#         return super(bien_so_xe, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
#     
#     def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
#         if context is None:
#             context = {}
#         ids = self.search(cr, user, args, context=context, limit=limit)
#         return self.name_get(cr, user, ids, context=context)
    
bien_so_xe()

class ma_xuong(osv.osv):
    _name = "ma.xuong"
    _columns = {
        'name': fields.char('Tên', size=1024, required=True),
        'code': fields.char('Mã', size=1024, required=True),
    }
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = '['+(record.code or '')+']'+' '+(record.name or '')
            res.append((record.id, name))
        return res
    
    def _check_code(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            object_ids = self.search(cr, uid, [('id','!=', line.id),('code','!=', False),('code','=', line.code)])
            if object_ids:
                return False
        return True

    _constraints = [
        (_check_code, 'Không được trùng mã', ['code']),
    ]
    
ma_xuong()

class no_hang_muc(osv.osv):
    _name = "no.hang.muc"
    _columns = {
        'name': fields.selection([('taixe','Lái xe'),
                                           ('nhadautu','Nhà đầu tư'),
                                           ('nhanvienvanphong','Nhân viên văn phòng')], 'Loại đối tượng', required=True),
        'mlg_type': fields.selection([('no_doanh_thu','Nợ DT-BH-AL'),
                                      ('chi_ho_dien_thoai','Chi hộ điện thoại'),
                                      ('phai_thu_bao_hiem','Phải thu bảo hiểm'),
                                      ('phai_thu_ky_quy','Phải thu ký quỹ'),
                                      ('phat_vi_pham','Phạt vi phạm'),
                                      ('thu_no_xuong','Thu nợ xưởng'),
                                      ('thu_phi_thuong_hieu','Thu phí thương hiệu'),
                                      ('tra_gop_xe','Trả góp xe'),
                                      ('hoan_tam_ung','Hoàn tạm ứng'),
                                      ],'Loại công nợ', required=True),
        'so_tien': fields.float('Số tiền',digits=(16,0), required=True),
    }
no_hang_muc()

class cauhinh_thumuc_import(osv.osv):
    _name = "cauhinh.thumuc.import"
    _columns = {
        'name': fields.char('Đường dẫn', size=2048, required=True),
        'mlg_type': fields.selection([
                                      ('chi_ho_dien_thoai','Phải thu chi hộ điện thoại'),
                                      ('phai_thu_bao_hiem','Phải thu bảo hiểm'),
                                      ('thu_no_xuong','Thu nợ xưởng'),
                                      ],'Loại công nợ', required=True),
    }
cauhinh_thumuc_import()

class cauhinh_thumuc_import_tudong(osv.osv):
    _name = "cauhinh.thumuc.import.tudong"
    _columns = {
        'name': fields.char('Đường dẫn', size=2048, required=True),
        'mlg_type': fields.selection([
                                      ('thu_no_xuong','Thu nợ xưởng (BDSC)'),
                                      ('no_doanh_thu_histaff','Nợ DT-BH-AL (HISTAFF)'),
                                      ('phat_vi_pham','Phạt vi phạm (HISTAFF)'),
                                      ('hoan_tam_ung','Phải thu tạm ứng (HISTAFF)'),
                                      ('phai_thu_ky_quy','Phải thu ký quỹ (HISTAFF)'),
                                      ('thu_phi_thuong_hieu_htkd','Thu phí thương hiệu (HTKD)'),
                                      ('tra_gop_xe_htkd','Trả góp xe (HTKD)'),
                                      ('chi_ho','Chi góp xe (HTKD)'),
                                      ('fustion_phaithu','Phải thu Fustion (ORACLE)'),
                                      ('fustion_phaitra','Phải trả Fustion (ORACLE)'),
                                      ('no_doanh_thu_shift','Nợ DT-BH-AL (SHIFT)'),
                                      ('chi_ho_dien_thoai_shift','Phải thu chi hộ điện thoại (SHIFT)'),
                                      ('phai_thu_bao_hiem_shift','Phải thu bảo hiểm (SHIFT)'),
                                      ('phat_vi_pham_shift','Phạt vi phạm (SHIFT)'),
                                      ('thu_no_xuong_shift','Thu nợ xưởng (SHIFT)'),
                                      ('thu_phi_thuong_hieu_shift','Thu phí thương hiệu (SHIFT)'),
                                      ('hoan_tam_ung_shift','Phải thu tạm ứng (SHIFT)'),
                                      ('phai_thu_ky_quy_shift','Phải thu ký quỹ (SHIFT)'),
                                      ('tra_gop_xe_shift','Trả góp xe (SHIFT)'),
                                      ],'Loại công nợ', required=True),
    }
cauhinh_thumuc_import_tudong()

class cauhinh_thumuc_output_tudong(osv.osv):
    _name = "cauhinh.thumuc.output.tudong"
    _columns = {
        'name': fields.char('Đường dẫn', size=2048, required=True),
        'mlg_type': fields.selection([
                                      ('thu_no_xuong','Thu nợ xưởng (BDSC)'),
                                      ('no_doanh_thu_histaff','Nợ DT-BH-AL (HISTAFF)'),
                                      ('phat_vi_pham','Phạt vi phạm (HISTAFF)'),
                                      ('hoan_tam_ung','Phải thu tạm ứng (HISTAFF)'),
                                      ('phai_thu_ky_quy','Phải thu ký quỹ (HISTAFF)'),
                                      ('thu_phi_thuong_hieu_htkd','Thu phí thương hiệu (HTKD)'),
                                      ('tra_gop_xe_htkd','Trả góp xe (HTKD)'),
                                      ('chi_ho','Chi góp xe (HTKD)'),
                                      ('oracle_phaithu','Doanh số thu (ORACLE)'),
                                      ('oracle_phaitra','Doanh số trả (ORACLE)'),
                                      ('no_doanh_thu_shift','Nợ DT-BH-AL (SHIFT)'),
                                      ('chi_ho_dien_thoai_shift','Phải thu chi hộ điện thoại (SHIFT)'),
                                      ('phai_thu_bao_hiem_shift','Phải thu bảo hiểm (SHIFT)'),
                                      ('phat_vi_pham_shift','Phạt vi phạm (SHIFT)'),
                                      ('thu_no_xuong_shift','Thu nợ xưởng (SHIFT)'),
                                      ('thu_phi_thuong_hieu_shift','Thu phí thương hiệu (SHIFT)'),
                                      ('hoan_tam_ung_shift','Phải thu tạm ứng (SHIFT)'),
                                      ('phai_thu_ky_quy_shift','Phải thu ký quỹ (SHIFT)'),
                                      ('tra_gop_xe_shift','Trả góp xe (SHIFT)'),
                                      ],'Loại công nợ', required=True),
    }
cauhinh_thumuc_output_tudong()

class ir_cron(osv.osv):
    _inherit = "ir.cron"
    
    _columns = {
        'mlg': fields.boolean('Mai Linh'),
    }
    
    def run_manually(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self._callback(cr, line.user_id.id, line.model, line.function, line.args, line.id)
            
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                                'mlg_arap_account', 'alert_warning_form_view')
        return {
                    'name': 'Thông báo',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': res[1],
                    'res_model': 'alert.warning.form',
                    'domain': [],
                    'context': {'default_name':'Thành công'},
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }
    
ir_cron()
    
class ir_sequence(osv.osv):
    _inherit = "ir.sequence"
    
    _columns = {
        'mlg': fields.boolean('Mai Linh'),
    }
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        if not name:
            ids = self.search(cr, user, args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [('code',operator,name)] + args, limit=limit, context=context)
            
        return self.name_get(cr, user, ids, context=context)
    
ir_sequence()
    
class lichsu_giaodich(osv.osv):
    _name = "lichsu.giaodich"
    _order = 'name desc'
    _columns = {
        'name': fields.datetime('Ngày'),
        'ten_file': fields.text('Tên file'),
        'loai_giaodich': fields.text('Loại giao dịch'),
        'thu_tra': fields.text('Thu/Trả'),
        'nhap_xuat': fields.text('Nhập/Xuất'),
        'tudong_bangtay': fields.text('Tự động/Bằng tay'),
        'trang_thai': fields.text('Trạng thái'),
        'noidung_loi': fields.text('Ghi chú'),
    }
lichsu_giaodich()

class loai_bao_hiem(osv.osv):
    _name = "loai.bao.hiem"
    _columns = {
        'name': fields.char('Tên', size=1024, required=True),
        'so_taikhoan': fields.char('Số tài khoản', size=1024, required=True),
    }
    
    def _check_name(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            object_ids = self.search(cr, uid, [('id','!=', line.id),('name','!=', False),('name','=', line.name)])
            if object_ids:
                return False
        return True

    _constraints = [
        (_check_name, 'Không được trùng mã', ['name']),
    ]
    
loai_bao_hiem()
class loai_no_doanh_thu(osv.osv):
    _name = "loai.no.doanh.thu"
    _columns = {
        'name': fields.char('Tên', size=1024, required=True),
        'so_taikhoan': fields.char('Số tài khoản', size=1024, required=True),
    }
    
    def _check_name(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            object_ids = self.search(cr, uid, [('id','!=', line.id),('name','!=', False),('name','=', line.name)])
            if object_ids:
                return False
        return True

    _constraints = [
        (_check_name, 'Không được trùng tên', ['name']),
    ]
    
loai_no_doanh_thu()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
