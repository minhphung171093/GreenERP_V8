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

class doanhthu_veso(osv.osv_memory):
    _name = 'doanhthu.veso'
     
    _columns = {
        'ky_ve_id': fields.many2one('ky.ve','Ký hiệu'),
        'daily_id': fields.many2one('dai.ly','Đại lý'),
                }

    def bt_show_report(self, cr, uid, ids, context=None):
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_phathanh', 'doanhthu_graph_report_form')
        return {
                    'name': 'Doanh thu vé số Bình Phước',
                    'view_type': 'form',
                    'view_mode': 'graph',
                    'view_id': res[1],
                    'res_model': 'doanhthu.graph.report',
                    'domain': [],
                    'context': { 'search_default_ky_ve': 1,
                                },
                    'type': 'ir.actions.act_window',
#                     'target': 'new',
                }
    
doanhthu_veso()

class dthu_phanh_veso(osv.osv_memory):
    _name = 'dthu.phanh.veso'
     
    _columns = {
        'daily_id': fields.many2one('dai.ly','Đại lý'),
                }

    def bt_show_report(self, cr, uid, ids, context=None):
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_phathanh', 'dthu_phanh_graph_report_form')
        return {
                    'name': 'Doanh thu / Phát hành vé số Bình Phước',
                    'view_type': 'form',
                    'view_mode': 'graph',
                    'view_id': res[1],
                    'res_model': 'dthu.phanh.graph.report',
                    'domain': [],
                    'context': { 'search_default_ky_ve': 1,
                                },
                    'type': 'ir.actions.act_window',
#                     'target': 'new',
                }
    
dthu_phanh_veso()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

