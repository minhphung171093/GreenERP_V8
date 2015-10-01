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
    }
loai_ky_quy()

class loai_vi_pham(osv.osv):
    _name = "loai.vi.pham"
    _columns = {
        'name': fields.char('Tên', size=1024, required=True),
        'description': fields.char('Mô tả', size=1024, required=True),
    }
loai_vi_pham()

class bai_giaoca(osv.osv):
    _name = "bai.giaoca"
    _columns = {
        'name': fields.char('Tên bãi giao ca', size=1024, required=True),
        'code': fields.char('Mã bãi giao ca', size=1024, required=True),
        'thungan_id': fields.many2one('thungan.bai.giaoca', 'Thu ngân bãi giao ca', required=True),
        'dieuhanh_id': fields.many2one('dieuhanh.bai.giaoca', 'Điều hành bãi giao ca', required=True),
    }
    
bai_giaoca()

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    _columns = {
        'mlg_type': fields.selection([('no_doanh_thu','Nợ doanh thu'),
                                      ('chi_ho_dien_thoai','Chi hộ điện thoại'),
                                      ('phai_thu_bao_hiem','Phải thu bảo hiểm'),
                                      ('phai_tra_ky_quy','Phải trả ký quỹ'),
                                      ('phat_vi_pham','Phạt vi phạm'),
                                      ('thu_no_xuong','Thu nợ xưởng'),
                                      ('thu_phi_thuong_hieu','Thu phí thương hiệu'),
                                      ('tra_gop_xe','Trả góp xe'),
                                      ('tam_ung','Tạm ứng')],'Loại'),
        'doi_xe_id': fields.many2one('account.account', 'Đội xe'),
        'bai_giaoca_id': fields.many2one('bai.giaoca', 'Bãi giao ca'),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, readonly=True, states={'draft':[('readonly',False)]},
                                      domain="[('type', 'in', ['cash','bank']), ('company_id', '=', company_id)]"),
        'bien_so_xe': fields.char('Biển số xe', size=1024),
        'so_hop_dong': fields.char('Số hợp đồng', size=1024),
        'loai_doituong_id': fields.many2one('loai.doi.tuong', 'Loại đối tượng'),
        'so_hoa_don':fields.char('Số hóa đơn',size = 64),
        'loai_kyquy_id': fields.many2one('loai.ky.quy', 'Loại ký quỹ'),
        'loai_vipham_id': fields.many2one('loai.vi.pham', 'Loại vi phạm'),
        'chinhanh_id': fields.many2one('account.account', 'Chi nhánh'),
        'so_bien_ban_vi_pham':fields.char('Số biên bản vi phạm',size = 64),
    }
    
    _defaults = {
        'date_invoice': time.strftime('%Y-%m-%d'),
        'journal_id': False,
    }
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('mlg_type') and (vals.get('name', '/') == '/' or 'name' not in vals):
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, vals['mlg_type'], context=context) or '/'
        return super(account_invoice, self).create(cr, uid, vals, context)
    
    def onchange_doituong(self, cr, uid, ids, partner_id=False, context=None):
        vals = {}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
            vals = {'account_id': partner.property_account_receivable.id,
                    'loai_doituong_id': partner.loai_doituong_id and partner.loai_doituong_id.id or False,
                    'bai_giaoca_id': partner.bai_giaoca_id and partner.bai_giaoca_id.id or False}
        return {'value': vals}
    
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
                
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
        self._log_event()
        return True
    
account_invoice()

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    
    _columns = {
        'name': fields.char('Diễn giải', size=1024, required=True),
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
    
    _columns = {
        'bai_giaoca_id': fields.many2one('bai.giaoca', 'Bãi giao ca'),
    }
    
account_move_line()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
