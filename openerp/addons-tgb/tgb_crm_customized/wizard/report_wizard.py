# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 OpenERP SA (<http://openerp.com>).
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

import base64
import re
import threading
from openerp.tools.safe_eval import safe_eval as eval
from openerp import tools
import openerp.modules
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
import datetime
import time
import calendar

class report_wizard(osv.osv):
    _name = 'report.wizard'
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard, self).default_get(cr, uid, fields, context=context)
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        line = self.browse(cr, uid, ids[0])
        datas = {'ids': [line.partner_id.id]}
        datas['model'] = 'res.partner'
        datas['form'] = self.pool.get('res.partner').read(cr, uid, [line.partner_id.id])[0]
        report_name = context.get('report_name')
        return {'type': 'ir.actions.report.xml', 'report_name': report_name , 'datas': datas}
    
report_wizard()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: