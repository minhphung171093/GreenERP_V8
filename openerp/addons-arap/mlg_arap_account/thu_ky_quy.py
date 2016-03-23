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

class thu_ky_quy(osv.osv):
    _name = "thu.ky.quy"
    _inherit = ['mail.thread']
    _description = "Thu ký quỹ"
    
    _columns = {
        'state': fields.selection([
            ('draft','Đang chờ'),
            ('paid','Đã thu'),
            ('cancel','Hủy bỏ'),
        ], string='Trạng thái', readonly=True),
        'chinhanh_id': fields.many2one('account.account','Chi nhánh', readonly=False),
        'partner_id': fields.many2one('res.partner','Đối tượng', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'ngay_thu': fields.date('Ngày thu', readonly=True, states={'draft': [('readonly', False)]}),
        'user_id': fields.many2one('res.users', 'Nhân viên thu', readonly=True, states={'draft': [('readonly', False)]}),
        'dien_giai': fields.text('Diễn giải', readonly=True, states={'draft': [('readonly', False)]}),
        'so_tien': fields.float('Số tiền',digits=(16,0), required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'sotien_conlai': fields.float('Số tiền còn lại',digits=(16,0)),
        'name': fields.char('Số'),
        'currency_id': fields.many2one('res.currency','Đơn vị tiền tệ'),
        'loai_doituong': fields.selection([('taixe','Lái xe'),
                                           ('nhadautu','Nhà đầu tư'),
                                           ('nhanvienvanphong','Nhân viên văn phòng')], 'Loại đối tượng'),
#         'bien_so_xe': fields.char('Biển số xe', size=1024, readonly=True, states={'draft': [('readonly', False)]}),
        'bien_so_xe_id': fields.many2one('bien.so.xe','Biển số xe', readonly=True, states={'draft': [('readonly', False)]}),
        'loai_kyquy_id': fields.many2one('loai.ky.quy', 'Loại ký quỹ', readonly=True, states={'draft': [('readonly', False)]}),
        'thu_chi_kyquy_ids': fields.many2many('tra.ky.quy', 'thu_chi_kyquy_ref', 'thu_id', 'chi_id', 'Thu chi ký quỹ'),
        'cantru_kyquy_chocongno_ids': fields.many2many('account.invoice', 'cantru_kyquy_chocongno_ref', 'thukyquy_id', 'congno_id', 'Cấn trừ ký quỹ cho công nợ'),
        'fusion_id': fields.char('Fusion Chi', size=1024),
    }
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('name', '/') == '/' or 'name' not in vals:
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'thu_ky_quy', context=context) or '/'
#         user = self.pool.get('res.users').browse(cr, uid, uid)
#         vals.update({'chinhanh_id':user.chinhanh_id and user.chinhanh_id.id or False})
        if not vals.get('so_tien',False) or (vals.get('so_tien') and vals['so_tien']<=0):
            raise osv.except_osv(_('Cảnh báo!'), _('Không thể tạo với số tiền nhỏ hơn hoặc bằng "0"!'))
        if vals.get('so_tien',False):
            vals.update({'sotien_conlai': vals['so_tien']})
            
        if vals['loai_doituong'] in ['taixe','nhanvienvanphong']:
            sql = '''
                select case when sotien_conlai!=0 then sotien_conlai else 0 end sotien_conlai from res_partner where id=%s
            '''%(vals['partner_id'])
            cr.execute(sql)
            sotien_conlai = cr.fetchone()[0]
            if sotien_conlai<vals['so_tien']:
                raise osv.except_osv(_('Cảnh báo!'), _('Không được phép tạo với số tiền nhập vào lớn hơn số tiền ký quỹ phải thu còn lại!'))
        if vals['loai_doituong'] == 'nhadautu':
            sql = '''
            
                select case when sotien_conlai!=0 then sotien_conlai else 0 end sotien_conlai
                    from chi_nhanh_line where chinhanh_id=%s and partner_id=%s
            '''%(vals['chinhanh_id'],vals['partner_id'])
            cr.execute(sql)
            sotien_conlai = cr.fetchone()[0]
            if sotien_conlai<vals['so_tien']:
                raise osv.except_osv(_('Cảnh báo!'), _('Không được phép tạo với số tiền nhập vào lớn hơn số tiền ký quỹ phải thu còn lại!'))
            
        return super(thu_ky_quy, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('so_tien',False):
            vals.update({'sotien_conlai': vals['so_tien']})
            for line in self.browse(cr, uid, ids):
                
                if line.loai_doituong in ['taixe','nhanvienvanphong']:
                    sql = '''
                        select case when sotien_conlai!=0 then sotien_conlai else 0 end sotien_conlai from res_partner where id=%s
                    '''%(line.partner_id.id)
                    cr.execute(sql)
                    sotien_conlai = cr.fetchone()[0]
                    if sotien_conlai<vals['so_tien']:
                        raise osv.except_osv(_('Cảnh báo!'), _('Không được phép chỉnh sửa với số tiền nhập vào lớn hơn số tiền ký quỹ phải thu còn lại!'))
                
                if line.loai_doituong == 'nhadautu':
                    sql = '''
                    
                        select case when sotien_conlai!=0 then sotien_conlai else 0 end sotien_conlai
                            from chi_nhanh_line where chinhanh_id=%s and partner_id=%s
                    '''%(line.chinhanh_id.id,line.partner_id.id)
                    cr.execute(sql)
                    sotien_conlai = cr.fetchone()[0]
                    if sotien_conlai<vals['so_tien']:
                        raise osv.except_osv(_('Cảnh báo!'), _('Không được phép chỉnh sửa với số tiền nhập vào lớn hơn số tiền ký quỹ phải thu còn lại!'))
        
        new_write = super(thu_ky_quy, self).write(cr, uid, ids, vals, context)
        for line in self.browse(cr, uid, ids):
            if line.so_tien<=0:
                raise osv.except_osv(_('Cảnh báo!'), _('Không thể sửa với số tiền nhỏ hơn hoặc bằng "0"!'))
        return new_write
    
    def _get_chinhanh(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.chinhanh_id and user.chinhanh_id.id or False
    
    def _get_currency(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.company_id and user.company_id.currency_id and user.company_id.currency_id.id or False
    
    _defaults = {
        'state': 'draft',
        'ngay_thu': lambda *a: time.strftime('%Y-%m-%d'),
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
    
    def onchange_loaidoituong(self, cr, uid, ids, loai_doituong=False, context=None):
        vals = {'loai_kyquy_id': False}
        if loai_doituong in ['taixe','nhanvienvanphong']:
            sql = '''
                select id from loai_ky_quy where upper(code)='KY_QUY_CONG_VIEC'
            '''
            cr.execute(sql)
            loai_kq_ids = [r[0] for r in cr.fetchall()]
            vals.update({'loai_kyquy_id': loai_kq_ids and loai_kq_ids[0] or False})
            
        if loai_doituong in ['nhadautu']:
            sql = '''
                select id from loai_ky_quy where upper(code)='KY_QUY_DH_BD'
            '''
            cr.execute(sql)
            loai_kq_ids = [r[0] for r in cr.fetchall()]
            vals.update({'loai_kyquy_id': loai_kq_ids and loai_kq_ids[0] or False})
        return {'value': vals}
    
thu_ky_quy()
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
