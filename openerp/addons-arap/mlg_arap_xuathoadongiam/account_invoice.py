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
from openerp import netsvc
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    _columns = {
        'tat_toan': fields.boolean('Đã xuất hóa đơn'),
        'ngay_tat_toan': fields.date('Ngày xuất hóa đơn'),
    }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('mlg_type', False)=='tra_gop_xe' and vals.get('bien_so_xe_id') and vals.get('chinhanh_id'):
            sql = '''
                select id from account_invoice where mlg_type='tra_gop_xe' and tat_toan = True and chinhanh_id=%s and bien_so_xe_id=%s limit 1
            '''%(vals['chinhanh_id'],vals['bien_so_xe_id'])
            cr.execute(sql)
            invoice_ids = [r[0] for r in cr.fetchall()]
            if invoice_ids:
                raise osv.except_osv(_('Cảnh báo!'), _('Không thể tạo công nợ vì biển số xe được chọn đã xuất hóa đơn rồi!'))
        return super(account_invoice, self).create(cr, uid, vals, context)
    
account_invoice()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
