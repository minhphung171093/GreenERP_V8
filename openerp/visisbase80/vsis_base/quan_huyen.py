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

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from openerp import netsvc
import datetime
from openerp import SUPERUSER_ID
from mmap import mmap,ACCESS_READ
from xlrd import open_workbook
from xlwt import Workbook
from tempfile import TemporaryFile
from datetime import date,datetime,time
from xlrd import open_workbook,xldate_as_tuple
from time import strftime
from xlwt import easyxf
from xlutils.copy import copy

import os
from openerp import modules
base_path = os.path.dirname(modules.get_module_path('vsis_base'))

class res_country_state(osv.osv):
    _inherit = "res.country.state"
    _columns = {
        'quan_huyen_lines': fields.one2many('quan.huyen', 'state_id', 'Quận/huyện'),
    }
    def init(self, cr):
        country_obj = self.pool.get('res.country')
        wb = open_workbook(base_path + '/vsis_base/TinhTP.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    val0 = s.cell(row,0).value
                    val1 = s.cell(row,1).value
                    val2 = s.cell(row,2).value
                    country_ids = country_obj.search(cr, 1, [('code','=',val2)])
                    if country_ids:
                        state_ids = self.search(cr, 1, [('name','=',val1),('code','=',val0),('country_id','in',country_ids)])
                        if not state_ids:
                            self.create(cr, 1, {'name': val1,'code':val0,'country_id':country_ids[0]})
        
res_country_state()

class quan_huyen(osv.osv):
    _name = "quan.huyen"
    _columns = {
        'name': fields.char('Tên', size=64, required=True),
        'state_id': fields.many2one('res.country.state', 'Tỉnh/TP'),
    }
    
    def init(self, cr):
        state_obj = self.pool.get('res.country.state')
        wb = open_workbook(base_path + '/vsis_base/QuanHuyen.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    val0 = s.cell(row,0).value
                    val1 = s.cell(row,1).value
                    state_ids = state_obj.search(cr, 1, [('name','=',val1)])
                    if state_ids:
                        quan_huyen_ids = self.search(cr, 1, [('name','=',val0),('state_id','in',state_ids)])
                        if not quan_huyen_ids:
                            self.create(cr, 1, {'name': val0,'state_id':state_ids[0]})
             
quan_huyen()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
