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

class baocao_tonghop_tieuthu(osv.osv_memory):
    _name = 'baocao.tonghop.tieuthu'
     
    _columns = {
        'ky_ve_id': fields.many2one('ky.ve','Ký hiệu',required = True),
        'loai_ve': fields.selection([
            ('tt', 'Truyền thống'),
            ('tc', 'Tự chọn'),
            ], 'Loại vé'),
        'loai_ve_id': fields.many2one('loai.ve','Mệnh giá',required = True),
        'ngay_mo_thuong': fields.date('Ngày mở thưởng'),
        'name':fields.char('Thuộc', size = 1024,readonly = True)
                }
    _defaults = {
        'loai_ve': 'tt',
                 }
    def onchange_ky_ve_id(self, cr, uid, ids, ky_ve_id=False,ngay_mo_thuong=False):
        vals = {}
        if ky_ve_id :
            ky_ve = self.pool.get('ky.ve').browse(cr,uid,ky_ve_id)
            vals = {'ngay_mo_thuong':ky_ve.ngay_mo_thuong,
                }
            if ngay_mo_thuong:
                kv = ky_ve.name
                kv=kv[-1:]
                day = ngay_mo_thuong[8:10],
                month = ngay_mo_thuong[5:7],
                year = ngay_mo_thuong[:4],
                vals = {'name':u'Kỳ ' + str(kv) + u' tháng ' + ''.join(month) + u' năm '+ ''.join(year),}
        return {'value': vals}  
     

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'baocao.tieuthu.kyve' 
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'baocao_tonghop_tieuthu_report', 'datas': datas}
    
baocao_tonghop_tieuthu()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

