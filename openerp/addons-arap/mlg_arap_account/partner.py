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

from operator import itemgetter
import time

from openerp.osv import fields, osv
from openerp import api
from openerp.tools.translate import _
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class res_partner(osv.osv):
    _inherit = 'res.partner'

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(res_partner, self).default_get(cr, uid, fields, context=context)
        if context.get('loai_doituong', False):
            sql = '''
                select res_id from ir_model_data where module='mlg_arap_account' and name='%s'
            '''%(context['loai_doituong'])
            cr.execute(sql)
            loai = cr.fetchone()
            if loai:
                res.update({'loai_doituong_id': loai[0]})
        if context.get('matdinh_receivable_payable', False):
            sql = '''
                select id from account_account where code='20' limit 1
            '''
            cr.execute(sql)
            account_id = cr.fetchone()
            res.update({'property_account_receivable': account_id[0],'property_account_payable': account_id[0],'account_ht_id': account_id[0]})
        return res
    
    def _get_sotien(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for partner in self.browse(cr, uid, ids, context=context):
            res[partner.id] = {
                'sotien_dathu': 0,
                'sotien_conlai': 0,
            }
            if partner.taixe or partner.nhanvienvanphong:
                sql = '''
                    select case when sum(sotien_conlai)!=0 then sum(sotien_conlai) else 0 end sotien from thu_ky_quy where partner_id=%s and state='paid'
                '''%(partner.id)
                cr.execute(sql)
                res[partner.id]['sotien_dathu'] = cr.fetchone()[0]
                res[partner.id]['sotien_conlai'] = partner.sotien_phaithu - res[partner.id]['sotien_dathu']
        return res
    
    def _get_partner(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('thu.ky.quy').browse(cr, uid, ids, context=context):
            result[line.partner_id.id] = True
        return result.keys()
    
    def _get_kyquy(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for partner in self.browse(cr, uid, ids, context=context):
#             sql = '''
#                 select id from thu_ky_quy where partner_id=%s and state='paid'
#             '''%(partner.id)
#             cr.execute(sql)
#             kyquy_ids = [r[0] for r in cr.fetchall()]
            kyquy_ids = self.pool.get('thu.ky.quy').search(cr, uid, [('partner_id','=',partner.id),('state','=','paid')])
            res[partner.id] = kyquy_ids
        return res
    
    def _get_congno(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        congno_obj = self.pool.get('tong.cong.no')
        for partner in self.browse(cr, uid, ids, context=context):
            cr.execute('delete from tong_cong_no where partner_id=%s',(partner.id,))
            
            sql = '''
                select mlg_type,case when sum(COALESCE(so_tien,0)+COALESCE(sotien_lai,0))!=0 then sum(COALESCE(so_tien,0)+COALESCE(sotien_lai,0)) else 0 end sotien_congno,
                        case when sum(COALESCE(residual,0)+COALESCE(sotien_lai_conlai,0))!=0 then sum(COALESCE(residual,0)+COALESCE(sotien_lai_conlai,0)) else 0 end sotien_conlai
                    from account_invoice
                    where partner_id=%s and state in ('open','paid') and type='out_invoice'
                    group by mlg_type
            '''%(partner.id)
            cr.execute(sql)
            vals = []
            for line in cr.dictfetchall():
                congno_obj.create(cr, uid, {
                    'partner_id': partner.id,
                    'mlg_type': line['mlg_type'],
                    'sotien_congno': line['sotien_congno'],
                    'sotien_dathu': line['sotien_congno']-line['sotien_conlai'],
                    'sotien_conlai': line['sotien_conlai'],
                })
            res[partner.id] = 'DONE'
        return res
    
    def _get_show_ctkq_ndt(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids, context=context):
            res[partner.id] = False
            for chinhanh in partner.chinhanh_line:
                if chinhanh.sotien_dathu>0:
                    res[partner.id] = True
                    break
        return res
    
    _columns = {
        'property_account_payable': fields.property(
            type='many2one',
            relation='account.account',
            string="Account Payable",
            domain="[('type', '=', 'other')]",
            help="This account will be used instead of the default one as the payable account for the current partner",
            required=False),
        'property_account_receivable': fields.property(
            type='many2one',
            relation='account.account',
            string="Account Receivable",
            domain="[('type', '=', 'other')]",
            help="This account will be used instead of the default one as the receivable account for the current partner",
            required=False),
        'bai_giaoca_id': fields.many2one('bai.giaoca', 'Bãi giao ca'),
        'account_ht_id': fields.many2one('account.account', 'Account'),
        'loai_doituong_id': fields.many2one('loai.doi.tuong', 'Loại đối tượng'),
        'ma_doi_tuong': fields.char('Mã đối tượng', size=1024),
        'bien_so_xe_id': fields.many2one('bien.so.xe','Biển số xe'),
        'loai_doituong': fields.related('loai_doituong_id', 'name', type='char', string='Loại đối tượng', readonly=True, store=True),
        'taixe': fields.boolean('Lái xe'),
        'nhadautu': fields.boolean('Nhà đầu tư'),
        'nhadautugiantiep': fields.boolean('Nhà đầu tư gián tiếp'),
        'nhanvienvanphong': fields.boolean('Nhân viên văn phòng'),
        'chinhanh_line': fields.one2many('chi.nhanh.line','partner_id','Chi nhánh NDT'),
        'cmnd': fields.char('Số CMND', size=1024),
        'mst': fields.char('Mã số thuế', size=1024),
        'giayphep_kinhdoanh': fields.char('Mã số giấy phép kinh doanh', size=1024),
        'chinhanh_id': fields.many2one('account.account','Chi nhánh', readonly=False),
        'create_user_id': fields.many2one('res.users','User'),
        'sotien_phaithu': fields.float('Số tiền phải thu',digits=(16,0)),
        'sotien_phaithu_dinhky': fields.float('Số tiền phải thu định kỳ',digits=(16,0)),
        'sotien_dathu': fields.function(_get_sotien, string='Số tiền đã thu', multi='sotien',
            store={
                'res.partner': (lambda self, cr, uid, ids, c={}: ids, ['sotien_phaithu','sotien_phaithu_dinhky'], 10),
                'thu.ky.quy': (_get_partner, ['state', 'so_tien', 'partner_id','sotien_conlai'], 10),
            },type='float',digits=(16,0)),
        'sotien_conlai': fields.function(_get_sotien, string='Số tiền còn lại', multi='sotien',
            store={
                'res.partner': (lambda self, cr, uid, ids, c={}: ids, ['sotien_phaithu','sotien_phaithu_dinhky'], 10),
                'thu.ky.quy': (_get_partner, ['state', 'so_tien', 'partner_id','sotien_conlai'], 10),
            },type='float',digits=(16,0)),
        'ky_quy_ids': fields.function(_get_kyquy, relation='thu.ky.quy',type='many2many', string='Ký quỹ', readonly=True),
        'tinh_congno': fields.function(_get_congno, type='char', string='Tính công nợ', readonly=True),
        'congno_line': fields.one2many('tong.cong.no', 'partner_id','Chi tiết công nợ', readonly=True),
        'loai_doituong_lienket': fields.selection([('baohiem','Bảo hiểm'),('congty_thanhvien','Công ty thành viên')],'Loại đối tượng liên kết'),
        'doituong_lienket': fields.char('Mã đối tượng liên kết', size=1024),
        'show_ctkq_ndt': fields.function(_get_show_ctkq_ndt,type='boolean',string='Hiện ctkq ndt'),
    }
    
    def _get_chinhanh(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.chinhanh_id and user.chinhanh_id.id or False

    _defaults = {
        'chinhanh_id': _get_chinhanh,
        'create_user_id': lambda self,cr, uid, context: uid,
    }
    
    def _check_ma_doi_tuong(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            sql = '''
                select id from res_partner where id!=%s and ma_doi_tuong is not null and upper(ma_doi_tuong)='%s'
            '''%(line.id,line.ma_doi_tuong.upper())
            cr.execute(sql)
            object_ids = [r[0] for r in cr.fetchall()]
#             object_ids = self.search(cr, uid, [('id','!=', line.id),('ma_doi_tuong','!=', False),('ma_doi_tuong','=', line.ma_doi_tuong)])
            if object_ids:
                return False
        return True
    
    def _check_cmnd(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            taixe_ids = self.search(cr, 1, [('id','!=', line.id),('cmnd','!=', False),('cmnd','=', line.cmnd),('taixe','=',True)])
            if line.taixe and taixe_ids:
                return False
            nhadautu_ids = self.search(cr, 1, [('id','!=', line.id),('cmnd','!=', False),('cmnd','=', line.cmnd),('nhadautu','=',True)])
            if line.nhadautu and nhadautu_ids:
                return False
            nhanvienvanphong_ids = self.search(cr, 1, [('id','!=', line.id),('cmnd','!=', False),('cmnd','=', line.cmnd),('nhanvienvanphong','=',True)])
            if line.nhanvienvanphong and nhanvienvanphong_ids:
                return False
        return True

#     def _check_mst(self, cr, uid, ids, context=None):
#         for line in self.browse(cr, uid, ids):
#             object_ids = self.search(cr, uid, [('id','!=', line.id),('mst','!=', False),('mst','=', line.mst)])
#             if object_ids:
#                 return False
#         return True
#     
#     def _check_gpkd(self, cr, uid, ids, context=None):
#         for line in self.browse(cr, uid, ids):
#             object_ids = self.search(cr, uid, [('id','!=', line.id),('giayphep_kinhdoanh','!=', False),('giayphep_kinhdoanh','=', line.giayphep_kinhdoanh)])
#             if object_ids:
#                 return False
#         return True
    
    _constraints = [
        (_check_ma_doi_tuong, 'Không được trùng mã đối tượng', ['ma_doi_tuong']),
        (_check_cmnd, 'Không được trùng CMND', ['cmnd']),
#         (_check_mst, 'Không được trùng MST', ['mst']),
#         (_check_gpkd, 'Không được trùng giấy phép kinh doanh', ['giayphep_kinhdoanh']),
    ]
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        chinhanh_id = user.chinhanh_id and user.chinhanh_id.id or False
        if context.get('cong_no_thu', False) and context.get('loai_doituong', False):
            if context['loai_doituong']=='taixe':
#                 partner_ids = self.search(cr, uid, [('taixe','=',True),('account_ht_id.parent_id','=',chinhanh_id)])
                sql = '''
                    select id from res_partner where taixe='t' and account_ht_id in (select id from account_account where parent_id=%s)
                '''%(chinhanh_id)
                cr.execute(sql)
                partner_ids = [r[0] for r in cr.fetchall()]
                args += [('id','in',partner_ids)]
            if context['loai_doituong']=='nhadautu':
                sql = '''
                    select partner_id from chi_nhanh_line where chinhanh_id=%s
                '''%(chinhanh_id)
                cr.execute(sql)
                partner_ids = [r[0] for r in cr.fetchall()]
                args += [('nhadautu','=',True),('id','in',partner_ids)]
            if context['loai_doituong']=='nhanvienvanphong':
#                 partner_ids = self.search(cr, uid, [('nhanvienvanphong','=',True),('account_ht_id.parent_id','=',chinhanh_id)])
                sql = '''
                    select id from res_partner where nhanvienvanphong='t' and account_ht_id in (select id from account_account where parent_id=%s)
                '''%(chinhanh_id)
                cr.execute(sql)
                partner_ids = [r[0] for r in cr.fetchall()]
                args += [('id','in',partner_ids)]
                
        if context.get('partner_for_phaitrakyquy', False) and context.get('loai_doituong', False):
            if context['loai_doituong']=='taixe':
#                 partner_ids = self.search(cr, uid, [('taixe','=',True),('account_ht_id.parent_id','=',chinhanh_id)])
                sql = '''
                    select id from res_partner where taixe='t' and account_ht_id in (select id from account_account where parent_id=%s) and sotien_dathu>0
                '''%(chinhanh_id)
                cr.execute(sql)
                partner_ids = [r[0] for r in cr.fetchall()]
                args += [('id','in',partner_ids)]
            if context['loai_doituong']=='nhadautu':
                sql = '''
                    select partner_id from chi_nhanh_line where chinhanh_id=%s and sotien_dathu>0
                '''%(chinhanh_id)
                cr.execute(sql)
                partner_ids = [r[0] for r in cr.fetchall()]
                args += [('nhadautu','=',True),('id','in',partner_ids)]
            if context['loai_doituong']=='nhanvienvanphong':
#                 partner_ids = self.search(cr, uid, [('nhanvienvanphong','=',True),('account_ht_id.parent_id','=',chinhanh_id)])
                sql = '''
                    select id from res_partner where nhanvienvanphong='t'
                        and account_ht_id in (select id from account_account where parent_id=%s) and sotien_dathu>0
                '''%(chinhanh_id)
                cr.execute(sql)
                partner_ids = [r[0] for r in cr.fetchall()]
                args += [('id','in',partner_ids)]
        
        if context.get('doituong_thukyquy', False) and context.get('chinhanh_id', False) and context.get('loai_doituong',False):
            if context['loai_doituong']=='nhadautu':
                sql = '''
                    select id from res_partner where id in (select partner_id from chi_nhanh_line where chinhanh_id=%s and sotien_conlai>0) and nhadautu='t'
                '''%(context['chinhanh_id'])
                cr.execute(sql)
                partner_ids = [r[0] for r in cr.fetchall()]
            if context['loai_doituong']=='taixe':
#                 partner_ids = self.search(cr, uid, [('taixe','=',True),('account_ht_id.parent_id','=',context['chinhanh_id']),('sotien_conlai','>',0)])
                sql = '''
                    select id from res_partner where taixe='t' and account_ht_id in (select id from account_account where parent_id=%s) and sotien_conlai>0
                '''%(context['chinhanh_id'])
                cr.execute(sql)
                partner_ids = [r[0] for r in cr.fetchall()]
            if context['loai_doituong']=='nhanvienvanphong':
#                 partner_ids = self.search(cr, uid, [('nhanvienvanphong','=',True),('account_ht_id.parent_id','=',context['chinhanh_id']),('sotien_conlai','>',0)])
                sql = '''
                    select id from res_partner where nhanvienvanphong='t' and account_ht_id in (select id from account_account where parent_id=%s) and sotien_conlai>0
                '''%(context['chinhanh_id'])
                cr.execute(sql)
                partner_ids = [r[0] for r in cr.fetchall()]
            args += [('id','in',partner_ids)]
        
        if context.get('timnhadautugiantiep', False):
            sql = '''
                select partner_id from chi_nhanh_line where chinhanh_id=%s
            '''%(chinhanh_id)
            cr.execute(sql)
            partner_ids = [r[0] for r in cr.fetchall()]
            args += [('nhadautugiantiep','=',True),('id','in',partner_ids)]
        
        if context.get('baocao_partner_with_loaidoituong', False) and context.get('loai_doituong', False) and context['loai_doituong']:
            if context['loai_doituong']=='taixe':
#                 partner_ids = self.search(cr, uid, [('taixe','=',True),('account_ht_id.parent_id','=',chinhanh_id)])
                sql = '''
                    select id from res_partner where taixe='t' and account_ht_id in (select id from account_account where parent_id=%s)
                '''%(chinhanh_id)
                cr.execute(sql)
                partner_ids = [r[0] for r in cr.fetchall()]
                args += [('id','in',partner_ids)]
            if context['loai_doituong']=='nhadautu':
                sql = '''
                    select partner_id from chi_nhanh_line where chinhanh_id=%s
                '''%(chinhanh_id)
                cr.execute(sql)
                partner_ids = [r[0] for r in cr.fetchall()]
                args += [('nhadautu','=',True),('id','in',partner_ids)]
            if context['loai_doituong']=='nhanvienvanphong':
#                 partner_ids = self.search(cr, uid, [('nhanvienvanphong','=',True),('account_ht_id.parent_id','=',chinhanh_id)])
                sql = '''
                    select id from res_partner where nhanvienvanphong='t' and account_ht_id in (select id from account_account where parent_id=%s)
                '''%(chinhanh_id)
                cr.execute(sql)
                partner_ids = [r[0] for r in cr.fetchall()]
                args += [('id','in',partner_ids)]
        
        return super(res_partner, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('ma_doi_tuong', False):
            vals['ma_doi_tuong'] = vals['ma_doi_tuong'].strip()
        return super(res_partner, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('chinhanh_id'):
            for partner in self.browse(cr, uid, ids):
               if (partner.taixe or partner.nhanvienvanphong) and partner.chinhanh_id.id!=vals['chinhanh_id']:
                   sql = '''
                       select case when sum(sotien_conlai)!=0 then sum(sotien_conlai) else 0 end sotienconlai
                           from thu_ky_quy where chinhanh_id=%s and partner_id=%s
                   '''%(partner.chinhanh_id.id,partner.id)
                   cr.execute(sql)
                   sotien_kyquy_conlai = cr.fetchone()[0]
                   if sotien_kyquy_conlai:
                       raise osv.except_osv(_('Cảnh báo!'),_('Không được phép đổi chi nhánh khi số tiền đã thu ký quỹ của chi nhánh củ chưa cấn trừ hết!'))
                   
                   sql = '''
                       select case when sum(COALESCE(residual,0) + COALESCE(sotien_lai_conlai,0))!=0 then sum(COALESCE(residual,0) + COALESCE(sotien_lai_conlai,0)) else 0 end sotienconlai
                           from account_invoice where chinhanh_id=%s and partner_id=%s
                   '''%(partner.chinhanh_id.id,partner.id)
                   cr.execute(sql)
                   sotien_congno_conlai = cr.fetchone()[0]
                   if sotien_congno_conlai:
                       raise osv.except_osv(_('Cảnh báo!'),_('Không được phép đổi chi nhánh khi công nợ phải thu của chi nhánh củ chưa cấn trừ hết!'))
        if vals.get('ma_doi_tuong', False):
            vals['ma_doi_tuong'] = vals['ma_doi_tuong'].strip()
        return super(res_partner, self).write(cr, uid, ids, vals, context)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        if not name:
            ids = self.search(cr, user, args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, [('ma_doi_tuong',operator,name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
            
        return self.name_get(cr, user, ids, context=context)
    
    def onchange_property_account_receivable(self, cr, uid, ids, property_account_receivable=False, context=None):
        return {'value': {'property_account_payable':property_account_receivable,'account_ht_id':property_account_receivable}}
    
    def onchange_chinhanh(self, cr, uid, ids, chinhanh_id=False, context=None):
        return {'value': {'bai_giaoca_id': False,'property_account_receivable':False,'property_account_payable':False,'account_ht_id':False}}
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = '['+(record.ma_doi_tuong or '')+']'+' '+(record.name or '')
            res.append((record.id, name))
        return res
    
#     def create(self, cr, uid, vals, context=None):
#         if context is None:
#             context = {}
#         user = self.pool.get('res.users').browse(cr, uid, uid)
#         vals.update({'chinhanh_id':user.chinhanh_id and user.chinhanh_id.id or False})
#         return super(res_partner, self).create(cr, uid, vals, context)
    
#     def write(self, cr, uid, ids, vals, context=None):
#         for line in self.browse(cr, uid, ids):
#             user = line.create_user_id
#             vals.update({'chinhanh_id':user.chinhanh_id and user.chinhanh_id.id or False})
#         return super(res_partner, self).write(cr, uid, ids, vals, context)
    
    def cantru_kyquy(self, cr, uid, ids, context=None):
        kyquy_obj = self.pool.get('thu.ky.quy')
        voucher_obj = self.pool.get('account.voucher')
        ngay_thanh_toan=time.strftime('%Y-%m-%d')
        for partner in self.browse(cr, uid, ids):
            if partner.taixe or partner.nhanvienvanphong:
                sotien_conlai = partner.sotien_dathu
                sotien_cantru = 0
                sql = '''
                    select id,partner_id,case when residual!=0 then residual else 0 end residual,name,bai_giaoca_id,
                        mlg_type,type,chinhanh_id,currency_id,company_id,
                        case when sotien_lai_conlai!=0 then sotien_lai_conlai else 0 end sotien_lai_conlai
                    
                        from account_invoice
                    
                        where state='open' and type='out_invoice' and chinhanh_id=%s and partner_id=%s
                        
                        order by date_invoice,id
                '''%(partner.chinhanh_id.id,partner.id)
                cr.execute(sql)
                for line in cr.dictfetchall():
                    if sotien_conlai>(line['residual']+line['sotien_lai_conlai']):
                        amount = line['residual']+line['sotien_lai_conlai']
                        sotien_tragopxe = line['residual']+line['sotien_lai_conlai']
                        sotien_conlai = sotien_conlai-(line['residual']+line['sotien_lai_conlai'])
                    else:
                        amount = sotien_conlai
                        sotien_tragopxe = sotien_conlai
                        sotien_conlai = 0
                    sotien_cantru=sotien_tragopxe
                    if not amount:
                        break
                    
                    journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','cash'),('chinhanh_id','=',line['chinhanh_id'])])
                        
                    sotientra = amount
                    sotienlai = line['sotien_lai_conlai']
                    if sotientra>=sotienlai:
                        sotientra = sotientra-sotienlai
                    else:
                        sotientra = 0
                    amount = sotientra
                        
                    vals = {
                        'amount': amount,
                        'sotien_tragopxe': sotien_tragopxe,
                        'sotien_lai_conlai': line['sotien_lai_conlai'],
                        'partner_id': line['partner_id'],
                        'reference': line['name'],
                        'bai_giaoca_id': line['bai_giaoca_id'],
                        'mlg_type': line['mlg_type'],
                        'type': 'receipt',
                        'chinhanh_id': line['chinhanh_id'],
                        'journal_id': journal_ids[0],
                        'date': ngay_thanh_toan,
                        'loai_giaodich': 'Giao dịch cấn trừ ký quỹ',
                    }
                    
                    context = {
                        'payment_expected_currency': line['currency_id'],
                        'default_partner_id': line['partner_id'],
                        'default_amount': amount,
                        'default_reference': line['name'],
                        'default_bai_giaoca_id': line['bai_giaoca_id'],
                        'default_mlg_type': line['mlg_type'],
                        'close_after_process': True,
                        'invoice_type': line['type'],
                        'invoice_id': line['id'],
                        'default_type': 'receipt',
                        'default_chinhanh_id': line['chinhanh_id'],
                        'type': 'receipt',
                        'loai_giaodich': 'Giao dịch cấn trừ ký quỹ',
                    }
                    vals_onchange_partner = voucher_obj.onchange_partner_id(cr, uid, [],line['partner_id'],journal_ids[0],amount,line['currency_id'],'receipt',ngay_thanh_toan,context)['value']
                    vals.update(vals_onchange_partner)
                    vals.update(
                        voucher_obj.onchange_journal(cr, uid, [],journal_ids[0],vals_onchange_partner['line_cr_ids'],False,line['partner_id'],ngay_thanh_toan,amount,'receipt',line['company_id'],context)['value']
                    )
                    line_cr_ids = []
                    for l in vals['line_cr_ids']:
                        line_cr_ids.append((0,0,l))
                    vals.update({'line_cr_ids':line_cr_ids})
                    voucher_id = voucher_obj.create(cr, uid, vals,context)
                    voucher_obj.button_proforma_voucher(cr, uid, [voucher_id],context)
                    
                    sql = '''
                        select id, sotien_conlai
                            from thu_ky_quy
                            
                            where sotien_conlai>0 and chinhanh_id=%s and partner_id=%s and state='paid'
                            
                            order by ngay_thu,id
                    '''%(partner.chinhanh_id.id,partner.id)
                    cr.execute(sql)
                    for kyquy in cr.dictfetchall():
                        if not sotien_cantru:
                            break
                        if sotien_cantru<kyquy['sotien_conlai']:
                            kyquy_obj.write(cr, uid, [kyquy['id']],{'sotien_conlai':kyquy['sotien_conlai']-sotien_cantru,
                                                                    'cantru_kyquy_chocongno_ids': [(4,line['id'])]})
                            sotien_cantru = 0
                        else:
                            kyquy_obj.write(cr, uid, [kyquy['id']],{'sotien_conlai':0,
                                                                    'cantru_kyquy_chocongno_ids': [(4,line['id'])]})
                            sotien_cantru = sotien_cantru-kyquy['sotien_conlai']
                    
            if partner.nhadautu:
                for chinhanh in partner.chinhanh_line:
                
                    sotien_conlai = chinhanh.sotien_dathu
                    sotien_cantru = 0
                    sql = '''
                        select id,partner_id,case when residual!=0 then residual else 0 end residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id,
                            case when sotien_lai_conlai!=0 then sotien_lai_conlai else 0 end sotien_lai_conlai
                        
                            from account_invoice
                        
                            where state='open' and type='out_invoice' and chinhanh_id=%s and partner_id=%s
                            
                            order by date_invoice,id
                    '''%(chinhanh.chinhanh_id.id,partner.id)
                    cr.execute(sql)
                    for line in cr.dictfetchall():
                        if sotien_conlai>(line['residual']+line['sotien_lai_conlai']):
                            amount = line['residual']+line['sotien_lai_conlai']
                            sotien_tragopxe = line['residual']+line['sotien_lai_conlai']
                            sotien_conlai = sotien_conlai-(line['residual']+line['sotien_lai_conlai'])
                        else:
                            amount = sotien_conlai
                            sotien_tragopxe = sotien_conlai
                            sotien_conlai = 0
                        sotien_cantru=sotien_tragopxe
                        if not amount:
                            break
                        
                        journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','cash'),('chinhanh_id','=',line['chinhanh_id'])])
                        
                        sotientra = amount
                        sotienlai = line['sotien_lai_conlai']
                        if sotientra>=sotienlai:
                            sotientra = sotientra-sotienlai
                        else:
                            sotientra = 0
                        amount = sotientra
                        
                        vals = {
                            'amount': amount,
                            'sotien_tragopxe': sotien_tragopxe,
                            'sotien_lai_conlai': line['sotien_lai_conlai'],
                            'partner_id': line['partner_id'],
                            'reference': line['name'],
                            'bai_giaoca_id': line['bai_giaoca_id'],
                            'mlg_type': line['mlg_type'],
                            'type': 'receipt',
                            'chinhanh_id': line['chinhanh_id'],
                            'journal_id': journal_ids[0],
                            'date': ngay_thanh_toan,
                            'loai_giaodich': 'Giao dịch cấn trừ ký quỹ',
                        }
                        
                        context = {
                            'payment_expected_currency': line['currency_id'],
                            'default_partner_id': line['partner_id'],
                            'default_amount': amount,
                            'default_reference': line['name'],
                            'default_bai_giaoca_id': line['bai_giaoca_id'],
                            'default_mlg_type': line['mlg_type'],
                            'close_after_process': True,
                            'invoice_type': line['type'],
                            'invoice_id': line['id'],
                            'default_type': 'receipt',
                            'default_chinhanh_id': line['chinhanh_id'],
                            'type': 'receipt',
                            'loai_giaodich': 'Giao dịch cấn trừ ký quỹ',
                        }
                        vals_onchange_partner = voucher_obj.onchange_partner_id(cr, uid, [],line['partner_id'],journal_ids[0],amount,line['currency_id'],'receipt',ngay_thanh_toan,context)['value']
                        vals.update(vals_onchange_partner)
                        vals.update(
                            voucher_obj.onchange_journal(cr, uid, [],journal_ids[0],vals_onchange_partner['line_cr_ids'],False,line['partner_id'],ngay_thanh_toan,amount,'receipt',line['company_id'],context)['value']
                        )
                        line_cr_ids = []
                        for l in vals['line_cr_ids']:
                            line_cr_ids.append((0,0,l))
                        vals.update({'line_cr_ids':line_cr_ids})
                        voucher_id = voucher_obj.create(cr, uid, vals,context)
                        voucher_obj.button_proforma_voucher(cr, uid, [voucher_id],context)
                    
                        sql = '''
                            select id, sotien_conlai
                                from thu_ky_quy
                                
                                where sotien_conlai>0 and chinhanh_id=%s and partner_id=%s and state='paid'
                                
                                order by ngay_thu,id
                        '''%(chinhanh.chinhanh_id.id,partner.id)
                        cr.execute(sql)
                        for kyquy in cr.dictfetchall():
                            if not sotien_cantru:
                                break
                            if sotien_cantru<kyquy['sotien_conlai']:
                                kyquy_obj.write(cr, uid, [kyquy['id']],{'sotien_conlai':kyquy['sotien_conlai']-sotien_cantru,
                                                                        'cantru_kyquy_chocongno_ids': [(4,line['id'])]})
                                sotien_cantru = 0
                            else:
                                kyquy_obj.write(cr, uid, [kyquy['id']],{'sotien_conlai':0,
                                                                        'cantru_kyquy_chocongno_ids': [(4,line['id'])]})
                                sotien_cantru = sotien_cantru-kyquy['sotien_conlai']
        return True
    
res_partner()

class chi_nhanh_line(osv.osv):
    _name = "chi.nhanh.line"
    
    def _get_sotien(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for chinhanhline in self.browse(cr, uid, ids, context=context):
            res[chinhanhline.id] = {
                'sotien_dathu': 0,
                'sotien_conlai': 0,
            }
            sql = '''
                select case when sum(sotien_conlai)!=0 then sum(sotien_conlai) else 0 end sotien from thu_ky_quy where partner_id=%s and chinhanh_id=%s and state='paid'
            '''%(chinhanhline.partner_id.id,chinhanhline.chinhanh_id.id)
            cr.execute(sql)
            res[chinhanhline.id]['sotien_dathu'] = cr.fetchone()[0]
            res[chinhanhline.id]['sotien_conlai'] = chinhanhline.sotien_phaithu - res[chinhanhline.id]['sotien_dathu']
        return res
    
    def _get_chi_nhanh_line(self, cr, uid, ids, context=None):
        result = {}
        chi_nhanh_line_obj = self.pool.get('chi.nhanh.line')
        for line in self.pool.get('thu.ky.quy').browse(cr, uid, ids, context=context):
            chi_nhanh_line_ids = chi_nhanh_line_obj.search(cr, uid, [('chinhanh_id','=',line.chinhanh_id.id),('partner_id','=',line.partner_id.id)])
            for chi_nhanh_line_id in chi_nhanh_line_ids:
                result[chi_nhanh_line_id] = True
        return result.keys()
    
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', required=True, ondelete='cascade'),
        'chinhanh_id': fields.many2one('account.account', 'Chi nhánh', required=True),
        'nhom_chinhanh_id': fields.many2one('account.account', 'Chi nhánh đầu tư', required=False),
        
        'sotien_phaithu': fields.float('Số tiền phải thu',digits=(16,0)),
        'sotien_phaithu_dinhky': fields.float('Số tiền phải thu định kỳ',digits=(16,0)),
        'sotien_dathu': fields.function(_get_sotien, string='Số tiền đã thu', multi='sotien',
            store={
                'chi.nhanh.line': (lambda self, cr, uid, ids, c={}: ids, ['sotien_phaithu','sotien_phaithu_dinhky'], 10),
                'thu.ky.quy': (_get_chi_nhanh_line, ['state', 'so_tien', 'partner_id','chinhanh_id','sotien_conlai'], 10),
            },type='float',digits=(16,0)),
        'sotien_conlai': fields.function(_get_sotien, string='Số tiền còn lại', multi='sotien',
            store={
                'chi.nhanh.line': (lambda self, cr, uid, ids, c={}: ids, ['sotien_phaithu','sotien_phaithu_dinhky'], 10),
                'thu.ky.quy': (_get_chi_nhanh_line, ['state', 'so_tien', 'partner_id','chinhanh_id','sotien_conlai'], 10),
            },type='float',digits=(16,0)),
    }
    
    def _check_chinhanh_id(self, cr, uid, ids, context=None):
        for cnl in self.browse(cr, uid, ids, context=context):
            if cnl.partner_id and cnl.partner_id.nhadautu:
                sql = '''
                    select id from chi_nhanh_line where id != %s and nhom_chinhanh_id=%s and partner_id=%s
                '''%(cnl.id,cnl.nhom_chinhanh_id.id,cnl.partner_id.id)
                cr.execute(sql)
                cnl_ids = [row[0] for row in cr.fetchall()]
                if cnl_ids:  
                    raise osv.except_osv(_('Cảnh báo!'),_('Không được phép chọn hai chi nhánh đầu tư giống nhau cho cùng một nhà đầu tư!'))
                    return False
        return True
    _constraints = [
        (_check_chinhanh_id, 'Identical Data', ['chinhanh_id']),
    ]
    
chi_nhanh_line()

class tong_cong_no(osv.osv):
    _name = "tong.cong.no"
    _columns = {
        'partner_id': fields.many2one('res.partner','Partner', ondelete='cascade'),
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
                                      ('chi_ho','Chi hộ'),],'Loại công nợ', readonly=True),
        'sotien_congno': fields.float('Số tiền công nợ',digits=(16,0)),
        'sotien_dathu': fields.float('Số tiền đã thu',digits=(16,0)),
        'sotien_conlai': fields.float('Số tiền còn lại',digits=(16,0)),
    }
tong_cong_no()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
