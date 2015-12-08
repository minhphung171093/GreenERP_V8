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
from openerp.addons.mlg_arap_account.report import amount_to_text_vn
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'convert_date': self.convert_date,
            'convert_amount': self.convert_amount,
            'convert': self.convert,
            'get_line': self.get_line,
            'get_from_date': self.get_from_date,
            'get_to_date': self.get_to_date,
            'get_chinhanh': self.get_chinhanh,
        })
        
    def get_line(self):
        wizard_data = self.localcontext['data']['form']
        from_date = wizard_data['from_date']
        to_date = wizard_data['to_date']
        chinhanh_id = wizard_data['chinhanh_id']
        sql = '''
            select * from fin_output_theodoanhsophaitra_oracle('%s','%s',%s)
        '''%(from_date,to_date,chinhanh_id[0])
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_chinhanh(self):
        wizard_data = self.localcontext['data']['form']
        chinhanh_id = wizard_data['chinhanh_id']
        if not chinhanh_id:
            return {'name':'','code':''}
        account = self.pool.get('account.account').browse(self.cr, self.uid, chinhanh_id[0])
        return {'name':account.name,'code':account.code}
    
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def get_from_date(self):
        wizard_data = self.localcontext['data']['form']
        from_date = wizard_data['from_date']
        return self.convert_date(from_date)
    
    def get_to_date(self):
        wizard_data = self.localcontext['data']['form']
        to_date = wizard_data['to_date']
        return self.convert_date(to_date)
    
    def convert(self, amount):
        amount_text = amount_to_text_vn.amount_to_text(amount, 'vn')
        if amount_text and len(amount_text)>1:
            amount = amount_text[1:]
            head = amount_text[:1]
            amount_text = head.upper()+amount
        return amount_text
    
    def convert_amount(self, amount):
        a = format(int(amount),',')
        return a
    