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
             'get_line': self.get_line,
             'get_nam': self.get_nam,
        })
    
    def get_nam(self):
        wizard_data = self.localcontext['data']['form']
        name = wizard_data['name']
        return name
    
    def get_line(self):
        wizard_data = self.localcontext['data']['form']
        name = wizard_data['name']
        loai_baocao = wizard_data['loai_baocao']
        sql = '''
            select case when sum(nhom_a)!=0 then sum(nhom_a) else 0 end nhom_a,
                    case when sum(nhom_b)!=0 then sum(nhom_b) else 0 end nhom_b,
                    case when sum(nhom_c)!=0 then sum(nhom_c) else 0 end nhom_c,
                    case when sum(tongso)!=0 then sum(tongso) else 0 end tongso,
                    stt,name,sequence,tieude
                from baocao_giamsat_line
                where stt=stt and name=name and sequence=sequence
                    and baocao_giamsat_id in (select id from baocao_giamsat where loai_baocao='%s' and name=%s and state='done')
                group by stt,name,sequence,tieude
                order by sequence
        '''%(loai_baocao,int(name))
        self.cr.execute(sql)
        vals = self.cr.dictfetchall()
        if vals:
            return vals
        else:
            return []
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
