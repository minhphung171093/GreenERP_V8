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
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import netsvc, api
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(account_invoice, self).default_get(cr, uid, fields, context=context)
        if context.get('default_mlg_type', False) and context['default_mlg_type']=='no_doanh_thu':
            date = datetime.now() + timedelta(days=-1)
            sql = '''
                select id from loai_no_doanh_thu where upper(code)='NO_DOANH_THU'
            '''
            cr.execute(sql)
            loai_ndt_ids = [r[0] for r in cr.fetchall()]
            res.update({'date_invoice': date.strftime('%Y-%m-%d'),
                        'loai_nodoanhthu_id': loai_ndt_ids and loai_ndt_ids[0] or False,
                        })
        return res
    
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
    
    def _get_loai_doituong(self, cr, uid, context=None):
        if context is None:
            context = {}
            
        vals = [('taixe','Lái xe'),
                ('nhadautu','Nhà đầu tư'),
                ('nhanvienvanphong','Nhân viên văn phòng')]
            
        if context.get('default_mlg_type', False) and context['default_mlg_type']=='no_doanh_thu':
            vals = [('taixe','Lái xe'),
                    ('nhanvienvanphong','Nhân viên văn phòng')
                ]
            
        if context.get('default_mlg_type', False) and context['default_mlg_type']=='chi_ho_dien_thoai':
            vals = [('taixe','Lái xe'),
                ('nhanvienvanphong','Nhân viên văn phòng'),
                ]
        
        if context.get('default_mlg_type', False) and context['default_mlg_type']=='phai_thu_bao_hiem':
            vals = [('nhadautu','Nhà đầu tư')]
        
        if context.get('default_mlg_type', False) and context['default_mlg_type']=='phat_vi_pham':
            vals = [('taixe','Lái xe'),
                ('nhanvienvanphong','Nhân viên văn phòng'),
                ]
            
        if context.get('default_mlg_type', False) and context['default_mlg_type']=='thu_phi_thuong_hieu':
            vals = [('taixe','Lái xe'),
                ('nhadautu','Nhà đầu tư'),
                ]
        
        if context.get('default_mlg_type', False) and context['default_mlg_type']=='tra_gop_xe':
            vals = [
                ('nhadautu','Nhà đầu tư'),
                ]
        
        return vals
    
    def _get_invisible_button_cancel(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = False
            if invoice.state not in ['draft', 'open']:
                res[invoice.id] = True
        return res
    
    def _get_sotien_lai_conlai(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = 0
            sql = '''
                select case when sum(so_tien)!=0 then sum(so_tien) else 0 end tong from so_tien_lai where invoice_id=%s
            '''%(invoice.id)
            cr.execute(sql)
            tong = cr.fetchone()[0]
            res[invoice.id] = invoice.sotien_lai - tong
        return res
    
    def _get_invoice(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('so.tien.lai').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()
    
    _columns = {
        'mlg_type': fields.selection([('no_doanh_thu','Nợ DT-BH-AL'),
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
        'bien_so_xe': fields.char('BSX', size=1024, readonly=True, states={'draft': [('readonly', False)]}),
        'ma_xuong_id': fields.many2one('ma.xuong','Mã xưởng', readonly=True, states={'draft': [('readonly', False)]}),
        'so_hop_dong': fields.char('Số hợp đồng', size=1024, readonly=True, states={'draft': [('readonly', False)]}),
        'so_dien_thoai': fields.char('Số điện thoại', size=1024, readonly=True, states={'draft': [('readonly', False)]}),
        'loai_doituong_id': fields.related('partner_id', 'loai_doituong_id',type='many2one',relation='loai.doi.tuong',string='Loại đối tượng', readonly=True, store=True),
        'so_hoa_don':fields.char('Số hóa đơn',size = 64, readonly=True, states={'draft': [('readonly', False)]}),
        'loai_kyquy_id': fields.many2one('loai.ky.quy', 'Loại ký quỹ', readonly=True, states={'draft': [('readonly', False)]}),
        'loai_tamung_id': fields.many2one('loai.tam.ung', 'Loại tạm ứng', readonly=True, states={'draft': [('readonly', False)]}),
        'loai_nodoanhthu_id': fields.many2one('loai.no.doanh.thu', 'Loại nợ DT-BH-AL', readonly=True, states={'draft': [('readonly', False)]}),
        'loai_vipham_id': fields.many2one('loai.vi.pham', 'Loại vi phạm', readonly=True, states={'draft': [('readonly', False)]}),
        'loai_baohiem_id': fields.many2one('loai.bao.hiem', 'Loại bảo hiểm', readonly=True, states={'draft': [('readonly', False)]}),
        'chinhanh_id': fields.many2one('account.account','Chi nhánh', readonly=False),
        'chinhanh_ndt_id': fields.many2one('account.account','Chi nhánh NDT', readonly=True, states={'draft': [('readonly', False)]}),
        'so_bien_ban_vi_pham':fields.char('Số biên bản vi phạm',size = 64, readonly=True, states={'draft': [('readonly', False)]}),
        'ngay_vi_pham':fields.date('Ngày vi phạm', readonly=True, states={'draft': [('readonly', False)]}),
        'dien_giai': fields.text('Diễn giải', readonly=True, states={'draft': [('readonly', False)]}),
        'so_tien': fields.float('Số tiền',digits=(16,0), readonly=True, states={'draft': [('readonly', False)]}),
        'so_tien_tren_hd': fields.float('Số tiền trên hóa đơn',digits=(16,0), readonly=True, states={'draft': [('readonly', False)]}),
        'chung_tu_bao_hiem':fields.char('Chứng từ bảo hiểm',size = 1024, readonly=True, states={'draft': [('readonly', False)]}),
        'so_tien_tren_ct': fields.float('Số tiền trên chứng từ',digits=(16,0), readonly=True, states={'draft': [('readonly', False)]}),
        'ma_bang_chiettinh_chiphi_sua': fields.char('Mã chiết tính', size=1024, readonly=True, states={'draft': [('readonly', False)]}),
#         'loai_doituong': fields.selection([('taixe','Lái xe'),
#                                            ('nhadautu','Nhà đầu tư'),
#                                            ('nhanvienvanphong','Nhân viên văn phòng')], 'Loại đối tượng', readonly=True, states={'draft': [('readonly', False)]}),
        'loai_doituong': fields.selection(_get_loai_doituong, 'Loại đối tượng', readonly=True, states={'draft': [('readonly', False)]}),
        'cmnd': fields.related('partner_id','cmnd',type='char',string='Số CMND',readonly=True),
        'giayphep_kinhdoanh': fields.related('partner_id','giayphep_kinhdoanh',type='char',string='Mã số giấy phép kinh doanh',readonly=True),
        'thu_cho_doituong_id': fields.many2one('res.partner','Thu cho đối tượng'),
#         'residual': fields.function(_compute_residual,type='float',digits=dp.get_precision('Account'), store=True,
#                                     string='Balance',help="Remaining amount due."),
        'fusion_id': fields.char('Fusion Chi', size=1024),
        'invisible_button_cancel': fields.function(_get_invisible_button_cancel, type='boolean', string='Invisible Button Cancel'),
        'ref_number': fields.char('Ref NUMBER', size=1024),
        'loai_giaodich': fields.char('Loại giao dịch', size=1024),
        'lichsu_thutienlai_line': fields.one2many('so.tien.lai', 'invoice_id', 'Lịch sử thu tiền lãi'),
        'sotien_lai': fields.float('Số tiền lãi',digits=(16,0), readonly=True, states={'draft': [('readonly', False)]}),
        'sotien_lai_conlai': fields.function(_get_sotien_lai_conlai,string='Số tiền lãi còn lại',digits=(16,0),
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['sotien_lai','lichsu_thutienlai_line'], 10),
                'so.tien.lai': (_get_invoice, ['invoice_id', 'so_tien', 'ngay','fusion_id'], 10),
            },type='float'),
        'cantru_kyquy_chocongno_ids': fields.many2many('thu.ky.quy', 'cantru_kyquy_chocongno_ref', 'congno_id', 'thukyquy_id', 'Cấn trừ ký quỹ cho công nợ'),
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
        'date_invoice':  lambda *a: time.strftime('%Y-%m-%d'),
        'journal_id': _get_journal,
        'currency_id': _get_currency,
        'chinhanh_id': _get_chinhanh,
        'sotien_lai': 0,
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
        if not vals.get('so_tien',False) or (vals.get('so_tien') and vals['so_tien']<=0):
            raise osv.except_osv(_('Cảnh báo!'), _('Không thể tạo với số tiền nhỏ hơn hoặc bằng "0"!'))
        
        if vals.get('mlg_type', False) and vals['mlg_type'] =='tra_gop_xe' and vals.get('chinhanh_id',False):
#             wf_service = netsvc.LocalService("workflow")
            if vals.get('thu_cho_doituong_id',False):
                sql = '''
                    select id from res_partner where id=%s and nhadautugiantiep=True and ma_doi_tuong in (select code from account_account where id=%s)
                '''%(vals['thu_cho_doituong_id'],vals['chinhanh_id'])
                cr.execute(sql)
                partner_ids = [r[0] for r in cr.fetchall()]
                if not partner_ids:
                    ptch_vals = {}
                    partner_obj = self.pool.get('res.partner')
                    partner = partner_obj.browse(cr, uid, vals['thu_cho_doituong_id'])
                    partner_tgx = partner_obj.browse(cr, uid, vals['partner_id'])
                    ptch_vals.update(self.onchange_nhadautugiantiep(cr, uid, [], partner.id, context)['value'])
                    ptch_vals.update({
                        'mlg_type': 'chi_ho',
                        'type': 'in_invoice',
                        'chinhanh_id': vals['chinhanh_id'],
                        'partner_id': partner.id,
                        'date_invoice': vals['date_invoice'],
                        'so_tien': vals.get('so_tien', 0),
                        'dien_giai': 'Tạo từ trả góp xe %s cho đối tượng [%s] %s'%(vals['name'],partner_tgx.ma_doi_tuong,partner_tgx.name),
                        'journal_id': vals['journal_id'],
                        'so_hop_dong': vals.get('so_hop_dong', False),
                        'bai_giaoca_id': vals.get('bai_giaoca_id', False),
                        'bien_so_xe_id': vals.get('bien_so_xe_id', False),
                        'loai_giaodich': 'Giao dịch tạo tự động từ trả góp xe',
                    })
                    invoice_vals = self.onchange_dien_giai_st(cr, uid, [], ptch_vals['dien_giai'], ptch_vals['so_tien'], ptch_vals['journal_id'], context)['value']
                    ptch_vals.update(invoice_vals)
                    invoice_id = self.create(cr, uid, ptch_vals)
#             wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
            if 'thu_cho_doituong_id' not in vals or not vals.get('thu_cho_doituong_id', False):
                sql = '''
                    select id from res_partner where nhadautugiantiep=True and ma_doi_tuong in (select code from account_account where id=%s)
                '''%(vals['chinhanh_id'])
                cr.execute(sql)
                partner_ids = [r[0] for r in cr.fetchall()]
                vals.update({'thu_cho_doituong_id':partner_ids and partner_ids[0] or False})
            
        if vals.get('mlg_type', False) and vals['mlg_type'] =='phai_tra_ky_quy':
            if vals['loai_doituong'] in ['taixe','nhanvienvanphong']:
                sql = '''
                    select case when sotien_dathu!=0 then sotien_dathu else 0 end sotien_dathu from res_partner where id=%s
                '''%(vals['partner_id'])
                cr.execute(sql)
                sotien_dathu = cr.fetchone()[0]
                if sotien_dathu<vals['so_tien']:
                    raise osv.except_osv(_('Cảnh báo!'), _('Không được phép tạo với số tiền nhập vào lớn hơn số tiền ký quỹ đã thu!'))
            if vals['loai_doituong'] == 'nhadautu':
                sql = '''
                
                    select case when sotien_dathu!=0 then sotien_dathu else 0 end sotien_dathu
                        from chi_nhanh_line where chinhanh_id=%s and partner_id=%s
                '''%(vals['chinhanh_id'],vals['partner_id'])
                cr.execute(sql)
                sotien_dathu = cr.fetchone()[0]
                if sotien_dathu<vals['so_tien']:
                    raise osv.except_osv(_('Cảnh báo!'), _('Không được phép tạo với số tiền nhập vào lớn hơn số tiền ký quỹ đã thu!'))
        new_id = super(account_invoice, self).create(cr, uid, vals, context)
        new = self.browse(cr, uid, new_id)
        if not new.invoice_line:
            value = self.onchange_dien_giai_st(cr, uid, [new_id], new.dien_giai, new.so_tien, new.journal_id.id)['value']
            if value.get('invoice_line', False):
                self.write(cr, uid, [new_id], {'invoice_line': value['invoice_line']})
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        wf_service = netsvc.LocalService("workflow")
        old_state_vals = {}
        for line in self.browse(cr, uid, ids):
            old_state_vals[line.id]=line.state
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
            
            if vals.get('state',False)=='open' and line.mlg_type=='tra_gop_xe':
                sql = '''
                    select id from account_invoice where dien_giai like '%'''+line.name+'''%' limit 1
                '''
                cr.execute(sql)
                chiho_ids = [r[0] for r in cr.fetchall()]
                for chiho_id in chiho_ids:
                    wf_service.trg_validate(uid, 'account.invoice', chiho_id, 'invoice_open', cr)
            
        new_write = super(account_invoice, self).write(cr, uid, ids, vals, context)
        for line in self.browse(cr, uid, ids):
            if line.so_tien<=0:
                raise osv.except_osv(_('Cảnh báo!'), _('Không thể sửa với số tiền nhỏ hơn hoặc bằng "0"!'))
            
            if line.mlg_type =='phai_tra_ky_quy' and line.state=='draft':
                if line.loai_doituong in ['taixe','nhanvienvanphong']:
                    sql = '''
                        select case when sotien_dathu!=0 then sotien_dathu else 0 end sotien_dathu from res_partner where id=%s
                    '''%(line.partner_id.id)
                    cr.execute(sql)
                    sotien_dathu = cr.fetchone()[0]
                    if sotien_dathu<line.so_tien:
                        raise osv.except_osv(_('Cảnh báo!'), _('Không được phép chỉnh sửa với số tiền nhập vào lớn hơn số tiền ký quỹ đã thu!'))
                
                if line.loai_doituong == 'nhadautu':
                    sql = '''
                    
                        select case when sotien_dathu!=0 then sotien_dathu else 0 end sotien_dathu
                            from chi_nhanh_line where chinhanh_id=%s and partner_id=%s
                    '''%(line.chinhanh_id.id,line.partner_id.id)
                    cr.execute(sql)
                    sotien_dathu = cr.fetchone()[0]
                    if sotien_dathu<line.so_tien:
                        raise osv.except_osv(_('Cảnh báo!'), _('Không được phép chỉnh sửa với số tiền nhập vào lớn hơn số tiền ký quỹ đã thu!'))
            
            if vals.get('state',False)=='cancel' and old_state_vals and old_state_vals[line.id] in ['open','paid']:
                if line.payment_ids:
                    raise osv.except_osv(_('Cảnh báo!'), _('Vui lòng hủy hết thanh toán trước khi hủy công nợ này!'))
                
                date_now = time.strftime('%Y-%m-%d')
                startdate_now = time.strftime('%Y-%m-01')
                enddate_pre = datetime.strptime(startdate_now,'%Y-%m-%d')+timedelta(days=-1)
                enddate_pre_str = enddate_pre.strftime('%Y-%m-%d')
                startdate_pre_f = enddate_pre_str[:4]+'-'+enddate_pre_str[5:7]+'-01'
                startdate_pre_str = time.strftime(startdate_pre_f)
                if line.date_invoice<startdate_pre_str:
                    raise osv.except_osv(_('Cảnh báo!'),_('Không được hủy công nợ cho tháng cách tháng hiện tại hơn hai tháng!'))
                if line.date_invoice<startdate_now:
                    nodauky_obj = self.pool.get('congno.dauky')
                    nodauky_line_obj = self.pool.get('congno.dauky.line')
                    chitiet_nodauky_line_obj = self.pool.get('chitiet.congno.dauky.line')
                    stl_obj = self.pool.get('so.tien.lai')
                    date_invoice = datetime.strptime(line.date_invoice,'%Y-%m-%d')
                    end_of_month = str(date_invoice + relativedelta(months=+1, day=1, days=-1))[:10]
                    date_invoice_str = date_invoice.strftime('%Y-%m-%d')
                    day = int(end_of_month[8:10])-int(date_invoice_str[8:10])+3
                    next_month = date_invoice + timedelta(days=day)
                    next_month_str = next_month.strftime('%Y-%m-%d')
                    sql = '''
                        select id,date_start,date_stop from account_period
                            where '%s' between date_start and date_stop and special != 't' limit 1 
                    '''%(next_month_str)
                    cr.execute(sql)
                    period = cr.dictfetchone()
                    if period:
                        sql = '''
                            select id from congno_dauky where period_id=%s and partner_id=%s
                        '''%(period['id'],line.partner_id.id)
                        cr.execute(sql)
                        nodauky = cr.fetchone()
                        if nodauky:
                            sql = '''
                                select id from congno_dauky_line
                                    where congno_dauky_id=%s and chinhanh_id=%s and mlg_type='%s'
                            '''%(nodauky[0], line.chinhanh_id.id, line.mlg_type)
                            cr.execute(sql)
                            nodauky_line = cr.fetchone()
                            if nodauky_line:
                                sql = '''
                                    update congno_dauky_line set so_tien_no=so_tien_no-%s where id=%s                            
                                '''%(line.so_tien,nodauky_line[0])
                                cr.execute(sql)
                                for stl in line.lichsu_thutienlai_line:
                                    stl_obj.unlink(cr, uid, stl.id)
                                if line.mlg_type=='no_doanh_thu' and line.loai_nodoanhthu_id:
                                    sql = '''
                                        select id from chitiet_congno_dauky_line
                                            where congno_dauky_line_id=%s and loai_id=%s
                                    '''%(nodauky_line[0],line.loai_nodoanhthu_id.id)
                                    cr.execute(sql)
                                    chitiet_line = cr.fetchone()
                                    if chitiet_line:
                                        sql = '''
                                            update chitiet_congno_dauky_line set so_tien_no=so_tien_no-%s where id=%s  
                                        '''%(line.so_tien,chitiet_line[0])
                                        cr.execute(sql)
                                if line.mlg_type=='phai_thu_bao_hiem' and line.loai_baohiem_id:
                                    sql = '''
                                        select id from chitiet_congno_dauky_line
                                            where congno_dauky_line_id=%s and loai_id=%s
                                    '''%(nodauky_line[0],line.loai_baohiem_id.id)
                                    cr.execute(sql)
                                    chitiet_line = cr.fetchone()
                                    if chitiet_line:
                                        sql = '''
                                            update chitiet_congno_dauky_line set so_tien_no=so_tien_no-%s where id=%s  
                                        '''%(line.so_tien,chitiet_line[0])
                                        cr.execute(sql)
                                if line.mlg_type=='phat_vi_pham' and line.loai_vipham_id:
                                    sql = '''
                                        select id from chitiet_congno_dauky_line
                                            where congno_dauky_line_id=%s and loai_id=%s
                                    '''%(nodauky_line[0],line.loai_vipham_id.id)
                                    cr.execute(sql)
                                    chitiet_line = cr.fetchone()
                                    if chitiet_line:
                                        sql = '''
                                            update chitiet_congno_dauky_line set so_tien_no=so_tien_no-%s where id=%s  
                                        '''%(line.so_tien,chitiet_line[0])
                                        cr.execute(sql)
                                if line.mlg_type=='hoan_tam_ung' and line.loai_tamung_id:
                                    sql = '''
                                        select id from chitiet_congno_dauky_line
                                            where congno_dauky_line_id=%s and loai_id=%s
                                    '''%(nodauky_line[0],line.loai_tamung_id.id)
                                    cr.execute(sql)
                                    chitiet_line = cr.fetchone()
                                    if chitiet_line:
                                        sql = '''
                                            update chitiet_congno_dauky_line set so_tien_no=so_tien_no-%s where id=%s  
                                        '''%(line.so_tien,chitiet_line[0])
                                        cr.execute(sql)
                                if line.mlg_type=='thu_no_xuong' and line.ma_xuong_id:
                                    sql = '''
                                        select id from chitiet_congno_dauky_line
                                            where congno_dauky_line_id=%s and loai_id=%s
                                    '''%(nodauky_line[0],line.ma_xuong_id.id)
                                    cr.execute(sql)
                                    chitiet_line = cr.fetchone()
                                    if chitiet_line:
                                        sql = '''
                                            update chitiet_congno_dauky_line set so_tien_no=so_tien_no-%s where id=%s  
                                        '''%(line.so_tien,chitiet_line[0])
                                        cr.execute(sql)
                
            if vals.get('state',False)=='open' and old_state_vals and old_state_vals[line.id]=='draft':
                date_now = time.strftime('%Y-%m-%d')
                startdate_now = time.strftime('%Y-%m-01')
                enddate_pre = datetime.strptime(startdate_now,'%Y-%m-%d')+timedelta(days=-1)
                enddate_pre_str = enddate_pre.strftime('%Y-%m-%d')
                startdate_pre_f = enddate_pre_str[:4]+'-'+enddate_pre_str[5:7]+'-01'
                startdate_pre_str = time.strftime(startdate_pre_f)
                if line.date_invoice<startdate_pre_str:
                    raise osv.except_osv(_('Cảnh báo!'),_('Không được treo công nợ cho tháng cách tháng hiện tại hơn hai tháng!'))
                if line.date_invoice<startdate_now:
                    nodauky_obj = self.pool.get('congno.dauky')
                    nodauky_line_obj = self.pool.get('congno.dauky.line')
                    chitiet_nodauky_line_obj = self.pool.get('chitiet.congno.dauky.line')
                    date_invoice = datetime.strptime(line.date_invoice,'%Y-%m-%d')
                    end_of_month = str(date_invoice + relativedelta(months=+1, day=1, days=-1))[:10]
                    date_invoice_str = date_invoice.strftime('%Y-%m-%d')
                    day = int(end_of_month[8:10])-int(date_invoice_str[8:10])+3
                    next_month = date_invoice + timedelta(days=day)
                    next_month_str = next_month.strftime('%Y-%m-%d')
                    sql = '''
                        select id,date_start,date_stop from account_period
                            where '%s' between date_start and date_stop and special != 't' limit 1 
                    '''%(next_month_str)
                    cr.execute(sql)
                    period = cr.dictfetchone()
                    if period:
                        sql = '''
                            select id from congno_dauky where period_id=%s and partner_id=%s
                        '''%(period['id'],line.partner_id.id)
                        cr.execute(sql)
                        nodauky = cr.fetchone()
                        if nodauky:
                            sql = '''
                                select id from congno_dauky_line
                                    where congno_dauky_id=%s and chinhanh_id=%s and mlg_type='%s'
                            '''%(nodauky[0], line.chinhanh_id.id, line.mlg_type)
                            cr.execute(sql)
                            nodauky_line = cr.fetchone()
                            if nodauky_line:
                                sql = '''
                                    update congno_dauky_line set so_tien_no=so_tien_no+%s where id=%s                            
                                '''%(line.so_tien+line.sotien_lai,nodauky_line[0])
                                cr.execute(sql)
                                if line.mlg_type=='no_doanh_thu' and line.loai_nodoanhthu_id:
                                    sql = '''
                                        select id from chitiet_congno_dauky_line
                                            where congno_dauky_line_id=%s and loai_id=%s
                                    '''%(nodauky_line[0],line.loai_nodoanhthu_id.id)
                                    cr.execute(sql)
                                    chitiet_line = cr.fetchone()
                                    if chitiet_line:
                                        sql = '''
                                            update chitiet_congno_dauky_line set so_tien_no=so_tien_no+%s where id=%s  
                                        '''%(line.so_tien,chitiet_line[0])
                                        cr.execute(sql)
                                    else:
                                        chitiet_nodauky_line_obj.create(cr, uid, {
                                            'congno_dauky_line_id': nodauky_line[0],
                                            'loai_id': line.loai_nodoanhthu_id.id,
                                            'so_tien_no': line.so_tien,
                                        })
                                if line.mlg_type=='phai_thu_bao_hiem' and line.loai_baohiem_id:
                                    sql = '''
                                        select id from chitiet_congno_dauky_line
                                            where congno_dauky_line_id=%s and loai_id=%s
                                    '''%(nodauky_line[0],line.loai_baohiem_id.id)
                                    cr.execute(sql)
                                    chitiet_line = cr.fetchone()
                                    if chitiet_line:
                                        sql = '''
                                            update chitiet_congno_dauky_line set so_tien_no=so_tien_no+%s where id=%s  
                                        '''%(line.so_tien,chitiet_line[0])
                                        cr.execute(sql)
                                    else:
                                        chitiet_nodauky_line_obj.create(cr, uid, {
                                            'congno_dauky_line_id': nodauky_line[0],
                                            'loai_id': line.loai_baohiem_id.id,
                                            'so_tien_no': line.so_tien,
                                        })
                                if line.mlg_type=='phat_vi_pham' and line.loai_vipham_id:
                                    sql = '''
                                        select id from chitiet_congno_dauky_line
                                            where congno_dauky_line_id=%s and loai_id=%s
                                    '''%(nodauky_line[0],line.loai_vipham_id.id)
                                    cr.execute(sql)
                                    chitiet_line = cr.fetchone()
                                    if chitiet_line:
                                        sql = '''
                                            update chitiet_congno_dauky_line set so_tien_no=so_tien_no+%s where id=%s  
                                        '''%(line.so_tien,chitiet_line[0])
                                        cr.execute(sql)
                                    else:
                                        chitiet_nodauky_line_obj.create(cr, uid, {
                                            'congno_dauky_line_id': nodauky_line[0],
                                            'loai_id': line.loai_vipham_id.id,
                                            'so_tien_no': line.so_tien,
                                        })
                                if line.mlg_type=='hoan_tam_ung' and line.loai_tamung_id:
                                    sql = '''
                                        select id from chitiet_congno_dauky_line
                                            where congno_dauky_line_id=%s and loai_id=%s
                                    '''%(nodauky_line[0],line.loai_tamung_id.id)
                                    cr.execute(sql)
                                    chitiet_line = cr.fetchone()
                                    if chitiet_line:
                                        sql = '''
                                            update chitiet_congno_dauky_line set so_tien_no=so_tien_no+%s where id=%s  
                                        '''%(line.so_tien,chitiet_line[0])
                                        cr.execute(sql)
                                    else:
                                        chitiet_nodauky_line_obj.create(cr, uid, {
                                            'congno_dauky_line_id': nodauky_line[0],
                                            'loai_id': line.loai_tamung_id.id,
                                            'so_tien_no': line.so_tien,
                                        })
                                if line.mlg_type=='thu_no_xuong' and line.ma_xuong_id:
                                    sql = '''
                                        select id from chitiet_congno_dauky_line
                                            where congno_dauky_line_id=%s and loai_id=%s
                                    '''%(nodauky_line[0],line.ma_xuong_id.id)
                                    cr.execute(sql)
                                    chitiet_line = cr.fetchone()
                                    if chitiet_line:
                                        sql = '''
                                            update chitiet_congno_dauky_line set so_tien_no=so_tien_no+%s where id=%s  
                                        '''%(line.so_tien,chitiet_line[0])
                                        cr.execute(sql)
                                    else:
                                        chitiet_nodauky_line_obj.create(cr, uid, {
                                            'congno_dauky_line_id': nodauky_line[0],
                                            'loai_id': line.ma_xuong_id.id,
                                            'so_tien_no': line.so_tien,
                                        })
                            else:
                                chitiet_loai_line=[]
                                if line.mlg_type=='no_doanh_thu' and line.loai_nodoanhthu_id:
                                    chitiet_loai_line = [(0,0,{
                                                            'loai_id': line.loai_nodoanhthu_id.id,
                                                            'so_tien_no': line.so_tien,
                                                        })]
                                if line.mlg_type=='phai_thu_bao_hiem' and line.loai_baohiem_id:
                                    chitiet_loai_line = [(0,0,{
                                                            'loai_id': line.loai_baohiem_id.id,
                                                            'so_tien_no': line.so_tien,
                                                        })]
                                if line.mlg_type=='phat_vi_pham' and line.loai_vipham_id:
                                    chitiet_loai_line = [(0,0,{
                                                            'loai_id': line.loai_vipham_id.id,
                                                            'so_tien_no': line.so_tien,
                                                        })]
                                if line.mlg_type=='hoan_tam_ung' and line.loai_tamung_id:
                                    chitiet_loai_line = [(0,0,{
                                                            'loai_id': line.loai_tamung_id.id,
                                                            'so_tien_no': line.so_tien,
                                                        })]
                                if line.mlg_type=='thu_no_xuong' and line.ma_xuong_id:
                                    chitiet_loai_line = [(0,0,{
                                                            'loai_id': line.ma_xuong_id.id,
                                                            'so_tien_no': line.so_tien,
                                                        })]
                                nodauky_line_obj.create(cr, uid, {
                                    'congno_dauky_id': nodauky[0],
                                    'chinhanh_id': line.chinhanh_id.id,
                                    'mlg_type': line.mlg_type,
                                    'so_tien_no': line.so_tien,
                                    'chitiet_loai_line': chitiet_loai_line,
                                })
                        else:
                            sql = '''
                                select sum(COALESCE(residual,0) + COALESCE(sotien_lai_conlai,0)) as so_tien_no,mlg_type,chinhanh_id
                                    from account_invoice
                                    where state='open' and partner_id=%s and date_invoice<'%s'
                                    group by chinhanh_id,mlg_type
                            '''%(line.partner_id.id,period['date_start'])
                            cr.execute(sql)
                            congno_dauky_line = []
                            for invoice in cr.dictfetchall():
                                chitiet_loai_line = []
                                if invoice['mlg_type']=='no_doanh_thu':
                                    sql = '''
                                        select sum(COALESCE(residual,0) + COALESCE(sotien_lai_conlai,0)) as so_tien_no,loai_nodoanhthu_id
                                            from account_invoice
                                            where state='open' and partner_id=%s and mlg_type='%s' and chinhanh_id=%s and date_invoice<'%s'
                                            group by loai_nodoanhthu_id
                                    '''%(line.partner_id.id,invoice['mlg_type'],invoice['chinhanh_id'],period['date_start'])
                                    cr.execute(sql)
                                    for inv_line in cr.dictfetchall():
                                        chitiet_loai_line.append((0,0,{
                                            'loai_id': inv_line['loai_nodoanhthu_id'],
                                            'so_tien_no': inv_line['so_tien_no'],
                                        }))
                                if invoice['mlg_type']=='phai_thu_bao_hiem':
                                    sql = '''
                                        select sum(COALESCE(residual,0) + COALESCE(sotien_lai_conlai,0)) as so_tien_no,loai_baohiem_id
                                            from account_invoice
                                            where state='open' and partner_id=%s and mlg_type='%s' and chinhanh_id=%s and date_invoice<'%s'
                                            group by loai_baohiem_id
                                    '''%(line.partner_id.id,invoice['mlg_type'],invoice['chinhanh_id'],period['date_start'])
                                    cr.execute(sql)
                                    for inv_line in cr.dictfetchall():
                                        chitiet_loai_line.append((0,0,{
                                            'loai_id': inv_line['loai_baohiem_id'],
                                            'so_tien_no': inv_line['so_tien_no'],
                                        }))
                                if invoice['mlg_type']=='phat_vi_pham':
                                    sql = '''
                                        select sum(COALESCE(residual,0) + COALESCE(sotien_lai_conlai,0)) as so_tien_no,loai_vipham_id
                                            from account_invoice
                                            where state='open' and partner_id=%s and mlg_type='%s' and chinhanh_id=%s and date_invoice<'%s'
                                            group by loai_vipham_id
                                    '''%(line.partner_id.id,invoice['mlg_type'],invoice['chinhanh_id'],period['date_start'])
                                    cr.execute(sql)
                                    for inv_line in cr.dictfetchall():
                                        chitiet_loai_line.append((0,0,{
                                            'loai_id': inv_line['loai_vipham_id'],
                                            'so_tien_no': inv_line['so_tien_no'],
                                        }))
                                if invoice['mlg_type']=='hoan_tam_ung':
                                    sql = '''
                                        select sum(COALESCE(residual,0) + COALESCE(sotien_lai_conlai,0)) as so_tien_no,loai_tamung_id
                                            from account_invoice
                                            where state='open' and partner_id=%s and mlg_type='%s' and chinhanh_id=%s and date_invoice<'%s'
                                            group by loai_tamung_id
                                    '''%(line.partner_id.id,invoice['mlg_type'],invoice['chinhanh_id'],period['date_start'])
                                    cr.execute(sql)
                                    for inv_line in cr.dictfetchall():
                                        chitiet_loai_line.append((0,0,{
                                            'loai_id': inv_line['loai_tamung_id'],
                                            'so_tien_no': inv_line['so_tien_no'],
                                        }))
                                if invoice['mlg_type']=='thu_no_xuong':
                                    sql = '''
                                        select sum(COALESCE(residual,0) + COALESCE(sotien_lai_conlai,0)) as so_tien_no,ma_xuong_id
                                            from account_invoice
                                            where state='open' and partner_id=%s and mlg_type='%s' and chinhanh_id=%s and date_invoice<'%s'
                                            group by ma_xuong_id
                                    '''%(line.partner_id.id,invoice['mlg_type'],invoice['chinhanh_id'],period['date_start'])
                                    cr.execute(sql)
                                    for inv_line in cr.dictfetchall():
                                        chitiet_loai_line.append((0,0,{
                                            'loai_id': inv_line['ma_xuong_id'],
                                            'so_tien_no': inv_line['so_tien_no'],
                                        }))
                                congno_dauky_line.append((0,0,{
                                    'chinhanh_id': invoice['chinhanh_id'],
                                    'mlg_type': invoice['mlg_type'],
                                    'so_tien_no': invoice['so_tien_no'],
                                    'chitiet_loai_line': chitiet_loai_line,
                                }))
                            nodauky_obj.create(cr, uid, {
                                'period_id': period['id'],
                                'partner_id': line.partner_id.id,
                                'congno_dauky_line': congno_dauky_line,               
                            })
            if not line.invoice_line:
                value = self.onchange_dien_giai_st(cr, uid, [line.id], line.dien_giai, line.so_tien, line.journal_id.id)['value']
                if value.get('invoice_line', False):
                    self.write(cr, uid, [line.id], {'invoice_line': value['invoice_line']})
        return new_write
    
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
#                     chinhanh_id = partner.property_account_receivable.parent_id.id
                else:
                    account_id = partner.property_account_payable and partner.property_account_payable.id or False
#                     chinhanh_id = partner.property_account_payable.parent_id.id
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
    
    def onchange_loaidoituong(self, cr, uid, ids, loai_doituong=False,loai_nodoanhthu_id=False, context=None):
        domain = {}
        vals = {'partner_id':False,'account_id':False}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        if ids:
            invoice = self.browse(cr, uid, ids[0])
            user = invoice.user_id
        chinhanh_id = user.chinhanh_id and user.chinhanh_id.id or False
#         if loai_doituong=='taixe':
#             domain={'partner_id': [('taixe','=',True),('property_account_receivable.parent_id','=',chinhanh_id)]}
        if loai_doituong=='nhadautu':
#             sql = '''
#                 select partner_id from chi_nhanh_line where chinhanh_id=%s
#             '''%(chinhanh_id)
#             cr.execute(sql)
#             partner_ids = [r[0] for r in cr.fetchall()]
#             domain={'partner_id': [('nhadautu','=',True),('id','in',partner_ids)]}
            vals.update({'chinhanh_ndt_id': chinhanh_id})
#         if loai_doituong=='nhanvienvanphong':
#             domain={'partner_id': [('nhanvienvanphong','=',True),('property_account_receivable.parent_id','=',chinhanh_id)]}
        if loai_doituong!='taixe':
            if loai_nodoanhthu_id:
                loai_nodoanhthu = self.pool.get('loai.no.doanh.thu').browse(cr, uid, loai_nodoanhthu_id)
                if loai_nodoanhthu.code.upper()=='NO_DOANH_THU':
                    vals.update({'loai_nodoanhthu_id': False})
        return {'value': vals, 'domain': domain}
    
    def onchange_dien_giai_st(self, cr, uid, ids, dien_giai='/',so_tien=False,journal_id=False, context=None):
        domain = {}
        vals = {}
        if ids and so_tien:
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
        journal_ids = self.pool.get('account.journal').search(cr, uid, [('chinhanh_id','=',inv.chinhanh_id.id),('type','=','cash')])
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
                'default_sotien_tragopxe': inv.residual+inv.sotien_lai_conlai,
                'default_sotien_lai_conlai': inv.sotien_lai_conlai,
                'default_reference': inv.name,
                'default_journal_id': journal_ids and journal_ids[0] or False,
                'default_bai_giaoca_id': inv.bai_giaoca_id and inv.bai_giaoca_id.id or False,
                'default_mlg_type': inv.mlg_type,
                'close_after_process': True,
                'invoice_type': inv.type,
                'invoice_id': inv.id,
                'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                'default_loai_giaodich': 'Giao dịch thu chi trực tiếp',
                'default_chinhanh_id': inv.chinhanh_id.id,
                'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
            }
        }
        
    def xoa_thanh_toan(self, cr, uid, mlg_type, invoice_number, context=None):
        try:
            voucher_obj = self.pool.get('account.voucher')
            wf_service = netsvc.LocalService("workflow")
            sql = '''
                select id from account_voucher where reference='%s'
            '''%(invoice_number)
            cr.execute(sql)
            vouhcer_ids = [r[0] for r in cr.fetchall()]
            voucher_obj.cancel_voucher(cr, 1, vouhcer_ids, context)
            voucher_obj.unlink(cr, 1, vouhcer_ids)
        except Exception, e:
            cr.rollback()
        return True
    
    def xoa_cong_no(self, cr, uid, mlg_type, invoice_number, context=None):
        try:
            wf_service = netsvc.LocalService("workflow")
            self.xoa_thanh_toan(cr, 1, mlg_type, invoice_number, context)
            sql = '''
                select id from account_invoice where mlg_type='%s' and name='%s'
            '''%(mlg_type, invoice_number)
            cr.execute(sql)
            invoice_ids = [r[0] for r in cr.fetchall()]
            for invoice_id in invoice_ids:
                wf_service.trg_validate(1, 'account.invoice', invoice_id, 'invoice_cancel', cr)
                sql = '''
                    delete from account_invoice_line where invoice_id=%s;
                    delete from account_invoice where id=%s;
                '''%(invoice_id,invoice_id)
                cr.execute(sql)
        except Exception, e:
            cr.rollback()
        return True
    
#     @api.multi
#     def action_cancel(self):
#         voucher_obj = self.pool.get('account.voucher')
#         stl_obj = self.pool.get('so.tien.lai')
#         for inv in self:
#             voucher_ids = voucher_obj.search(self.env.cr, self.env.uid, [('reference', '=', inv.name),('state','=','posted')])
#             voucher_obj.cancel_voucher(self.env.cr, self.env.uid, voucher_ids)
#         
#         res = super(account_invoice, self).action_cancel()
#         return res
    
    @api.multi
    def bt_huythanhtoan_hoadon(self):
        wf_service = netsvc.LocalService("workflow")
        voucher_obj = self.pool.get('account.voucher')
        for inv in self:
            voucher_ids = voucher_obj.search(self.env.cr, self.env.uid, [('reference', '=', inv.name),('state','=','posted')])
            if voucher_ids:
                voucher_obj.cancel_voucher(self.env.cr, self.env.uid, voucher_ids)
                wf_service.trg_validate(self.env.uid, 'account.invoice', inv.id, 'invoice_cancel', self.env.cr)
        return True
        
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

class so_tien_lai(osv.osv):
    _name = "so.tien.lai"
    
    _columns = {
        'invoice_id': fields.many2one('account.invoice', 'Invoice', ondelete='cascade'),
        'ngay': fields.date('Ngày'),
        'fusion_id': fields.char('Fusion Chi', size=1024),
        'so_tien': fields.float('Số tiền',digits=(16,0)),
        'move_line_id': fields.many2one('account.move.line', 'Account move line'),
        'loai_giaodich': fields.char('Loại giao dịch', size=1024),
    }
    
so_tien_lai()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
