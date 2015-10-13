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

class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'company_roc': fields.char('Company ROC',size=1024),
        'nric': fields.char('NRIC',size=1024),
        'signature_specimen': fields.char('Signature Specimen',size=1024),
        'hp': fields.char('HP',size=1024),
        'office_no': fields.char('Office No',size=1024),
        'street_personal': fields.char('Street'),
        'street2_personal': fields.char('Street2'),
        'zip_personal': fields.char('Zip', size=24, change_default=True),
        'city_personal': fields.char('City'),
        'state_personal_id': fields.many2one("res.country.state", 'State', ondelete='restrict'),
        'country_personal_id': fields.many2one('res.country', 'Country', ondelete='restrict'),
        'street_secretary': fields.char('Street'),
        'street2_secretary': fields.char('Street2'),
        'zip_secretary': fields.char('Zip', size=24, change_default=True),
        'city_secretary': fields.char('City'),
        'state_secretary_id': fields.many2one("res.country.state", 'State', ondelete='restrict'),
        'country_secretary_id': fields.many2one('res.country', 'Country', ondelete='restrict'),
        'period_of_year':fields.selection([('month','Month'),('quarter','Quarter'),('half_year','Half year'),('year','Year')],'Period or Year'),
        'document_collection_ids':fields.one2many('document.collection','partner_id','Document Collection'),
    }
    
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('period_of_year',False):
            if vals['period_of_year']=='month':
                document_collection_ids = []
                for seq,m in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December']):
                    year = int(time.strftime('%Y'))
                    month = seq+1
                    day = calendar.monthrange(year, month)[1]
                    alert_date = datetime.datetime(year,month,day)
                    document_collection_ids.append((0,0,{'name':m,'alert_date':alert_date.strftime('%Y-%m-%d')}))
                vals.update({'document_collection_ids':document_collection_ids})
            if vals['period_of_year']=='quarter':
                document_collection_ids = []
                for seq,m in enumerate(['First Quarter','Second Quarter', 'Third Quarter','Fourth Quarter']):
                    year = int(time.strftime('%Y'))
                    month = (seq+1)*3
                    day = calendar.monthrange(year, month)[1]
                    alert_date = datetime.datetime(year,month,day)
                    document_collection_ids.append((0,0,{'name':m,'alert_date':alert_date.strftime('%Y-%m-%d')}))
                vals.update({'document_collection_ids':document_collection_ids})
            if vals['period_of_year']=='half_year':
                document_collection_ids = []
                for seq,m in enumerate(['First Half','Second Half']):
                    year = int(time.strftime('%Y'))
                    month = (seq+1)*6
                    day = calendar.monthrange(year, month)[1]
                    alert_date = datetime.datetime(year,month,day)
                    document_collection_ids.append((0,0,{'name':m,'alert_date':alert_date.strftime('%Y-%m-%d')}))
                vals.update({'document_collection_ids':document_collection_ids})
            if vals['period_of_year']=='year':
                vals.update({'document_collection_ids':[(0,0,{'name':time.strftime('%Y'),'alert_date':time.strftime('%Y-12-31')})]})
        return super(res_partner, self).create(cr, uid, vals, context)
    
    
res_partner()

class document_collection(osv.osv):
    _name = "document.collection"
    _columns = {
        'name': fields.char('Name', size=1024, required=True),
        'partner_id':fields.many2one('res.partner','Partner',ondelete='cascade'),
        'alert_date': fields.date('Alert Date'),
        'document_sales_invoice':fields.boolean('Sales Invoice'),
        'document_receipt':fields.boolean('Receipt'),
        'document_payment_voucher':fields.boolean('Payment Voucher'),
        'document_bank_statement':fields.boolean('Bank Statement'),
        'document_rental_contract':fields.boolean('Rental Contract'),
        'document_petty_cash':fields.boolean('Petty Cash'),
        'tracking_sales_invoice':fields.boolean('Sales Invoice'),
        'tracking_receipt':fields.boolean('Receipt'),
        'tracking_payment_voucher':fields.boolean('Payment Voucher'),
        'tracking_bank_statement':fields.boolean('Bank Statement'),
        'tracking_rental_contract':fields.boolean('Rental Contract'),
        'tracking_petty_cash':fields.boolean('Petty Cash'),
    }
    _defaults = {
             }
document_collection()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: