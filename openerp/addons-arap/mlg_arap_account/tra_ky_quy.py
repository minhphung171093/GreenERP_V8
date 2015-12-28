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

class tra_ky_quy(osv.osv):
    _name = "tra.ky.quy"
    _inherit = ['mail.thread']
    
    _columns = {
        'state': fields.selection([
            ('draft','Đang chờ'),
            ('paid','Đã trả'),
            ('cancel','Hủy bỏ'),
        ], string='Trạng thái', readonly=True),
        'chinhanh_id': fields.many2one('account.account','Chi nhánh', readonly=True),
        'partner_id': fields.many2one('res.partner','Đối tượng', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'ngay_tra': fields.date('Ngày trả', readonly=True, states={'draft': [('readonly', False)]}),
        'user_id': fields.many2one('res.users', 'Nhân viên chi', readonly=True, states={'draft': [('readonly', False)]}),
        'dien_giai': fields.text('Diễn giải', readonly=True, states={'draft': [('readonly', False)]}),
        'so_tien': fields.float('Số tiền',digits=(16,0), required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'name': fields.char('Số'),
        'currency_id': fields.many2one('res.currency','Đơn vị tiền tệ'),
        'loai_doituong': fields.selection([('taixe','Lái xe'),
                                           ('nhadautu','Nhà đầu tư'),
                                           ('nhanvienvanphong','Nhân viên văn phòng')], 'Loại đối tượng'),
#         'bien_so_xe': fields.char('Biển số xe', size=1024, readonly=True, states={'draft': [('readonly', False)]}),
        'bien_so_xe_id': fields.many2one('bien.so.xe','Biển số xe', readonly=True, states={'draft': [('readonly', False)]}),
        'loai_kyquy_id': fields.many2one('loai.ky.quy', 'Loại ký quỹ', readonly=True, states={'draft': [('readonly', False)]}),
        'thu_chi_kyquy_ids': fields.many2many('thu.ky.quy', 'thu_chi_kyquy_ref', 'chi_id', 'thu_id', 'Thu chi ký quỹ'),
    }
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('name', '/') == '/' or 'name' not in vals:
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'phai_tra_ky_quy', context=context) or '/'
            
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
            
        return super(tra_ky_quy, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('so_tien', False):
            for line in self.browse(cr, uid, ids):
                if line.so_tien<=0:
                    raise osv.except_osv(_('Cảnh báo!'), _('Không thể sửa với số tiền nhỏ hơn hoặc bằng "0"!'))
                
                if line.loai_doituong in ['taixe','nhanvienvanphong']:
                    sql = '''
                        select case when sotien_dathu!=0 then sotien_dathu else 0 end sotien_dathu from res_partner where id=%s
                    '''%(line.partner_id.id)
                    cr.execute(sql)
                    sotien_dathu = cr.fetchone()[0]
                    if sotien_dathu<vals['so_tien']:
                        raise osv.except_osv(_('Cảnh báo!'), _('Không được phép chỉnh sửa với số tiền nhập vào lớn hơn số tiền ký quỹ đã thu!'))
                
                if line.loai_doituong == 'nhadautu':
                    sql = '''
                    
                        select case when sotien_dathu!=0 then sotien_dathu else 0 end sotien_dathu
                            from chi_nhanh_line where chinhanh_id=%s and partner_id=%s
                    '''%(line.chinhanh_id.id,line.partner_id.id)
                    cr.execute(sql)
                    sotien_dathu = cr.fetchone()[0]
                    if sotien_dathu<vals['so_tien']:
                        raise osv.except_osv(_('Cảnh báo!'), _('Không được phép chỉnh sửa với số tiền nhập vào lớn hơn số tiền ký quỹ đã thu!'))
                    
        return super(tra_ky_quy, self).write(cr, uid, ids, vals, context)
    
    def _get_chinhanh(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.chinhanh_id and user.chinhanh_id.id or False
    
    def _get_currency(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.company_id and user.company_id.currency_id and user.company_id.currency_id.id or False
    
    _defaults = {
        'state': 'draft',
        'ngay_tra': time.strftime('%Y-%m-%d'),
        'chinhanh_id': _get_chinhanh,
        'user_id': lambda self, cr, uid, context: uid,
        'currency_id': _get_currency,
    }
    
    def bt_tra(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            kyquy_obj = self.pool.get('thu.ky.quy')
            sotien_cantru = line.so_tien
            sql = '''
                select id, sotien_conlai
                    from thu_ky_quy
                    
                    where sotien_conlai>0 and chinhanh_id=%s and partner_id=%s and state='paid'
                    
                    order by ngay_thu,id
            '''%(line.chinhanh_id.id,line.partner_id.id)
            cr.execute(sql)
            thu_chi_kyquy_ids = []
            for kyquy in cr.dictfetchall():
                if not sotien_cantru:
                    break
                if sotien_cantru<kyquy['sotien_conlai']:
                    kyquy_obj.write(cr, uid, [kyquy['id']],{'sotien_conlai':kyquy['sotien_conlai']-sotien_cantru})
                    sotien_cantru = 0
                else:
                    kyquy_obj.write(cr, uid, [kyquy['id']],{'sotien_conlai':0})
                    sotien_cantru = sotien_cantru-kyquy['sotien_conlai']
                thu_chi_kyquy_ids.append((4,kyquy['id']))
            if sotien_cantru>0:
                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền trả lớn hơn số tiền đã thu còn lại!')
        return self.write(cr, uid, ids, {'state': 'paid','thu_chi_kyquy_ids': thu_chi_kyquy_ids})
    
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
    
tra_ky_quy()
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
