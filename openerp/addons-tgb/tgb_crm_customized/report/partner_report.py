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
            'get_company_full_address': self.get_company_full_address,
            'get_contact_attn': self.get_contact_attn,
            'convert_date_d_B_Y': self.convert_date_d_B_Y,
            'get_upper': self.get_upper,
            'get_2directorin1line': self.get_2directorin1line,
        })
        
    def get_datenow(self):
        return time.strftime('%d/%m/%Y')
    
    def get_upper(self, a):
        if a:
            return a.upper()
        return ''
    
    def get_2directorin1line(self, partner_id):
        res = []
        sql = '''
            select name from res_partner where upper(function)='%s' and parent_id=%s
        '''%('DIRECTOR',partner_id)
        self.cr.execute(sql)
        for seq,contact in enumerate(self.cr.dictfetchall()):
            if seq%2==0:
                res.append({'director1':contact['name'],'director2':''})
            else:
                res[seq-1]['director2']=contact['name']
        return res
    
    def convert_date_d_B_Y(self,date):
        if date:
            return datetime.strptime(date,'%Y-%m-%d').strftime('%d-%B-%Y')
        return ''
    
    def get_company_full_address(self, company_id):
        address = ''
        if company_id and company_id.partner_id:
            partner = company_id.partner_id
            if partner.street:
                address += partner.street+' '
            if partner.street2:
                address += partner.street2+' '
            if partner.country_id:
                address += partner.country_id.name+' '
            if partner.zip:
                address += partner.zip+' '
        return address
    
    def get_contact_attn(self, company_id):
        attn = ''
        if company_id and company_id.partner_id and company_id.partner_id.child_ids:
            attn = company_id.partner_id.child_ids[0].name
        return attn
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
