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
        if not args:
            args = []
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

class account_chart(osv.osv_memory):
    _inherit = "account.chart"

    _defaults = {
        'target_move': 'all',
    }
account_chart()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
