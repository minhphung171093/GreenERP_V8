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
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class account_voucher(osv.osv):
    _inherit = "account.voucher"
    _columns = {
        'bai_giaoca_id': fields.many2one('bai.giaoca', 'Bãi giao ca'),
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
                                      ('chi_ho','Chi hộ'),],'Loại công nợ'),
        'chinhanh_id': fields.many2one('account.account','Chi nhánh'),
        'fusion_id': fields.char('Fusion Thu', size=1024),
        'loai_giaodich': fields.char('Loại giao dịch', size=1024),
        'sotien_tragopxe': fields.float('Số tiền đã trả', digits=(16,0)),
        'sotien_lai_conlai': fields.float('Số tiền lãi còn lại',digits=(16,0)),
        'sotienlai_id': fields.many2one('so.tien.lai', 'So tien lai'),
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
                'fusion_id': line.fusion_id,
                'loai_giaodich': line.loai_giaodich,
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
                
            if voucher.fusion_id:
                cr.execute(''' update account_move_line set fusion_id=%s where move_id=%s ''',(voucher.fusion_id,move_id,))
            
            if voucher.loai_giaodich:
                cr.execute(''' update account_move_line set loai_giaodich=%s where move_id=%s ''',(voucher.loai_giaodich,move_id,))
            
            if voucher.sotienlai_id:
                cr.execute(''' select id from account_move_line where move_id=%s and credit!=0 limit 1 ''',(move_id,))
                moveline = cr.fetchone()
                if moveline:
                    cr.execute(''' update so_tien_lai set move_line_id=%s where id=%s ''',(moveline[0],voucher.sotienlai_id.id,))
            if voucher.journal_id.entry_posted:
                move_pool.post(cr, uid, [move_id], context={})
            # We automatically reconcile the account move lines.
            reconcile = False
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    reconcile = move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
        return True
    
    def button_proforma_voucher(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        for line in self.browse(cr, uid, ids):
            
            startdate_now = time.strftime('%Y-%m-01')
            enddate_pre = datetime.strptime(startdate_now,'%Y-%m-%d')+timedelta(days=-1)
            enddate_pre_str = enddate_pre.strftime('%Y-%m-%d')
            startdate_pre_f = '%Y-'+enddate_pre_str[5:7]+'-01'
            startdate_pre_str = time.strftime(startdate_pre_f)
            if line.date<startdate_pre_str:
                raise osv.except_osv(_('Cảnh báo!'),_('Không được cấn trừ công nợ cho tháng cách tháng hiện tại hơn hai tháng!'))
            
            if line.mlg_type=='phai_tra_ky_quy' and line.partner_id:
                kyquy_obj = self.pool.get('thu.ky.quy')
                sotien_cantru = line.amount
                sql = '''
                    select id, sotien_conlai
                        from thu_ky_quy
                        
                        where sotien_conlai>0 and chinhanh_id=%s and partner_id=%s and state='paid'
                        
                        order by ngay_thu,id
                '''%(line.chinhanh_id.id,line.partner_id.id)
                cr.execute(sql)
                for kyquy in cr.dictfetchall():
                    if not sotien_cantru:
                        break
                    if sotien_cantru<kyquy['sotien_conlai']:
                        kyquy_obj.write(cr, uid, [kyquy['id']],{'sotien_conlai':kyquy['sotien_conlai']-sotien_cantru})
                        sotien_cantru = 0
                    else:
                        kyquy_obj.write(cr, uid, [kyquy['id']],{'sotien_conlai':0})
                        sotien_cantru = sotien_cantru-kyquy['sotien_conlai']
                if sotien_cantru>0:
                    raise osv.except_osv(_('Cảnh báo!'), 'Số tiền thanh toán lớn hơn số tiền đã thu còn lại!')
            
        if context.get('invoice_id', False):
            for voucher in self.browse(cr, uid, ids):
                
                invoice = self.pool.get('account.invoice').browse(cr, uid, context['invoice_id'])
                if invoice.date_invoice>voucher.date:
                    raise osv.except_osv(_('Cảnh báo!'), 'Ngày thanh toán phải lớn hơn ngày công nợ!')
                
                date_now = time.strftime('%Y-%m-%d')
                if date_now[:4]!=voucher.date[:4] or date_now[5:7]!=voucher.date[5:7]:
                    nodauky_obj = self.pool.get('congno.dauky')
                    nodauky_line_obj = self.pool.get('congno.dauky.line')
                    date_voucher = datetime.strptime(voucher.date,'%Y-%m-%d')
                    end_of_month = str(date_voucher + relativedelta(months=+1, day=1, days=-1))[:10]
                    date_voucher_str = date_voucher.strftime('%Y-%m-%d')
                    day = int(end_of_month[8:10])-int(date_voucher_str[8:10])+3
                    next_month = date_voucher + timedelta(days=day)
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
                        '''%(period['id'],voucher.partner_id.id)
                        cr.execute(sql)
                        nodauky = cr.fetchone()
                        if nodauky:
                            sql = '''
                                select id from congno_dauky_line
                                    where congno_dauky_id=%s and chinhanh_id=%s and mlg_type='%s'
                            '''%(nodauky[0], voucher.chinhanh_id.id, voucher.mlg_type)
                            cr.execute(sql)
                            nodauky_line = cr.fetchone()
                            if nodauky_line:
                                sql = '''
                                    update congno_dauky_line set so_tien_no=so_tien_no-%s where id=%s                            
                                '''%(voucher.amount,nodauky_line[0])
                                cr.execute(sql)
                            else:
                                nodauky_line_obj.create(cr, uid, {
                                    'congno_dauky_id': nodauky[0],
                                    'chinhanh_id': voucher.chinhanh_id.id,
                                    'mlg_type': voucher.mlg_type,
                                    'so_tien_no': invoice.so_tien-voucher.amount,
                                })
                        else:
                            sql = '''
                                select sum(COALESCE(residual,0) + COALESCE(sotien_lai_conlai,0)) as so_tien_no,mlg_type,chinhanh_id
                                    from account_invoice
                                    where state='open' and partner_id=%s and date_invoice<'%s'
                                    group by chinhanh_id,mlg_type
                            '''%(voucher.partner_id.id,period['date_start'])
                            cr.execute(sql)
                            congno_dauky_line = []
                            for inv in cr.dictfetchall():
                                congno_dauky_line.append((0,0,{
                                    'chinhanh_id': inv['chinhanh_id'],
                                    'mlg_type': inv['mlg_type'],
                                    'so_tien_no': inv['so_tien_no']-voucher.amount,
                                }))
                            nodauky_obj.create(cr, uid, {
                                'period_id': period['id'],
                                'partner_id': voucher.partner_id.id,
                                'congno_dauky_line': congno_dauky_line,               
                            })
                
                if voucher.sotien_tragopxe and voucher.sotien_lai_conlai:
                    if voucher.sotien_tragopxe>=voucher.sotien_lai_conlai:
                        sotien = voucher.sotien_lai_conlai
                    else:
                        sotien = voucher.sotien_tragopxe
                    sotienlai_id = self.pool.get('so.tien.lai').create(cr, uid, {
                        'invoice_id': context['invoice_id'],
                        'ngay': voucher.date,
                        'fusion_id': voucher.fusion_id,
                        'so_tien': sotien,
                    })
                    self.write(cr, uid, [voucher.id], {'sotienlai_id':sotienlai_id})
        self.signal_workflow(cr, uid, ids, 'proforma_voucher')
        return {'type': 'ir.actions.act_window_close'}
    
    def onchange_sotien_tragopxe(self, cr, uid, ids, sotien_tragopxe, mlg_type, sotien_lai_conlai, context=None):
        res = {'value':{}}
        if mlg_type=='tra_gop_xe':
            sotientra = sotien_tragopxe
            sotienlai = sotien_lai_conlai
            if sotientra>=sotienlai:
                sotientra = sotientra-sotienlai
            else:
                sotientra = 0
            res['value'].update({'amount': sotientra})
        return res
    
account_voucher()

class account_voucher_line(osv.osv):
    _inherit = "account.voucher.line"
    _columns = {
        'bai_giaoca_id': fields.many2one('bai.giaoca', 'Bãi giao ca'),
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
                                      ('chi_ho','Chi hộ'),],'Loại công nợ'),
        'fusion_id': fields.char('Fusion Thu', size=1024),
        'loai_giaodich': fields.char('Loại giao dịch', size=1024),
    }
    
account_voucher_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
