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
        'loai_doituong_id': fields.many2one('loai.doi.tuong', 'Loại đối tượng'),
        'ma_doi_tuong': fields.char('Mã đối tượng', size=1024),
        'bien_so_xe': fields.char('Biển số xe', size=1024),
        'loai_doituong': fields.related('loai_doituong_id', 'name', type='char', string='Loại đối tượng', readonly=True, store=True),
        'taixe': fields.boolean('Tài xế'),
        'nhadautu': fields.boolean('Nhà đầu tư'),
        'nhanvienvanphong': fields.boolean('Nhân viên văn phòng'),
        'chinhanh_line': fields.one2many('chi.nhanh.line','partner_id','Chi nhánh'),
        'cmnd': fields.char('Số CMND', size=1024),
        'mst': fields.char('Mã số thuế', size=1024),
        'giayphep_kinhdoanh': fields.char('Mã số giấy phép kinh doanh', size=1024),
        'chinhanh_id': fields.many2one('account.account','Chi nhánh', readonly=True),
    }
    
    def _get_chinhanh(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.chinhanh_id and user.chinhanh_id.id or False

    _defaults = {
        'chinhanh_id': _get_chinhanh,
    }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('cong_no_thu', False) and context.get('loai_doituong', False):
            if context['loai_doituong']=='taixe':
                partner_ids = self.search(cr, uid, [('taixe','=',True)])
                args += [('id','in',partner_ids)]
            if context['loai_doituong']=='nhadautu':
                partner_ids = self.search(cr, uid, [('nhadautu','=',True)])
                args += [('id','in',partner_ids)]
            if context['loai_doituong']=='nhanvienvanphong':
                partner_ids = self.search(cr, uid, [('nhanvienvanphong','=',True)])
                args += [('id','in',partner_ids)]
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
        return {'value': {'property_account_payable':property_account_receivable}}
    
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
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        vals.update({'chinhanh_id':user.chinhanh_id and user.chinhanh_id.id or False})
        return super(res_partner, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        vals.update({'chinhanh_id':user.chinhanh_id and user.chinhanh_id.id or False})
        return super(res_partner, self).write(cr, uid, ids, vals, context)
    
res_partner()

class chi_nhanh_line(osv.osv):
    _name = "chi.nhanh.line"
    
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Chi nhánh', required=True, ondelete='cascade'),
        'chinhanh_id': fields.many2one('account.account', 'Chi nhánh', required=True),
        'nhom_chinhanh_id': fields.many2one('account.account', 'Chi nhánh đầu tư', required=True),
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
