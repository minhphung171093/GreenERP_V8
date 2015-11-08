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

class ql_bao_hiem(osv.osv):
    _name = "ql.bao.hiem"
    
    def _get_sotien(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for line in self.browse(cr, uid, ids):
            result[line.id] = {'sotien_datra':0,'sotien_conlai':0}
            sql = '''
                select amount_total, residual from account_invoice
                    where state in ('open','paid') and partner_id=%s and so_hoa_don='%s' and bien_so_xe_id=%s and mlg_type='phai_thu_bao_hiem'
                        and date_invoice between '%s' and '%s' order by date_invoice limit 1
            '''%(line.partner_id.id,line.so_hoa_don,line.name.id,line.ngay_tham_gia,line.ngay_ket_thuc)
            cr.execute(sql)
            invoice = cr.dictfetchone()
            if invoice:
                sotien = invoice['amount_total']
                sotien_conlai = invoice['residual']
                result[line.id] = {'sotien_datra':sotien-sotien_conlai,'sotien_conlai':sotien_conlai}
        return result
    
    _columns = {
        'name': fields.many2one('bien.so.xe','Biển số xe', required=True),
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
