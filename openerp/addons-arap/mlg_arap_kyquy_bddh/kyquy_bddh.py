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

class cauhinh_kyquy_bddh(osv.osv):
    _name = "cauhinh.kyquy.bddh"
    
    _columns = {
        'name': fields.integer('Số tháng', required=True),
        'so_tien': fields.integer('Số tiền', digits=(16,0), required=True),
    }
    
    def tinh_kyquy_bddh(self, cr, uid, context=None):
        try:
            sql = '''
                select name,so_tien from cauhinh_kyquy_bddh limit 1
            '''
            cr.execute(sql)
            date_now = time.strftime('%Y-%m-%d')
            for line in cr.dictfetchall():
                sql = '''
                    select rp.id as partner_id
                        from res_partner rp
                        left join chi_nhanh_line cnl on cnl.partner_id=rp.id
                        left join lichsu_kyquy_bddh lskqbddh on lskqbddh.chinhanh_line_id=cnl.id
                        where 
                '''
        except Exception, e:
            cr.rollback()
        return True
    
cauhinh_kyquy_bddh()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
