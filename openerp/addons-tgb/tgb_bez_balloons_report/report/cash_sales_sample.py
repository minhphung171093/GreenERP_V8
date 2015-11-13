# -*- coding: utf-8 -*-
##############################################################################
#
#
##############################################################################

import time
from openerp.report import report_sxw
from openerp.osv import osv
from openerp.tools.translate import _
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_datenow': self.get_datenow,
            'convert_date': self.convert_date,
        })
        
    def get_datenow(self):
        return time.strftime('%Y-%m-%d')
    
    def convert_date(self,date):
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d-%b-%y (%a)')
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
