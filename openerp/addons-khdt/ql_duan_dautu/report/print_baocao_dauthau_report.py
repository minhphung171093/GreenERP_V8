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
            select case when sum(tongso_goithau_a)!=0 then sum(tongso_goithau_a) else 0 end tongso_goithau_a,
                    case when sum(tongso_goithau_b)!=0 then sum(tongso_goithau_b) else 0 end tongso_goithau_b,
                    case when sum(tongso_goithau_c)!=0 then sum(tongso_goithau_c) else 0 end tongso_goithau_c,
                    case when sum(tongso_goithau)!=0 then sum(tongso_goithau) else 0 end tongso_goithau,
                    case when sum(tonggia_goithau_a)!=0 then sum(tonggia_goithau_a) else 0 end tonggia_goithau_a,
                    case when sum(tonggia_goithau_b)!=0 then sum(tonggia_goithau_b) else 0 end tonggia_goithau_b,
                    case when sum(tonggia_goithau_c)!=0 then sum(tonggia_goithau_c) else 0 end tonggia_goithau_c,
                    case when sum(tonggia_goithau)!=0 then sum(tonggia_goithau) else 0 end tonggia_goithau,
                    case when sum(tonggia_trungthau_a)!=0 then sum(tonggia_trungthau_a) else 0 end tonggia_trungthau_a,
                    case when sum(tonggia_trungthau_b)!=0 then sum(tonggia_trungthau_b) else 0 end tonggia_trungthau_b,
                    case when sum(tonggia_trungthau_c)!=0 then sum(tonggia_trungthau_c) else 0 end tonggia_trungthau_c,
                    case when sum(tonggia_trungthau)!=0 then sum(tonggia_trungthau) else 0 end tonggia_trungthau,
                    case when sum(chenhlech_a)!=0 then sum(chenhlech_a) else 0 end chenhlech_a,
                    case when sum(chenhlech_b)!=0 then sum(chenhlech_b) else 0 end chenhlech_b,
                    case when sum(chenhlech_c)!=0 then sum(chenhlech_c) else 0 end chenhlech_c,
                    case when sum(tong_chenhlech)!=0 then sum(tong_chenhlech) else 0 end tong_chenhlech,
                    name,sequence,tieude
                from baocao_dauthau_line
                where name=name and sequence=sequence
                    and baocao_dauthau_id in (select id from baocao_dauthau where loai_baocao='%s' and name=%s and state='done')
                group by name,sequence,tieude
                order by sequence
        '''%(loai_baocao,int(name))
        self.cr.execute(sql)
        vals = self.cr.dictfetchall()
        if vals:
            return vals
        else:
            return []
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
