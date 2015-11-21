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
                select id from account_account where code='200' limit 1
            '''
            cr.execute(sql)
            account_id = cr.fetchone()
            res.update({'property_account_receivable': account_id[0],'property_account_payable': account_id[0]})
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
                    select case when sum(so_tien)!=0 then sum(so_tien) else 0 end sotien from thu_ky_quy where partner_id=%s and state='paid'
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
            sql = '''
                select id from thu_ky_quy where partner_id=%s and state='paid'
            '''%(partner.id)
            cr.execute(sql)
            kyquy_ids = [r[0] for r in cr.fetchall()]
            res[partner.id] = kyquy_ids
        return res
    
    def _get_kyquy(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for partner in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from thu_ky_quy where partner_id=%s and state='paid'
            '''%(partner.id)
            cr.execute(sql)
            kyquy_ids = [r[0] for r in cr.fetchall()]
            res[partner.id] = kyquy_ids
        return res
    
    def _get_congno(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        congno_obj = self.pool.get('tong.cong.no')
        for partner in self.browse(cr, uid, ids, context=context):
            cr.execute('delete from tong_cong_no where partner_id=%s',(partner.id,))
            
            sql = '''
                select mlg_type,case when sum(amount_total)!=0 then sum(amount_total) else 0 end sotien_congno,
                        case when sum(residual)!=0 then sum(residual) else 0 end sotien_conlai
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
        'chinhanh_line': fields.one2many('chi.nhanh.line','partner_id','Chi nhánh'),
        'cmnd': fields.char('Số CMND', size=1024),
        'mst': fields.char('Mã số thuế', size=1024),
        'giayphep_kinhdoanh': fields.char('Mã số giấy phép kinh doanh', size=1024),
        'chinhanh_id': fields.many2one('account.account','Chi nhánh', readonly=True),
        'create_user_id': fields.many2one('res.users','User'),
        'sotien_phaithu': fields.float('Số tiền phải thu'),
        'sotien_phaithu_dinhky': fields.float('Số tiền phải thu định kỳ'),
        'sotien_dathu': fields.function(_get_sotien, string='Số tiền đã thu', multi='sotien',
            store={
                'res.partner': (lambda self, cr, uid, ids, c={}: ids, ['sotien_phaithu','sotien_phaithu_dinhky'], 10),
                'thu.ky.quy': (_get_partner, ['state', 'so_tien', 'partner_id'], 10),
            },type='float'),
        'sotien_conlai': fields.function(_get_sotien, string='Số tiền còn lại', multi='sotien',
            store={
                'res.partner': (lambda self, cr, uid, ids, c={}: ids, ['sotien_phaithu','sotien_phaithu_dinhky'], 10),
                'thu.ky.quy': (_get_partner, ['state', 'so_tien', 'partner_id'], 10),
            },type='float'),
        'ky_quy_ids': fields.function(_get_kyquy, relation='thu.ky.quy',type='many2many', string='Ký quỹ', readonly=True),
        'tinh_congno': fields.function(_get_congno, type='char', string='Tính công nợ', readonly=True),
        'congno_line': fields.one2many('tong.cong.no', 'partner_id','Chi tiết công nợ', readonly=True),
        'loai_doituong_lienket': fields.selection([('baohiem','Bảo hiểm'),('congty_thanhvien','Công ty thành viên')],'Loại đối tượng liên kết'),
        'doituong_lienket': fields.char('Mã đối tượng liên kết', size=1024),
    }
    
    def _get_chinhanh(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.chinhanh_id and user.chinhanh_id.id or False

    _defaults = {
        'chinhanh_id': _get_chinhanh,
        'create_user_id': lambda self,cr, uid, context: uid,
    }
    
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
            
        return super(res_partner, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
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
                select case when sum(so_tien)!=0 then sum(so_tien) else 0 end sotien from thu_ky_quy where partner_id=%s and chinhanh_id=%s and state='paid'
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
        'partner_id': fields.many2one('res.partner', 'Chi nhánh', required=True, ondelete='cascade'),
        'chinhanh_id': fields.many2one('account.account', 'Chi nhánh', required=True),
        'nhom_chinhanh_id': fields.many2one('account.account', 'Chi nhánh đầu tư', required=False),
        
        'sotien_phaithu': fields.float('Số tiền phải thu'),
        'sotien_phaithu_dinhky': fields.float('Số tiền phải thu định kỳ'),
        'sotien_dathu': fields.function(_get_sotien, string='Số tiền đã thu', multi='sotien',
            store={
                'chi.nhanh.line': (lambda self, cr, uid, ids, c={}: ids, ['sotien_phaithu','sotien_phaithu_dinhky'], 10),
                'thu.ky.quy': (_get_chi_nhanh_line, ['state', 'so_tien', 'partner_id','chinhanh_id'], 10),
            },type='float'),
        'sotien_conlai': fields.function(_get_sotien, string='Số tiền còn lại', multi='sotien',
            store={
                'chi.nhanh.line': (lambda self, cr, uid, ids, c={}: ids, ['sotien_phaithu','sotien_phaithu_dinhky'], 10),
                'thu.ky.quy': (_get_chi_nhanh_line, ['state', 'so_tien', 'partner_id','chinhanh_id'], 10),
            },type='float'),
    }
    
    def _check_chinhanh_id(self, cr, uid, ids, context=None):
        for cnl in self.browse(cr, uid, ids, context=context):
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
                                      ('chi_ho','Chi hộ'),],'Loại công nợ', readonly=True),
        'sotien_congno': fields.float('Số tiền công nợ'),
        'sotien_dathu': fields.float('Số tiền đã thu'),
        'sotien_conlai': fields.float('Số tiền còn lại'),
    }
tong_cong_no()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
