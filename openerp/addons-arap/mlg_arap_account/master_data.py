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

class thungan_bai_giaoca(osv.osv):
    _name = "thungan.bai.giaoca"
    _columns = {
        'name': fields.char('Tên', size=1024, required=True),
    }
thungan_bai_giaoca()

class dieuhanh_bai_giaoca(osv.osv):
    _name = "dieuhanh.bai.giaoca"
    _columns = {
        'name': fields.char('Tên', size=1024, required=True),
    }
dieuhanh_bai_giaoca()

class loai_doi_tuong(osv.osv):
    _name = "loai.doi.tuong"
    _columns = {
        'name': fields.char('Tên', size=1024, required=True),
    }
loai_doi_tuong()

class loai_ky_quy(osv.osv):
    _name = "loai.ky.quy"
    _columns = {
        'name': fields.char('Tên', size=1024, required=True),
        'description': fields.char('Mô tả', size=1024),
    }
loai_ky_quy()

class loai_vi_pham(osv.osv):
    _name = "loai.vi.pham"
    _columns = {
        'name': fields.char('Tên', size=1024, required=True),
        'description': fields.char('Mô tả', size=1024),
    }
loai_vi_pham()

class loai_tam_ung(osv.osv):
    _name = "loai.tam.ung"
    _columns = {
        'name': fields.char('Tên', size=1024, required=True),
    }
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
    
bai_giaoca()

class bien_so_xe(osv.osv):
    _name = "bien.so.xe"
    _columns = {
        'name': fields.char('Tên', size=1024, required=True),
    }
    
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
    
ma_xuong()

class no_hang_muc(osv.osv):
    _name = "no.hang.muc"
    _columns = {
        'name': fields.selection([('taixe','Lái xe'),
                                           ('nhadautu','Nhà đầu tư'),
                                           ('nhanvienvanphong','Nhân viên văn phòng')], 'Loại đối tượng', required=True),
        'mlg_type': fields.selection([('no_doanh_thu','Nợ doanh thu'),
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
                                      ('phai_thu_ky_quy','Phải thu ký quỹ (HISTAFF)'),
                                      ('phat_vi_pham','Phạt vi phạm (HISTAFF)'),
                                      ('thu_no_xuong','Thu nợ xưởng (BDSC)'),
                                      ('thu_phi_thuong_hieu_htkd','Thu phí thương hiệu (HTKD)'),
                                      ('thu_phi_thuong_hieu_shift','Thu phí thương hiệu (SHIFT)'),
                                      ('tra_gop_xe_htkd','Trả góp xe (HTKD)'),
                                      ('tra_gop_xe_shift','Trả góp xe (SHIFT)'),
                                      ('hoan_tam_ung','Phải thu tạm ứng (HISTAFF)'),
                                      ('fustion_phaithu','Phải thu Fustion (ORACLE)'),
                                      ('fustion_phaitra','Phải trả Fustion (ORACLE)'),
                                      ('chi_ho','Chi góp xe (HTKD)')
                                      ],'Loại công nợ', required=True),
    }
cauhinh_thumuc_import_tudong()

class cauhinh_thumuc_output_tudong(osv.osv):
    _name = "cauhinh.thumuc.output.tudong"
    _columns = {
        'name': fields.char('Đường dẫn', size=2048, required=True),
        'mlg_type': fields.selection([
                                      ('phai_thu_ky_quy','Phải thu ký quỹ (HISTAFF)'),
                                      ('phat_vi_pham','Phạt vi phạm (HISTAFF)'),
                                      ('thu_no_xuong','Thu nợ xưởng (BDSC)'),
                                      ('thu_phi_thuong_hieu_htkd','Thu phí thương hiệu (HTKD)'),
                                      ('thu_phi_thuong_hieu_shift','Thu phí thương hiệu (SHIFT)'),
                                      ('tra_gop_xe_htkd','Trả góp xe (HTKD)'),
                                      ('tra_gop_xe_shift','Trả góp xe (SHIFT)'),
                                      ('hoan_tam_ung','Phải thu tạm ứng (HISTAFF)'),
                                      ('oracle_phaithu','Doanh số thu (ORACLE)'),
                                      ('oracle_phaitra','Doanh số trả (ORACLE)'),
                                      ('chi_ho','Chi góp xe (HTKD)')
                                      ],'Loại công nợ', required=True),
    }
cauhinh_thumuc_output_tudong()

class ir_cron(osv.osv):
    _inherit = "ir.cron"
    
    _columns = {
        'mlg': fields.boolean('Mai Linh'),
    }
    
ir_cron()
    
class lichsu_giaodich(osv.osv):
    _name = "lichsu.giaodich"
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
loai_bao_hiem()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
