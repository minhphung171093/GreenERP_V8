# -*- coding: utf-8 -*-
##############################################################################
#
#    HLVSolution, Open Source Management Solution
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
import random
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        
        self.localcontext.update({
             'get_vietname_date': self.get_vietname_date,
             'get_can_cu_phap_ly': self.get_can_cu_phap_ly,
             'get_nha_dau_tu': self.get_nha_dau_tu,
             'get_date_now': self.get_date_now,
        })
    
    def get_date_now(self):
        return time.strftime('%Y-%m-%d')
    
    def get_vietname_date(self, date):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_can_cu_phap_ly(self, gcndt_id):
        sql=''' select canculuat_id
                from hosodautu_canculuat_ref
                where hosodautu_id = %s'''%(gcndt_id)
        self.cr.execute(sql)
        phaply_ids = [row[0] for row in self.cr.fetchall()]
        phaplys = self.pool.get('can.cu.luat').browse(self.cr,self.uid,phaply_ids)
        return phaplys
    
    def get_nha_dau_tu(self, gcndt_id):
        res = []
        temp = 1
        sql=''' select partner_id
                from nha_dau_tu_rel
                where ho_so_id = %s'''%(gcndt_id)
        self.cr.execute(sql)
        nhadautu_ids = [row[0] for row in self.cr.fetchall()]
        res.append('')
        for nhadautu in self.pool.get('res.partner').browse(self.cr, self.uid, nhadautu_ids):
            if nhadautu.is_company == True:
                ndt = str(temp)+'. '+str(nhadautu.name or '')+'; Giấy phép thành lập số '+str(nhadautu.giay_thanh_lap_so or '')+'; cấp ngày '+str(nhadautu.ngay_cap_phep_thanh_lap or '')+'; nơi cấp '+str(nhadautu.noi_cap_phep_thanh_lap or '')+'; địa chỉ trụ sở chính '+str(nhadautu.street or '')+', '+str(nhadautu.state_id.name or '')+', '+str(nhadautu.country_id.name or '')
                res.append(ndt)
                temp += 1
                if nhadautu.child_ids:
                    for child in nhadautu.child_ids:
                        ndd = 'Đại diện bởi: '+str(child.name or '')+'; quốc tịch '+str(child.country_id.name or '')
                        res.append(ndd)
                res.append('')
            else:
                ndt = str(temp)+'. '+str(nhadautu.name or '')+'; quốc tịch '+str(nhadautu.country_id.name or '')
                res.append(ndt)
                temp += 1
                res.append('')
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
