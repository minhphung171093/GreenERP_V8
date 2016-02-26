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
import time
from datetime import datetime
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv,fields
from openerp.tools.translate import _
import random
# from datetime import date
from dateutil.rrule import rrule, DAILY

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class tonghop_nhapxuat_ton(osv.osv_memory):
    _name = 'tonghop.nhapxuat.ton'
     
    _columns = {
        'name':fields.char('Xuất Báo Cáo', size = 1024,readonly = True)
                }
     
    _defaults = {
        'name':'Tổng hợp nhập - xuất - tồn kho vé số tự chọn',        
                }
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tonghop.nhapxuat.ton' 
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tonghop_nhapxuat_ton_report', 'datas': datas}
    
tonghop_nhapxuat_ton()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

