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
        'thungan_id': fields.many2one('thungan.bai.giaoca', 'Thu ngân bãi giao ca', required=True),
        'dieuhanh_id': fields.many2one('dieuhanh.bai.giaoca', 'Điều hành bãi giao ca', required=True),
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
        'so_tien': fields.float('Số tiền', required=True),
    }
no_hang_muc()

class ql_bao_hiem(osv.osv):
    _name = "ql.bao.hiem"
    
    def _get_sotien(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for line in self.browse(cr, uid, ids):
            result[line.id] = {'sotien_datra':0,'sotien_conlai':0}
            sql = '''
                select amount_total, residual from account_invoice
                    where state in ('open','paid') and partner_id=%s and so_hoa_don='%s' and bien_so_xe='%s' and mlg_type='phai_thu_bao_hiem'
                        and date_invoice between '%s' and '%s' order by date_invoice limit 1
            '''%(line.partner_id.id,line.so_hoa_don,line.name,line.ngay_tham_gia,line.ngay_ket_thuc)
            cr.execute(sql)
            invoice = cr.dictfetchone()
            if invoice:
                sotien = invoice['amount_total']
                sotien_conlai = invoice['residual']
                result[line.id] = {'sotien_datra':sotien-sotien_conlai,'sotien_conlai':sotien_conlai}
        return result
    
    _columns = {
        'name': fields.char('Biển số xe', size=1024, required=True),
        'hieu_xe': fields.char('Hiệu xe', size=1024),
        'dong_xe': fields.char('Dòng xe', size=1024),
        'cap_noi_that': fields.char('Cấp nội thất', size=1024),
        'partner_id': fields.many2one('res.partner','Nhà đầu tư', required=True),
        'loai_hinh_kd': fields.selection([('thuong_quyen','Thương quyền'),
                                      ('cong_ty','Công ty'),
                                      ],'Loại hình kinh doanh'),
        'ngay_tham_gia': fields.date('Ngày tham gia BH', required=True),
        'ngay_ket_thuc': fields.date('Ngày kết thúc BH', required=True),
        'so_hoa_don':fields.char('Số hóa đơn',size = 64, required=True),
        'nha_cung_cap_bh':fields.char('Nhà cung cấp BH',size = 1024),
        'chinhanh_id': fields.many2one('account.account','Chi nhánh', required=True),
        'sotien_datra': fields.function(_get_sotien, type='float', string='Số tiền đã trả', multi='sotien'),
        'sotien_conlai': fields.function(_get_sotien, type='float', string='Số tiền còn lại', multi='sotien'),
        'currency_id': fields.many2one('res.currency','Đơn vị tiền tệ'),
        'user_id': fields.many2one('res.users','Người tạo'),
    }
    
    def _get_currency(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.company_id and user.company_id.currency_id and user.company_id.currency_id.id or False
    
    def _get_chinhanh(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.chinhanh_id and user.chinhanh_id.id or False
    
    _defaults = {
        'currency_id': _get_currency,
        'chinhanh_id': _get_chinhanh,
        'user_id': lambda self,cr, uid, context: uid,
    }
    
#     def create(self, cr, uid, vals, context=None):
#         if context is None:
#             context = {}
#         user = self.pool.get('res.users').browse(cr, uid, uid)
#         vals.update({'chinhanh_id':user.chinhanh_id and user.chinhanh_id.id or False})
#         return super(ql_bao_hiem, self).create(cr, uid, vals, context)
#     
#     def write(self, cr, uid, ids, vals, context=None):
#         for line in self.browse(cr, uid, ids):
#             user = line.user_id
#             vals.update({'chinhanh_id':user.chinhanh_id and user.chinhanh_id.id or False})
#         return super(ql_bao_hiem, self).write(cr, uid, ids, vals, context)
    
ql_bao_hiem()

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    
    def _compute_residual(self):
        self.residual = 0.0
        # Each partial reconciliation is considered only once for each invoice it appears into,
        # and its residual amount is divided by this number of invoices
        partial_reconciliations_done = []
        for line in self.sudo().move_id.line_id:
            if line.account_id.type not in ('other'):
                continue
            if line.reconcile_partial_id and line.reconcile_partial_id.id in partial_reconciliations_done:
                continue
            # Get the correct line residual amount
            if line.currency_id == self.currency_id:
                line_amount = line.amount_residual_currency if line.currency_id else line.amount_residual
            else:
                from_currency = line.company_id.currency_id.with_context(date=line.date)
                line_amount = from_currency.compute(line.amount_residual, self.currency_id)
            # For partially reconciled lines, split the residual amount
            if line.reconcile_partial_id:
                partial_reconciliation_invoices = set()
                for pline in line.reconcile_partial_id.line_partial_ids:
                    if pline.invoice and self.type == pline.invoice.type:
                        partial_reconciliation_invoices.update([pline.invoice.id])
                line_amount = self.currency_id.round(line_amount / len(partial_reconciliation_invoices))
                partial_reconciliations_done.append(line.reconcile_partial_id.id)
            self.residual += line_amount
        self.residual = max(self.residual, 0.0)
        
    _columns = {
        'mlg_type': fields.selection([('no_doanh_thu','Nợ doanh thu'),
                                      ('chi_ho_dien_thoai','Chi hộ điện thoại'),
                                      ('phai_thu_bao_hiem','Phải thu bảo hiểm'),
                                      ('phai_thu_ky_quy','Phải thu ký quỹ'),
                                      ('phat_vi_pham','Phạt vi phạm'),
                                      ('thu_no_xuong','Thu nợ xưởng'),
                                      ('thu_phi_thuong_hieu','Thu phí thương hiệu'),
                                      ('tra_gop_xe','Trả góp xe'),
                                      ('hoan_tam_ung','Hoàn tạm ứng'),
                                      ('chi_no_doanh_thu','Chi nợ doanh thu'),
                                      ('chi_dien_thoai','Chi điện thoại'),
                                      ('chi_bao_hiem','Chi bảo hiểm'),
                                      ('phai_tra_ky_quy','Phải trả ký quỹ'),
                                      ('tam_ung','Tạm ứng'),
                                      ('chi_ho','Chi hộ'),],'Loại công nợ', readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft','Pending'),
            ('proforma','Pro-forma'),
            ('proforma2','Pro-forma'),
            ('open','Open'),
            ('paid','Paid'),
            ('cancel','Cancelled'),
        ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Pro-forma' when invoice is in Pro-forma status,invoice does not have an invoice number.\n"
             " * The 'Open' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice.\n"
             " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel invoice."),
        'doi_xe_id': fields.many2one('account.account', 'Đội xe'),
        'bai_giaoca_id': fields.related('partner_id', 'bai_giaoca_id', type='many2one', relation='bai.giaoca', string='Bãi giao ca', readonly=True, store=True),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, readonly=True, states={'draft':[('readonly',False)]},
                                      domain="[('type', 'in', ['cash','bank']), ('company_id', '=', company_id)]"),
#         'account_id': fields.related('partner_id', 'property_account_receivable', type='many2one', relation='account.account', string='Đội xe', readonly=True, store=True),
        'bien_so_xe_id': fields.many2one('bien.so.xe','Biển số xe'),
        'bien_so_xe': fields.char('Biển số xe', size=1024, readonly=True, states={'draft': [('readonly', False)]}),
        'ma_xuong_id': fields.many2one('ma.xuong','Mã xưởng', readonly=True, states={'draft': [('readonly', False)]}),
        'so_hop_dong': fields.char('Số hợp đồng', size=1024, readonly=True, states={'draft': [('readonly', False)]}),
        'loai_doituong_id': fields.related('partner_id', 'loai_doituong_id',type='many2one',relation='loai.doi.tuong',string='Loại đối tượng', readonly=True, store=True),
        'so_hoa_don':fields.char('Số hóa đơn',size = 64, readonly=True, states={'draft': [('readonly', False)]}),
        'loai_kyquy_id': fields.many2one('loai.ky.quy', 'Loại ký quỹ', readonly=True, states={'draft': [('readonly', False)]}),
        'loai_tamung_id': fields.many2one('loai.tam.ung', 'Loại tạm ứng', readonly=True, states={'draft': [('readonly', False)]}),
        'loai_vipham_id': fields.many2one('loai.vi.pham', 'Loại vi phạm', readonly=True, states={'draft': [('readonly', False)]}),
        'chinhanh_id': fields.many2one('account.account','Chi nhánh', readonly=True),
        'chinhanh_ndt_id': fields.many2one('account.account','Chi nhánh', readonly=True, states={'draft': [('readonly', False)]}),
        'so_bien_ban_vi_pham':fields.char('Số biên bản vi phạm',size = 64, readonly=True, states={'draft': [('readonly', False)]}),
        'ngay_vi_pham':fields.date('Ngày vi phạm', readonly=True, states={'draft': [('readonly', False)]}),
        'dien_giai': fields.text('Diễn giải', readonly=True, states={'draft': [('readonly', False)]}),
        'so_tien': fields.float('Số tiền', readonly=True, states={'draft': [('readonly', False)]}),
        'so_tien_tren_hd': fields.float('Số tiền trên hóa đơn', readonly=True, states={'draft': [('readonly', False)]}),
        'chung_tu_bao_hiem':fields.char('Chứng từ bảo hiểm',size = 1024, readonly=True, states={'draft': [('readonly', False)]}),
        'so_tien_tren_ct': fields.float('Số tiền trên chứng từ', readonly=True, states={'draft': [('readonly', False)]}),
        'ma_bang_chiettinh_chiphi_sua': fields.char('Mã bảng chiết tính chi phí sửa', size=1024, readonly=True, states={'draft': [('readonly', False)]}),
        'loai_doituong': fields.selection([('taixe','Lái xe'),
                                           ('nhadautu','Nhà đầu tư'),
                                           ('nhanvienvanphong','Nhân viên văn phòng')], 'Loại đối tượng', readonly=True, states={'draft': [('readonly', False)]}),
        'cmnd': fields.related('partner_id','cmnd',type='char',string='Số CMND',readonly=True),
        'giayphep_kinhdoanh': fields.related('partner_id','giayphep_kinhdoanh',type='char',string='Mã số giấy phép kinh doanh',readonly=True),
#         'residual': fields.function(_compute_residual,type='float',digits=dp.get_precision('Account'), store=True,
#                                     string='Balance',help="Remaining amount due."),
    }
    
    def _get_chinhanh(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
#         if not user.chinhanh_id:
#             raise osv.except_osv(_('Cảnh báo!'), _('''Vui lòng định nghĩa chi nhánh cho người dùng '%s' '''%(user.name)))
        return user.chinhanh_id and user.chinhanh_id.id or False
    
    def _get_journal(self, cr, uid, context=None):
        journal_ids = self.pool.get('account.journal').search(cr, uid, [('code','=','TG')])
        return journal_ids and journal_ids[0] or False
    
    def _get_currency(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.company_id and user.company_id.currency_id and user.company_id.currency_id.id or False
    
    _defaults = {
        'date_invoice': time.strftime('%Y-%m-%d'),
        'journal_id': _get_journal,
        'currency_id': _get_currency,
        'chinhanh_id': _get_chinhanh,
    }
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('mlg_type') and (vals.get('name', '/') == '/' or 'name' not in vals):
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, vals['mlg_type'], context=context) or '/'
#         if vals.get('loai_doituong',False)=='nhadautu':
#             sql = '''
#                 select nhom_chinhanh_id from chi_nhanh_line where chinhanh_id=%s and partner_id=%s
#             '''%(vals['chinhanh_ndt_id'],vals['partner_id'])
#             cr.execute(sql)
#             account_ids = [r[0] for r in cr.fetchall()]
#             account_id = account_ids and account_ids[0] or False
#             vals.update({'account_id':account_id})
#bat dau de tao du lieu readonly
#         if vals.get('loai_doituong',False) and vals['loai_doituong']!='nhadautu':
#             partner = self.pool.get('res.partner').browse(cr, uid, vals['partner_id'])
#             if context.get('default_type',False)=='out_invoice':
#                 account_id = partner.property_account_receivable and partner.property_account_receivable.id or False
#             else:
#                 account_id = partner.property_account_payable and partner.property_account_payable.id or False
#             vals.update({'account_id':account_id})
#         user = self.pool.get('res.users').browse(cr, uid, uid)
#         vals.update({'chinhanh_id':user.chinhanh_id and user.chinhanh_id.id or False})
        
        if vals.get('mlg_type',False) and vals.get('partner_id',False) and vals.get('loai_doituong',False):
            if not vals.get('so_tien', False):
                vals.update({'so_tien':0})
            sql = '''
                select case when sum(so_tien)!=0 then sum(so_tien) else 0 end sotien from no_hang_muc where name='%s' and mlg_type='%s'
            '''%(vals['loai_doituong'],vals['mlg_type'])
            cr.execute(sql)
            sotien_hangmuc = cr.fetchone()[0]
            sql = '''
                select case when sum(residual)!=0 then sum(residual) else 0 end residual from account_invoice
                    where partner_id=%s and mlg_type='%s' and state='open'
            '''%(vals['partner_id'],vals['mlg_type'])
            cr.execute(sql)
            sotien_conno = cr.fetchone()[0]
            if sotien_hangmuc and (sotien_conno+vals['so_tien'])>sotien_hangmuc:
                raise osv.except_osv(_('Cảnh báo!'), _('Không thể tạo khi đang nợ vượt hạng mức!'))
        if not vals.get('so_tien',False):
            raise osv.except_osv(_('Cảnh báo!'), _('Không thể tạo với số tiền bằng "0"!'))
        return super(account_invoice, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        for line in self.browse(cr, uid, ids):
#             user = line.user_id
#             vals.update({'chinhanh_id':user.chinhanh_id and user.chinhanh_id.id or False})
#             if ((vals.get('loai_doituong',False) and vals['loai_doituong']!='nhadautu') or ('loai_doituong' not in vals and line.loai_doituong and line.loai_doituong!='nhadautu')) and vals.get('partner_id',False):
#                 partner = self.pool.get('res.partner').browse(cr, uid, vals['partner_id'])
#                 if context.get('default_type',False)=='out_invoice':
#                     account_id = partner.property_account_receivable and partner.property_account_receivable.id or False
#                 else:
#                     account_id = partner.property_account_payable and partner.property_account_payable.id or False
#                 vals.update({'account_id':account_id})
#ket thuc
#             if vals.get('partner_id',False):
#                 partner = self.pool.get('res.partner').browse(cr, uid, vals['partner_id'])
#                 account_id = partner.property_account_receivable and partner.property_account_receivable.id or False
#                 vals.update({'account_id':account_id})
#             if vals.get('loai_doituong',False)=='nhadautu' or ('loai_doituong' not in vals and line.loai_doituong=='nhadautu'):
#                 if vals.get('chinhanh_ndt_id',False):
#                     chinhanh_ndt_id = vals['chinhanh_ndt_id']
#                 else:
#                     chinhanh_ndt_id = line.chinhanh_ndt_id.id
#                 if vals.get('partner_id',False):
#                     partner_id = vals['partner_id']
#                 else:
#                     partner_id = line.partner_id.id
#                 sql = '''
#                     select nhom_chinhanh_id from chi_nhanh_line where chinhanh_id=%s and partner_id=%s
#                 '''%(chinhanh_ndt_id,partner_id)
#                 cr.execute(sql)
#                 account_ids = [r[0] for r in cr.fetchall()]
#                 account_id = account_ids and account_ids[0] or False
#                 vals.update({'account_id':account_id})

                
            if vals.get('state',False)=='open' and line.type=='out_invoice':
                sql = '''
                    select case when sum(so_tien)!=0 then sum(so_tien) else 0 end sotien from no_hang_muc where name='%s' and mlg_type='%s'
                '''%(vals.get('loai_doituong',False) and vals['loai_doituong'] or line.loai_doituong,line.mlg_type)
                cr.execute(sql)
                sotien_hangmuc = cr.fetchone()[0]
                sql = '''
                    select case when sum(residual)!=0 then sum(residual) else 0 end residual from account_invoice
                        where partner_id=%s and mlg_type='%s' and state='open'
                '''%(vals.get('partner_id',False) and vals['partner_id'] or line.partner_id.id,line.mlg_type)
                cr.execute(sql)
                sotien_conno = cr.fetchone()[0]
                if sotien_hangmuc and sotien_conno>sotien_hangmuc:
                    raise osv.except_osv(_('Cảnh báo!'), _('Không thể duyệt khi đang nợ vượt hạng mức!'))
        return super(account_invoice, self).write(cr, uid, ids, vals, context)
    
    def in_phieu(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'account.invoice'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        name_report = context['name_report']
        invoice = self.browse(cr, uid, ids[0])
        name_report +='_'+invoice.loai_doituong
        return {'type': 'ir.actions.report.xml', 'report_name': name_report, 'datas': datas}
    
    def onchange_doituong(self, cr, uid, ids, partner_id=False,loai_doituong=False, context=None):
        vals = {}
        domain = {}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
            account_id = False
            sql = '''
                select chinhanh_id from chi_nhanh_line where partner_id=%s
            '''%(partner_id)
            cr.execute(sql)
            chinhanh_ids = [r[0] for r in cr.fetchall()]
            domain = {'chinhanh_ndt_id':[('id','in',chinhanh_ids)]}
            chinhanh_id = False
            if loai_doituong!='nhadautu':
                if context.get('default_type',False)=='out_invoice':
                    account_id = partner.property_account_receivable and partner.property_account_receivable.id or False
                    chinhanh_id = partner.property_account_receivable.parent_id.id
                else:
                    account_id = partner.property_account_payable and partner.property_account_payable.id or False
                    chinhanh_id = partner.property_account_payable.parent_id.id
            else:
                user = self.pool.get('res.users').browse(cr, uid, uid)
                if ids:
                    invoice = self.browse(cr, uid, ids[0])
                    user = invoice.user_id
                chinhanh_id = user.chinhanh_id and user.chinhanh_id.id or False
                sql = '''
                    select nhom_chinhanh_id from chi_nhanh_line where chinhanh_id=%s and partner_id=%s
                '''%(chinhanh_id,partner_id)
                cr.execute(sql)
                account_ids = [r[0] for r in cr.fetchall()]
                account_id = account_ids and account_ids[0] or False
                vals.update({'cmnd': partner.cmnd,'giayphep_kinhdoanh': partner.giayphep_kinhdoanh,'account_id':account_id})
            if partner.taixe:
                bai_giaoca_id=partner.bai_giaoca_id and partner.bai_giaoca_id.id or False
            else:
                bai_giaoca_id = False
            vals.update({'account_id':account_id,
                    'bai_giaoca_id': bai_giaoca_id,
                    })
        return {'value': vals,'domain': domain}
    
    def onchange_nhadautugiantiep(self, cr, uid, ids, partner_id=False, context=None):
        vals = {}
        domain = {}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
#             account_id = False
#             chinhanh_id = False
#             user = self.pool.get('res.users').browse(cr, uid, uid)
#             if ids:
#                 invoice = self.browse(cr, uid, ids[0])
#                 user = invoice.user_id
#             chinhanh_id = user.chinhanh_id and user.chinhanh_id.id or False
#             sql = '''
#                 select nhom_chinhanh_id from chi_nhanh_line where chinhanh_id=%s and partner_id=%s
#             '''%(chinhanh_id,partner_id)
#             cr.execute(sql)
#             account_ids = [r[0] for r in cr.fetchall()]
#             account_id = account_ids and account_ids[0] or False
            vals.update({'cmnd': partner.cmnd,'giayphep_kinhdoanh': partner.giayphep_kinhdoanh,'account_id':partner.property_account_receivable.id})
        return {'value': vals}
    
    def onchange_loaidoituong(self, cr, uid, ids, loai_doituong=False, context=None):
        domain = {}
        vals = {'partner_id':False,'account_id':False}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        if ids:
            invoice = self.browse(cr, uid, ids[0])
            user = invoice.user_id
        chinhanh_id = user.chinhanh_id and user.chinhanh_id.id or False
        if loai_doituong=='taixe':
            domain={'partner_id': [('taixe','=',True),('property_account_receivable.parent_id','=',chinhanh_id)]}
        if loai_doituong=='nhadautu':
            sql = '''
                select partner_id from chi_nhanh_line where chinhanh_id=%s
            '''%(chinhanh_id)
            cr.execute(sql)
            partner_ids = [r[0] for r in cr.fetchall()]
            domain={'partner_id': [('nhadautu','=',True),('id','in',partner_ids)]}
            vals.update({'chinhanh_ndt_id': chinhanh_id})
        if loai_doituong=='nhanvienvanphong':
            domain={'partner_id': [('nhanvienvanphong','=',True),('property_account_receivable.parent_id','=',chinhanh_id)]}
        return {'value': vals, 'domain': domain}
    
    def onchange_dien_giai_st(self, cr, uid, ids, dien_giai='/',so_tien=False,journal_id=False, context=None):
        domain = {}
        vals = {}
        if ids:
            cr.execute('delete from account_invoice_line where invoice_id in %s',(tuple(ids),))
        if not dien_giai:
            dien_giai = '/'
        if so_tien and journal_id:
            journal = self.pool.get('account.journal').browse(cr, uid, journal_id)
            vals = {'invoice_line': [(0,0,{'name': dien_giai,'price_unit': so_tien,'account_id':journal.default_credit_account_id.id})]}
        return {'value': vals}
    
    def onchange_chinhanh_ndt(self, cr, uid, ids, chinhanh_ndt_id=False, partner_id=False, context=None):
        domain = {}
        vals = {}
        if chinhanh_ndt_id and partner_id:
#             sql = '''
#                 select bsx_id from chinhanh_bien_so_xe_ref where chinhanh_id in (select id from chi_nhanh_line where chinhanh_id=%s and partner_id=%s)
#             '''%(chinhanh_ndt_id,partner_id)
#             cr.execute(sql)
#             bsx_ids = [r[0] for r in cr.fetchall()]
#             domain={'bien_so_xe_id': [('id','in',bsx_ids)]}
            sql = '''
                select nhom_chinhanh_id from chi_nhanh_line where chinhanh_id=%s and partner_id=%s
            '''%(chinhanh_ndt_id,partner_id)
            cr.execute(sql)
            account_ids = [r[0] for r in cr.fetchall()]
            account_id = account_ids and account_ids[0] or False
            vals = {'account_id':account_id}
        return {'value': vals, 'domain': domain}
    
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_invoice_tax = self.env['account.invoice.tax']
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise except_orm(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise except_orm(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            date_invoice = inv.date_invoice

            company_currency = inv.company_id.currency_id
            # create the analytical lines, one move line per invoice line
            iml = inv._get_analytic_lines()
            # check if taxes are all computed
            compute_taxes = account_invoice_tax.compute(inv.with_context(lang=inv.partner_id.lang))
            inv.check_tax_lines(compute_taxes)

            # I disabled the check_total feature
            if self.env['res.users'].has_group('account.group_supplier_inv_check_total'):
                if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding / 2.0):
                    raise except_orm(_('Bad Total!'), _('Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise except_orm(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

            # one move line per tax line
            iml += account_invoice_tax.move_line_get(inv.id)

            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
            else:
                ref = inv.number

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, ref, iml)

            name = inv.supplier_invoice_number or inv.name or '/'
            totlines = []
            if inv.payment_term:
                totlines = inv.with_context(ctx).payment_term.compute(total, date_invoice)[0]
            if totlines:
                res_amount_currency = total_currency
                ctx['date'] = date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'ref': ref,
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'ref': ref
                })

            date = date_invoice

            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)

            line = [(0, 0, self.line_get_convert(l, part.id, date)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            if journal.centralisation:
                raise except_orm(_('User Error!'),
                        _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = inv.finalize_invoice_move_lines(line)

            move_vals = {
                'ref': inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal.id,
                'date': inv.date_invoice,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
            }
            ctx['company_id'] = inv.company_id.id
            period = inv.period_id
            if not period:
                period = period.with_context(ctx).find(date_invoice)[:1]
            if period:
                move_vals['period_id'] = period.id
                for i in line:
                    i[2]['period_id'] = period.id

            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)

            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'period_id': period.id,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
            
            # Them bai giao ca cho account move line 
            if inv.bai_giaoca_id:
                acc_move_line = self.env['account.move.line']
                acc_move_lines = acc_move_line.search([('move_id','=',move.id)])
                acc_move_lines.with_context(ctx).write({'bai_giaoca_id': inv.bai_giaoca_id.id})
            
            # Them Loai cong no cho account move line 
            if inv.mlg_type:
                acc_move_line = self.env['account.move.line']
                acc_move_lines = acc_move_line.search([('move_id','=',move.id)])
                acc_move_lines.with_context(ctx).write({'mlg_type': inv.mlg_type})
                
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
        self._log_event()
        return True
    
    def invoice_pay_customer(self, cr, uid, ids, context=None):
        if not ids: return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_voucher', 'view_vendor_receipt_dialog_form')

        inv = self.browse(cr, uid, ids[0], context=context)
        return {
            'name':_("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'payment_expected_currency': inv.currency_id.id,
                'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                'default_amount': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
                'default_reference': inv.name,
#                 'default_journal_id': inv.journal_id.id,
                'default_bai_giaoca_id': inv.bai_giaoca_id and inv.bai_giaoca_id.id or False,
                'default_mlg_type': inv.mlg_type,
                'close_after_process': True,
                'invoice_type': inv.type,
                'invoice_id': inv.id,
                'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                'default_chinhanh_id': inv.chinhanh_id.id,
                'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
            }
        }
    
account_invoice()

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    
    _columns = {
        'ma_bang_chiettinh_chiphi_sua': fields.char('Mã bảng chiết tính chi phí sửa', size=1024),
    }
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(account_invoice_line, self).default_get(cr, uid, fields, context=context)
        if context.get('journal_id', False):
            journal = self.pool.get('account.journal').browse(cr, uid, context['journal_id'])
            res.update({'account_id': journal.default_credit_account_id.id})
        elif 'journal_id' in context and not context['journal_id']:
            raise osv.except_osv(_('Cảnh báo!'), _('Vui lòng chọn phương thức thanh toán trước!'))
        return res
    
account_invoice_line()

class account_move_line(osv.osv):
    _inherit = "account.move.line"
    
    def _get_thu_chi(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for line in self.browse(cr, uid, ids):
            if line.mlg_type in ['chi_no_doanh_thu','chi_dien_thoai','chi_bao_hiem','phai_tra_ky_quy','tam_ung']:
                result[line.id] = 'Chi'
            else:
                result[line.id] = 'Thu'
        return result
    
    def _get_con_lai(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for line in self.browse(cr, uid, ids):
            result[line.id] = line.debit - line.credit
        return result
    
    _columns = {
        'bai_giaoca_id': fields.many2one('bai.giaoca', 'Bãi giao ca'),
        'mlg_type': fields.selection([('no_doanh_thu','Nợ doanh thu'),
                                      ('chi_ho_dien_thoai','Chi hộ điện thoại'),
                                      ('phai_thu_bao_hiem','Phải thu bảo hiểm'),
                                      ('phai_thu_ky_quy','Phải thu ký quỹ'),
                                      ('phat_vi_pham','Phạt vi phạm'),
                                      ('thu_no_xuong','Thu nợ xưởng'),
                                      ('thu_phi_thuong_hieu','Thu phí thương hiệu'),
                                      ('tra_gop_xe','Trả góp xe'),
                                      ('hoan_tam_ung','Hoàn tạm ứng'),
                                      ('chi_no_doanh_thu','Chi nợ doanh thu'),
                                      ('chi_dien_thoai','Chi điện thoại'),
                                      ('chi_bao_hiem','Chi bảo hiểm'),
                                      ('phai_tra_ky_quy','Phải trả ký quỹ'),
                                      ('tam_ung','Tạm ứng'),
                                      ('chi_ho','Chi hộ'),],'Loại công nợ'),
        'thu_chi': fields.function(_get_thu_chi,type='char', string='Thu/Chi', store=True),
        'con_lai': fields.function(_get_con_lai,type='float', string='Còn lại', store=True),
    }
    
account_move_line()

class account_voucher(osv.osv):
    _inherit = "account.voucher"
    _columns = {
        'bai_giaoca_id': fields.many2one('bai.giaoca', 'Bãi giao ca'),
        'mlg_type': fields.selection([('no_doanh_thu','Nợ doanh thu'),
                                      ('chi_ho_dien_thoai','Chi hộ điện thoại'),
                                      ('phai_thu_bao_hiem','Phải thu bảo hiểm'),
                                      ('phai_thu_ky_quy','Phải thu ký quỹ'),
                                      ('phat_vi_pham','Phạt vi phạm'),
                                      ('thu_no_xuong','Thu nợ xưởng'),
                                      ('thu_phi_thuong_hieu','Thu phí thương hiệu'),
                                      ('tra_gop_xe','Trả góp xe'),
                                      ('hoan_tam_ung','Hoàn tạm ứng'),
                                      ('chi_no_doanh_thu','Chi nợ doanh thu'),
                                      ('chi_dien_thoai','Chi điện thoại'),
                                      ('chi_bao_hiem','Chi bảo hiểm'),
                                      ('phai_tra_ky_quy','Phải trả ký quỹ'),
                                      ('tam_ung','Tạm ứng'),
                                      ('chi_ho','Chi hộ'),],'Loại công nợ'),
        'chinhanh_id': fields.many2one('account.account','Chi nhánh'),
    }
    def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        """
        Returns a dict that contains new values and context

        @param partner_id: latest value from user input for field partner_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        def _remove_noise_in_o2m():
            """if the line is partially reconciled, then we must pay attention to display it only once and
                in the good o2m.
                This function returns True if the line is considered as noise and should not be displayed
            """
            if line.reconcile_partial_id:
                if currency_id == line.currency_id.id:
                    if line.amount_residual_currency <= 0:
                        return True
                else:
                    if line.amount_residual <= 0:
                        return True
            return False

        if context is None:
            context = {}
        context_multi_currency = context.copy()

        currency_pool = self.pool.get('res.currency')
        move_line_pool = self.pool.get('account.move.line')
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')
        line_pool = self.pool.get('account.voucher.line')

        #set default values
        default = {
            'value': {'line_dr_ids': [], 'line_cr_ids': [], 'pre_line': False},
        }

        # drop existing lines
        line_ids = ids and line_pool.search(cr, uid, [('voucher_id', '=', ids[0])])
        for line in line_pool.browse(cr, uid, line_ids, context=context):
            if line.type == 'cr':
                default['value']['line_cr_ids'].append((2, line.id))
            else:
                default['value']['line_dr_ids'].append((2, line.id))

        if not partner_id or not journal_id:
            return default

        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        partner = partner_pool.browse(cr, uid, partner_id, context=context)
        currency_id = currency_id or journal.company_id.currency_id.id

        total_credit = 0.0
        total_debit = 0.0
        account_type = None
        if context.get('account_id'):
            account_type = self.pool['account.account'].browse(cr, uid, context['account_id'], context=context).type
        if ttype == 'payment':
            if not account_type:
                account_type = 'other'
            total_debit = price or 0.0
        else:
            total_credit = price or 0.0
            if not account_type:
                account_type = 'other'

        if not context.get('move_line_ids', False):
            ids = move_line_pool.search(cr, uid, [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id)], context=context)
        else:
            ids = context['move_line_ids']
        invoice_id = context.get('invoice_id', False)
        company_currency = journal.company_id.currency_id.id
        move_lines_found = []

        #order the lines by most old first
        ids.reverse()
        account_move_lines = move_line_pool.browse(cr, uid, ids, context=context)

        #compute the total debit/credit and look for a matching open amount or invoice
        for line in account_move_lines:
            if _remove_noise_in_o2m():
                continue

            if invoice_id:
                if line.invoice.id == invoice_id:
                    #if the invoice linked to the voucher line is equal to the invoice_id in context
                    #then we assign the amount on that line, whatever the other voucher lines
                    move_lines_found.append(line.id)
            elif currency_id == company_currency:
                #otherwise treatments is the same but with other field names
                if line.amount_residual == price:
                    #if the amount residual is equal the amount voucher, we assign it to that voucher
                    #line, whatever the other voucher lines
                    move_lines_found.append(line.id)
                    break
                #otherwise we will split the voucher amount on each line (by most old first)
                total_credit += line.credit or 0.0
                total_debit += line.debit or 0.0
            elif currency_id == line.currency_id.id:
                if line.amount_residual_currency == price:
                    move_lines_found.append(line.id)
                    break
                total_credit += line.credit and line.amount_currency or 0.0
                total_debit += line.debit and line.amount_currency or 0.0

        remaining_amount = price
        #voucher line creation
        for line in account_move_lines:

            if _remove_noise_in_o2m():
                continue

            if line.currency_id and currency_id == line.currency_id.id:
                amount_original = abs(line.amount_currency)
                amount_unreconciled = abs(line.amount_residual_currency)
            else:
                #always use the amount booked in the company currency as the basis of the conversion into the voucher currency
                amount_original = currency_pool.compute(cr, uid, company_currency, currency_id, line.credit or line.debit or 0.0, context=context_multi_currency)
                amount_unreconciled = currency_pool.compute(cr, uid, company_currency, currency_id, abs(line.amount_residual), context=context_multi_currency)
            line_currency_id = line.currency_id and line.currency_id.id or company_currency
            rs = {
                'name':line.move_id.name,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id':line.id,
                'account_id':line.account_id.id,
                'amount_original': amount_original,
                'amount': (line.id in move_lines_found) and min(abs(remaining_amount), amount_unreconciled) or 0.0,
                'date_original':line.date,
                'date_due':line.date_maturity,
                'amount_unreconciled': amount_unreconciled,
                'currency_id': line_currency_id,
                #Them bai giao ca tren voucher line
                'bai_giaoca_id': line.bai_giaoca_id and line.bai_giaoca_id.id or False,
                # Them loại công no tren voucher line
                'mlg_type': line.mlg_type,
            }
            remaining_amount -= rs['amount']
            #in case a corresponding move_line hasn't been found, we now try to assign the voucher amount
            #on existing invoices: we split voucher amount by most old first, but only for lines in the same currency
            if not move_lines_found:
                if currency_id == line_currency_id:
                    if line.credit:
                        amount = min(amount_unreconciled, abs(total_debit))
                        rs['amount'] = amount
                        total_debit -= amount
                    else:
                        amount = min(amount_unreconciled, abs(total_credit))
                        rs['amount'] = amount
                        total_credit -= amount

            if rs['amount_unreconciled'] == rs['amount']:
                rs['reconcile'] = True

            if rs['type'] == 'cr':
                default['value']['line_cr_ids'].append(rs)
            else:
                default['value']['line_dr_ids'].append(rs)

            if len(default['value']['line_cr_ids']) > 0:
                default['value']['pre_line'] = 1
            elif len(default['value']['line_dr_ids']) > 0:
                default['value']['pre_line'] = 1
            default['value']['writeoff_amount'] = self._compute_writeoff_amount(cr, uid, default['value']['line_dr_ids'], default['value']['line_cr_ids'], price, ttype)
        return default
    
    def action_move_line_create(self, cr, uid, ids, context=None):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        if context is None:
            context = {}
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        for voucher in self.browse(cr, uid, ids, context=context):
            local_context = dict(context, force_company=voucher.journal_id.company_id.id)
            if voucher.move_id:
                continue
            company_currency = self._get_company_currency(cr, uid, voucher.id, context)
            current_currency = self._get_current_currency(cr, uid, voucher.id, context)
            # we select the context to use accordingly if it's a multicurrency case or not
            context = self._sel_context(cr, uid, voucher.id, context)
            # But for the operations made by _convert_amount, we always need to give the date in the context
            ctx = context.copy()
            ctx.update({'date': voucher.date})
            # Create the account move record.
            move_id = move_pool.create(cr, uid, self.account_move_get(cr, uid, voucher.id, context=context), context=context)
            # Get the name of the account_move just created
            name = move_pool.browse(cr, uid, move_id, context=context).name
            # Create the first line of the voucher
            move_line_id = move_line_pool.create(cr, uid, self.first_move_line_get(cr,uid,voucher.id, move_id, company_currency, current_currency, local_context), local_context)
            move_line_brw = move_line_pool.browse(cr, uid, move_line_id, context=context)
            line_total = move_line_brw.debit - move_line_brw.credit
            rec_list_ids = []
            if voucher.type == 'sale':
                line_total = line_total - self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            elif voucher.type == 'purchase':
                line_total = line_total + self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            # Create one move line per voucher line where amount is not 0.0
            line_total, rec_list_ids = self.voucher_move_line_create(cr, uid, voucher.id, line_total, move_id, company_currency, current_currency, context)

            # Create the writeoff line if needed
            ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, local_context)
            if ml_writeoff:
                move_line_pool.create(cr, uid, ml_writeoff, local_context)
            # We post the voucher.
            self.write(cr, uid, [voucher.id], {
                'move_id': move_id,
                'state': 'posted',
                'number': name,
            })
            
            # them bai_giaoca_id
            if voucher.bai_giaoca_id:
                cr.execute(''' update account_move_line set bai_giaoca_id=%s where move_id=%s ''',(voucher.bai_giaoca_id.id,move_id,))
                
            # them bai_giaoca_id
            if voucher.mlg_type:
                cr.execute(''' update account_move_line set mlg_type=%s where move_id=%s ''',(voucher.mlg_type,move_id,))
            
            if voucher.journal_id.entry_posted:
                move_pool.post(cr, uid, [move_id], context={})
            # We automatically reconcile the account move lines.
            reconcile = False
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    reconcile = move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
        return True
    
account_voucher()

class account_voucher_line(osv.osv):
    _inherit = "account.voucher.line"
    _columns = {
        'bai_giaoca_id': fields.many2one('bai.giaoca', 'Bãi giao ca'),
        'mlg_type': fields.selection([('no_doanh_thu','Nợ doanh thu'),
                                      ('chi_ho_dien_thoai','Chi hộ điện thoại'),
                                      ('phai_thu_bao_hiem','Phải thu bảo hiểm'),
                                      ('phai_thu_ky_quy','Phải thu ký quỹ'),
                                      ('phat_vi_pham','Phạt vi phạm'),
                                      ('thu_no_xuong','Thu nợ xưởng'),
                                      ('thu_phi_thuong_hieu','Thu phí thương hiệu'),
                                      ('tra_gop_xe','Trả góp xe'),
                                      ('hoan_tam_ung','Hoàn tạm ứng'),
                                      ('chi_no_doanh_thu','Chi nợ doanh thu'),
                                      ('chi_dien_thoai','Chi điện thoại'),
                                      ('chi_bao_hiem','Chi bảo hiểm'),
                                      ('phai_tra_ky_quy','Phải trả ký quỹ'),
                                      ('tam_ung','Tạm ứng'),
                                      ('chi_ho','Chi hộ'),],'Loại công nợ'),
    }
    
account_voucher_line()

class account_account(osv.osv):
    _inherit = "account.account"
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('cong_no_thu', False) and context.get('partner_id', False):
            sql = '''
                select chinhanh_id from chi_nhanh_line where partner_id=%s
            '''%(context['partner_id'])
            cr.execute(sql)
            chinhanh_ids = [r[0] for r in cr.fetchall()]
            args += [('id','in',chinhanh_ids)]
        
        if context.get('show_doixe',False):
            sql = '''
                select id from account_account where parent_id in (select id from account_account where parent_id in (select id from account_account where code='1'))
            '''
            cr.execute(sql)
            doixe_ids = [r[0] for r in cr.fetchall()]
            args += [('id','in',doixe_ids)]
        
        if context.get('cong_no_thu_nhadautu', False) and context.get('chinhanh_ndt_id', False) and context.get('partner_id', False):
            sql = '''
                select nhom_chinhanh_id from chi_nhanh_line where partner_id=%s and chinhanh_id=%s
            '''%(context['partner_id'],context['chinhanh_ndt_id'])
            cr.execute(sql)
            chinhanh_ids = [r[0] for r in cr.fetchall()]
            args += [('id','in',chinhanh_ids)]
        if context.get('search_chinhanh_in_chinhanhids'):
            chinhanh_ids = context['chinhanh_user']
            if chinhanh_ids and chinhanh_ids[0] and chinhanh_ids[0][2]:
                args += [('id','in',chinhanh_ids[0][2])]
            else:
                args += [('parent_id.code','=','1')]
        return super(account_account, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=None, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if context is None:
            context = {}
        if not name:
            ids = self.search(cr, user, args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [('code',operator,name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context=context)
    
account_account()

class thu_ky_quy(osv.osv):
    _name = "thu.ky.quy"
    _inherit = ['mail.thread']
    
    _columns = {
        'state': fields.selection([
            ('draft','Đang chờ'),
            ('paid','Đã thu'),
            ('cancel','Hủy bỏ'),
        ], string='Trạng thái', readonly=True),
        'chinhanh_id': fields.many2one('account.account','Chi nhánh', readonly=True),
        'partner_id': fields.many2one('res.partner','Đối tượng', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'ngay_thu': fields.date('Ngày thu', readonly=True, states={'draft': [('readonly', False)]}),
        'user_id': fields.many2one('res.users', 'Nhân viên thu', readonly=True, states={'draft': [('readonly', False)]}),
        'dien_giai': fields.text('Diễn giải', readonly=True, states={'draft': [('readonly', False)]}),
        'so_tien': fields.float('Số tiền', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'name': fields.char('Số'),
        'currency_id': fields.many2one('res.currency','Đơn vị tiền tệ'),
        'loai_doituong': fields.selection([('taixe','Lái xe'),
                                           ('nhadautu','Nhà đầu tư'),
                                           ('nhanvienvanphong','Nhân viên văn phòng')], 'Loại đối tượng'),
        'bien_so_xe': fields.char('Biển số xe', size=1024, readonly=True, states={'draft': [('readonly', False)]}),
        'loai_kyquy_id': fields.many2one('loai.ky.quy', 'Loại ký quỹ', readonly=True, states={'draft': [('readonly', False)]}),
    }
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('name', '/') == '/' or 'name' not in vals:
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'thu_ky_quy', context=context) or '/'
#         user = self.pool.get('res.users').browse(cr, uid, uid)
#         vals.update({'chinhanh_id':user.chinhanh_id and user.chinhanh_id.id or False})
        return super(thu_ky_quy, self).create(cr, uid, vals, context)
    
#     def write(self, cr, uid, ids, vals, context=None):
#         for line in self.browse(cr, uid, ids):
#             user = line.user_id
#             vals.update({'chinhanh_id':user.chinhanh_id and user.chinhanh_id.id or False})
#         return super(thu_ky_quy, self).write(cr, uid, ids, vals, context)
    
    def _get_chinhanh(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.chinhanh_id and user.chinhanh_id.id or False
    
    def _get_currency(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.company_id and user.company_id.currency_id and user.company_id.currency_id.id or False
    
    _defaults = {
        'state': 'draft',
        'ngay_thu': time.strftime('%Y-%m-%d'),
        'chinhanh_id': _get_chinhanh,
        'user_id': lambda self, cr, uid, context: uid,
        'currency_id': _get_currency,
    }
    
    def bt_thu(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'paid'})
    
    def bt_huybo(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'})
    
    def onchange_doituong(self, cr, uid, ids, partner_id=False, context=None):
        vals = {}
        domain = {}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if partner.taixe:
                vals={'loai_doituong': 'taixe'}
            if partner.nhadautu:
                vals={'loai_doituong': 'nhadautu'}
            if partner.nhanvienvanphong:
                vals={'loai_doituong': 'nhanvienvanphong'}
        return {'value': vals}
    
thu_ky_quy()

class account_journal(osv.osv):
    _inherit = "account.journal"
    
    _columns = {
        'chinhanh_id': fields.many2one('account.account','Chi nhánh'),
    }
    
account_journal()
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
