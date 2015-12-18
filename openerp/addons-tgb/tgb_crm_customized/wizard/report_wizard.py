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
from openerp import netsvc,SUPERUSER_ID
import datetime
import time
import calendar

class report_wizard(osv.osv_memory):
    _name = 'report.wizard'
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard, self).default_get(cr, uid, fields, context=context)
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard()

class report_wizard_agm_dormant(osv.osv_memory):
    _name = 'report.wizard.agm.dormant'
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_agm_dormant, self).default_get(cr, uid, fields, context=context)
        partner_id = False
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
        if context.get('agm_dormant',False) and context['agm_dormant']:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
            
            report_filename='AR filing as dormant company YE Dec 2015_Flavors Apple'
            report_extention='.doc'
            report_name='ar_filing_as_dormant_company_ye_dec_2015_flavors_apple'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'ar_filing_as_dormant_company_ye_dec_2015_flavors_apple_fname': report_val['datas_fname'],
                        'ar_filing_as_dormant_company_ye_dec_2015_flavors_apple_datas': report_val['db_datas']})
            
            report_filename='Attendance List_AGM_YE Dec 2015_Flavors Apple'
            report_extention='.doc'
            report_name='attendance_list_agm_ye_dec_2015_flavors_apple'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'attendance_list_agm_ye_dec_2015_flavors_apple_fname': report_val['datas_fname'],
                        'attendance_list_agm_ye_dec_2015_flavors_apple_datas': report_val['db_datas']})
            
            report_filename='Confirmation for YE 31 December 2015_Flavors Apple'
            report_extention='.doc'
            report_name='confirmation_for_ye_31_december_2015_flavors_apple'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'confirmation_for_ye_31_december_2015_flavors_apple_fname': report_val['datas_fname'],
                        'confirmation_for_ye_31_december_2015_flavors_apple_datas': report_val['db_datas']})
            
            report_filename='Directors Resolution_AGM_YE Dec 2015_Flavors Apple'
            report_extention='.doc'
            report_name='directors_resolution_agm_ye_dec_2015_flavors_apple'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'directors_resolution_agm_ye_dec_2015_flavors_apple_fname': report_val['datas_fname'],
                        'directors_resolution_agm_ye_dec_2015_flavors_apple_datas': report_val['db_datas']})
            
            report_filename='Dormant company confirmation_YE 31122015_Flavors Apple'
            report_extention='.doc'
            report_name='dormant_company_confirmation_ye_31122015_flavors_apple'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'dormant_company_confirmation_ye_31122015_flavors_apple_fname': report_val['datas_fname'],
                        'dormant_company_confirmation_ye_31122015_flavors_apple_datas': report_val['db_datas']})
            
            report_filename='Engement Letter'
            report_extention='.doc'
            report_name='engement_letter'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'engement_letter_fname': report_val['datas_fname'],
                        'engement_letter_datas': report_val['db_datas']})
            
            report_filename='Minutes of Meeting_AGM_YE Dec 2015_Flavors Apple'
            report_extention='.doc'
            report_name='minutes_of_meeting_agm_ye_dec_2015_flavors_apple'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'minutes_of_meeting_agm_ye_dec_2015_flavors_apple_fname': report_val['datas_fname'],
                        'minutes_of_meeting_agm_ye_dec_2015_flavors_apple_datas': report_val['db_datas']})
            
            report_filename='Notice of Meeting_AGM_YE Dec 2015_Flavors Apple'
            report_extention='.doc'
            report_name='notice_of_meeting_agm_ye_dec_2015_flavors_apple'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'notice_of_meeting_agm_ye_dec_2015_flavors_apple_fname': report_val['datas_fname'],
                        'notice_of_meeting_agm_ye_dec_2015_flavors_apple_datas': report_val['db_datas']})
            
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        'ar_filing_as_dormant_company_ye_dec_2015_flavors_apple_fname': fields.char('File Name',size=256),
        'ar_filing_as_dormant_company_ye_dec_2015_flavors_apple_datas': fields.binary('Database Data'),
        
        'attendance_list_agm_ye_dec_2015_flavors_apple_fname': fields.char('File Name',size=256),
        'attendance_list_agm_ye_dec_2015_flavors_apple_datas': fields.binary('Database Data'),
        
        'confirmation_for_ye_31_december_2015_flavors_apple_fname': fields.char('File Name',size=256),
        'confirmation_for_ye_31_december_2015_flavors_apple_datas': fields.binary('Database Data'),
        
        'directors_resolution_agm_ye_dec_2015_flavors_apple_fname': fields.char('File Name',size=256),
        'directors_resolution_agm_ye_dec_2015_flavors_apple_datas': fields.binary('Database Data'),
        
        'dormant_company_confirmation_ye_31122015_flavors_apple_fname': fields.char('File Name',size=256),
        'dormant_company_confirmation_ye_31122015_flavors_apple_datas': fields.binary('Database Data'),
        
        'engement_letter_fname': fields.char('File Name',size=256),
        'engement_letter_datas': fields.binary('Database Data'),
        
        'minutes_of_meeting_agm_ye_dec_2015_flavors_apple_fname': fields.char('File Name',size=256),
        'minutes_of_meeting_agm_ye_dec_2015_flavors_apple_datas': fields.binary('Database Data'),
        
        'notice_of_meeting_agm_ye_dec_2015_flavors_apple_fname': fields.char('File Name',size=256),
        'notice_of_meeting_agm_ye_dec_2015_flavors_apple_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_agm_dormant()

class report_wizard_example(osv.osv_memory):
    _name = 'report.wizard.example'
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_example, self).default_get(cr, uid, fields, context=context)
        partner_id = False
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
        if context.get('example',False) and context['example']:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
            
            report_filename='ServiceGoWhere _AR filing as dormant company_Jun 2015'
            report_extention='.doc'
            report_name='servicegowhere_ar_filing_as_dormant_company_jun_2015'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'servicegowhere_ar_filing_as_dormant_company_jun_2015_fname': report_val['datas_fname'],
                        'servicegowhere_ar_filing_as_dormant_company_jun_2015_datas': report_val['db_datas']})
            
            report_filename='ServiceGoWhere _Attendance List_AGM_Jun 2015'
            report_extention='.doc'
            report_name='servicegowhere_attendance_list_agm_jun_2015'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'servicegowhere_attendance_list_agm_jun_2015_fname': report_val['datas_fname'],
                        'servicegowhere_attendance_list_agm_jun_2015_datas': report_val['db_datas']})
            
            report_filename='ServiceGoWhere _Confirmation for YE Jun 2015'
            report_extention='.doc'
            report_name='servicegowhere_confirmation_for_ye_jun_2015'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'servicegowhere_confirmation_for_ye_jun_2015_fname': report_val['datas_fname'],
                        'servicegowhere_confirmation_for_ye_jun_2015_datas': report_val['db_datas']})
            
            report_filename='ServiceGoWhere _Directors Resolution_AGM_YE Jun 2015'
            report_extention='.doc'
            report_name='servicegowhere_directors_resolution_agm_ye_jun_2015'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'servicegowhere_directors_resolution_agm_ye_jun_2015_fname': report_val['datas_fname'],
                        'servicegowhere_directors_resolution_agm_ye_jun_2015_datas': report_val['db_datas']})
            
            report_filename='ServiceGoWhere_Dormant company confirmation_Jun 2015'
            report_extention='.doc'
            report_name='servicegowhere_dormant_company_confirmation_jun_2015'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'servicegowhere_dormant_company_confirmation_jun_2015_fname': report_val['datas_fname'],
                        'servicegowhere_dormant_company_confirmation_jun_2015_datas': report_val['db_datas']})
            
            report_filename='ServiceGoWhere_Engement Letter Jun 2015'
            report_extention='.doc'
            report_name='servicegowhere_engement_letter_jun_2015'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'servicegowhere_engement_letter_jun_2015_fname': report_val['datas_fname'],
                        'servicegowhere_engement_letter_jun_2015_datas': report_val['db_datas']})
            
            report_filename='ServiceGoWhere_Minutes of Meeting_AGM_YE Jun 2015'
            report_extention='.doc'
            report_name='servicegowhere_minutes_of_meeting_agm_ye_jun_2015'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'servicegowhere_minutes_of_meeting_agm_ye_jun_2015_fname': report_val['datas_fname'],
                        'servicegowhere_minutes_of_meeting_agm_ye_jun_2015_datas': report_val['db_datas']})
            
            report_filename='ServiceGoWhere _Notice of Meeting_AGM_YE Jun 2015'
            report_extention='.doc'
            report_name='servicegowhere_notice_of_meeting_agm_ye_jun_2015'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'servicegowhere_notice_of_meeting_agm_ye_jun_2015_fname': report_val['datas_fname'],
                        'servicegowhere_notice_of_meeting_agm_ye_jun_2015_datas': report_val['db_datas']})
            
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),

        'servicegowhere_ar_filing_as_dormant_company_jun_2015_fname': fields.char('File Name',size=256),
        'servicegowhere_ar_filing_as_dormant_company_jun_2015_datas': fields.binary('Database Data'),
        
        'servicegowhere_attendance_list_agm_jun_2015_fname': fields.char('File Name',size=256),
        'servicegowhere_attendance_list_agm_jun_2015_datas': fields.binary('Database Data'),
        
        'servicegowhere_confirmation_for_ye_jun_2015_fname': fields.char('File Name',size=256),
        'servicegowhere_confirmation_for_ye_jun_2015_datas': fields.binary('Database Data'),
        
        'servicegowhere_directors_resolution_agm_ye_jun_2015_fname': fields.char('File Name',size=256),
        'servicegowhere_directors_resolution_agm_ye_jun_2015_datas': fields.binary('Database Data'),
        
        'servicegowhere_dormant_company_confirmation_jun_2015_fname': fields.char('File Name',size=256),
        'servicegowhere_dormant_company_confirmation_jun_2015_datas': fields.binary('Database Data'),
        
        'servicegowhere_engement_letter_jun_2015_fname': fields.char('File Name',size=256),
        'servicegowhere_engement_letter_jun_2015_datas': fields.binary('Database Data'),
        
        'servicegowhere_minutes_of_meeting_agm_ye_jun_2015_fname': fields.char('File Name',size=256),
        'servicegowhere_minutes_of_meeting_agm_ye_jun_2015_datas': fields.binary('Database Data'),
        
        'servicegowhere_notice_of_meeting_agm_ye_jun_2015_fname': fields.char('File Name',size=256),
        'servicegowhere_notice_of_meeting_agm_ye_jun_2015_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
    def back_to_agm_dormant(self, cr, uid, ids, context=None):
        line = self.browse(cr, uid, ids[0])
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'tgb_crm_customized', 'wizard_report_form_agm_dormant')
        return {
                    'name': 'AGM_Dormant',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'report.wizard.agm.dormant',
                    'domain': [],
                    'view_id': res[1],
                    'type': 'ir.actions.act_window',
                    'context':{'default_partner_id':line.partner_id.id,'example':0,'agm_dormant':1},
                    'target': 'new',
                }
     
report_wizard_example()

class report_wizard_agm_one(osv.osv_memory):
    _name = 'report.wizard.agm.one'
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_agm_one, self).default_get(cr, uid, fields, context=context)
        partner_id = False
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
        if context.get('agm_one',False) and context['agm_one']:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
            
            report_filename='Format_1st AGM-Attendance One Director'
            report_extention='.doc'
            report_name='format_1st_agm_attendance_one_director'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_1st_agm_attendance_one_director_fname': report_val['datas_fname'],
                        'format_1st_agm_attendance_one_director_datas': report_val['db_datas']})
            
            report_filename='Format_1st AGM-Minutes of Meeting_One Director'
            report_extention='.doc'
            report_name='format_1st_agm_minutes_of_meeting_one_director'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_1st_agm_minutes_of_meeting_one_director_fname': report_val['datas_fname'],
                        'format_1st_agm_minutes_of_meeting_one_director_datas': report_val['db_datas']})
            
            report_filename='Format_1st AGM-Notice of meeting_One Director'
            report_extention='.doc'
            report_name='format_1st_agm_notice_of_meeting_one_director'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_1st_agm_notice_of_meeting_one_director_fname': report_val['datas_fname'],
                        'format_1st_agm_notice_of_meeting_one_director_datas': report_val['db_datas']})
            
            report_filename='Format_1st AGM-Resolution_One Director'
            report_extention='.doc'
            report_name='format_1st_agm_resolution_one_director'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_1st_agm_resolution_one_director_fname': report_val['datas_fname'],
                        'format_1st_agm_resolution_one_director_datas': report_val['db_datas']})
            
            report_filename='Format_Appointment Letter_1st AGM_One Director'
            report_extention='.doc'
            report_name='format_appointment_letter_1st_agm_one_director'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_appointment_letter_1st_agm_one_director_fname': report_val['datas_fname'],
                        'format_appointment_letter_1st_agm_one_director_datas': report_val['db_datas']})
            
            report_filename='Format_AR Cert under S197_1st AGM_One Director'
            report_extention='.doc'
            report_name='format_ar_cert_under_s197_1st_agm_one_director'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_ar_cert_under_s197_1st_agm_one_director_fname': report_val['datas_fname'],
                        'format_ar_cert_under_s197_1st_agm_one_director_datas': report_val['db_datas']})
            
            report_filename='Format_Declaration of Directors_1st AGM_One Director'
            report_extention='.doc'
            report_name='format_declaration_of_directors_1st_agm_one_director'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_declaration_of_directors_1st_agm_one_director_fname': report_val['datas_fname'],
                        'format_declaration_of_directors_1st_agm_one_director_datas': report_val['db_datas']})
            
            report_filename='Format_Letter of Representation_1st AGM_One Director'
            report_extention='.doc'
            report_name='format_letter_of_representation_1st_agm_one_oirector'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_letter_of_representation_1st_agm_one_oirector_fname': report_val['datas_fname'],
                        'format_letter_of_representation_1st_agm_one_oirector_datas': report_val['db_datas']})
            
            report_filename='Format_Statement by Exempt Pte Co Exempt from Audit - S205C(3)_1st AGM_One Director'
            report_extention='.doc'
            report_name='format_statement_by_exempt_pte_co_exempt_from_audit_s205c_1st_agm_one_director'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_statement_1st_agm_one_director_fname': report_val['datas_fname'],
                        'format_statement_1st_agm_one_director_datas': report_val['db_datas']})
            
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        'format_1st_agm_attendance_one_director_fname': fields.char('File Name',size=256),
        'format_1st_agm_attendance_one_director_datas': fields.binary('Database Data'),
        
        'format_1st_agm_minutes_of_meeting_one_director_fname': fields.char('File Name',size=256),
        'format_1st_agm_minutes_of_meeting_one_director_datas': fields.binary('Database Data'),
        
        'format_1st_agm_notice_of_meeting_one_director_fname': fields.char('File Name',size=256),
        'format_1st_agm_notice_of_meeting_one_director_datas': fields.binary('Database Data'),
        
        'format_1st_agm_resolution_one_director_fname': fields.char('File Name',size=256),
        'format_1st_agm_resolution_one_director_datas': fields.binary('Database Data'),
        
        'format_appointment_letter_1st_agm_one_director_fname': fields.char('File Name',size=256),
        'format_appointment_letter_1st_agm_one_director_datas': fields.binary('Database Data'),
        
        'format_ar_cert_under_s197_1st_agm_one_director_fname': fields.char('File Name',size=256),
        'format_ar_cert_under_s197_1st_agm_one_director_datas': fields.binary('Database Data'),
        
        'format_letter_of_representation_1st_agm_one_oirector_fname': fields.char('File Name',size=256),
        'format_letter_of_representation_1st_agm_one_oirector_datas': fields.binary('Database Data'),
        
        'format_declaration_of_directors_1st_agm_one_director_fname': fields.char('File Name',size=256),
        'format_declaration_of_directors_1st_agm_one_director_datas': fields.binary('Database Data'),
        
        'format_statement_1st_agm_one_director_fname': fields.char('File Name',size=256),
        'format_statement_1st_agm_one_director_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_agm_one()

class report_wizard_agm_two(osv.osv_memory):
    _name = 'report.wizard.agm.two'
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_agm_two, self).default_get(cr, uid, fields, context=context)
        partner_id = False
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
        if context.get('agm_two',False) and context['agm_two']:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
            
            report_filename='Format_1st AGM-Attendance List'
            report_extention='.doc'
            report_name='format_1st_agm_attendance_list'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_1st_agm_attendance_list_fname': report_val['datas_fname'],
                        'format_1st_agm_attendance_list_datas': report_val['db_datas']})
            
            report_filename='Format_1st AGM-Minutes of Meeting'
            report_extention='.doc'
            report_name='format_1st_agm_minutes_of_meeting'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_1st_agm_minutes_of_meeting_fname': report_val['datas_fname'],
                        'format_1st_agm_minutes_of_meeting_datas': report_val['db_datas']})
            
            report_filename='Format_1st AGM-Notice of meeting'
            report_extention='.doc'
            report_name='format_1st_agm_notice_of_meeting'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_1st_agm_notice_of_meeting_fname': report_val['datas_fname'],
                        'format_1st_agm_notice_of_meeting_datas': report_val['db_datas']})
            
            report_filename='Format_1st AGM-Resolution'
            report_extention='.doc'
            report_name='format_1st_agm_resolution'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_1st_agm_resolution_fname': report_val['datas_fname'],
                        'format_1st_agm_resolution_datas': report_val['db_datas']})
            
            report_filename='Format_Appointment Letter_1st AGM'
            report_extention='.doc'
            report_name='format_appointment_letter_1st_agm'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_appointment_letter_1st_agm_fname': report_val['datas_fname'],
                        'format_appointment_letter_1st_agm_datas': report_val['db_datas']})
            
            report_filename='Format_AR Cert under S197_1st AGM'
            report_extention='.doc'
            report_name='format_ar_cert_under_s197_1st_agm'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_ar_cert_under_s197_1st_agm_fname': report_val['datas_fname'],
                        'format_ar_cert_under_s197_1st_agm_datas': report_val['db_datas']})
            
            report_filename='Format_Declaration of Directors_1st AGM'
            report_extention='.doc'
            report_name='format_declaration_of_directors_1st_agm'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_declaration_of_directors_1st_agm_fname': report_val['datas_fname'],
                        'format_declaration_of_directors_1st_agm_datas': report_val['db_datas']})
            
            report_filename='Format_Letter of Representation_1st AGM'
            report_extention='.doc'
            report_name='format_letter_of_representation_1st_agm'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_letter_of_representation_1st_agm_fname': report_val['datas_fname'],
                        'format_letter_of_representation_1st_agm_datas': report_val['db_datas']})
            
            report_filename='Format_Statement by Exempt Pte Co Exempt from Audit - S205C(3)_1st AGM'
            report_extention='.doc'
            report_name='format_statement_by_exempt_pte_co_exempt_from_audit_s205c_1st_agm'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_statement_by_exempt_pte_co_exempt_fname': report_val['datas_fname'],
                        'format_statement_by_exempt_pte_co_exempt_datas': report_val['db_datas']})
            
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        'format_1st_agm_attendance_list_fname': fields.char('File Name',size=256),
        'format_1st_agm_attendance_list_datas': fields.binary('Database Data'),
        
        'format_1st_agm_minutes_of_meeting_fname': fields.char('File Name',size=256),
        'format_1st_agm_minutes_of_meeting_datas': fields.binary('Database Data'),
        
        'format_1st_agm_notice_of_meeting_fname': fields.char('File Name',size=256),
        'format_1st_agm_notice_of_meeting_datas': fields.binary('Database Data'),
        
        'format_1st_agm_resolution_fname': fields.char('File Name',size=256),
        'format_1st_agm_resolution_datas': fields.binary('Database Data'),
        
        'format_appointment_letter_1st_agm_fname': fields.char('File Name',size=256),
        'format_appointment_letter_1st_agm_datas': fields.binary('Database Data'),
        
        'format_ar_cert_under_s197_1st_agm_fname': fields.char('File Name',size=256),
        'format_ar_cert_under_s197_1st_agm_datas': fields.binary('Database Data'),
        
        'format_declaration_of_directors_1st_agm_fname': fields.char('File Name',size=256),
        'format_declaration_of_directors_1st_agm_datas': fields.binary('Database Data'),
        
        'format_letter_of_representation_1st_agm_fname': fields.char('File Name',size=256),
        'format_letter_of_representation_1st_agm_datas': fields.binary('Database Data'),
        
        'format_statement_by_exempt_pte_co_exempt_fname': fields.char('File Name',size=256),
        'format_statement_by_exempt_pte_co_exempt_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_agm_two()

class report_wizard_subsequent_year_agm_two(osv.osv_memory):
    _name = 'report.wizard.subsequent.year.agm.two'
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_subsequent_year_agm_two, self).default_get(cr, uid, fields, context=context)
        partner_id = False
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
        if context.get('subsequent_year_agm_two',False) and context['subsequent_year_agm_two']:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
            
            report_filename='Format_Appointment Letter'
            report_extention='.doc'
            report_name='format_appointment_letter'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_appointment_letter_fname': report_val['datas_fname'],
                        'format_appointment_letter_datas': report_val['db_datas']})
            
            report_filename='Format_AR Cert under S197'
            report_extention='.doc'
            report_name='format_ar_cert_under_s197'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_ar_cert_under_s197_fname': report_val['datas_fname'],
                        'format_ar_cert_under_s197_datas': report_val['db_datas']})
            
            report_filename='Format_Declaration of Directors'
            report_extention='.doc'
            report_name='format_declaration_of_directors'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_declaration_of_directors_fname': report_val['datas_fname'],
                        'format_declaration_of_directors_datas': report_val['db_datas']})
            
            report_filename='Format_DR & AGM'
            report_extention='.doc'
            report_name='format_dr_and_agm'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_dr_and_agm_fname': report_val['datas_fname'],
                        'format_dr_and_agm_datas': report_val['db_datas']})
            
            report_filename='Format_Letter of Representation'
            report_extention='.doc'
            report_name='format_letter_of_representation'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_letter_of_representation_fname': report_val['datas_fname'],
                        'format_letter_of_representation_datas': report_val['db_datas']})
            
            report_filename='Format_Statement by Exempt Pte Co Exempt from Audit - S205C(3)'
            report_extention='.doc'
            report_name='format_statement_by_exempt_pte_co_exempt_from_audit_s205c3'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_statement_by_exempt_pte_co_exempt_fname': report_val['datas_fname'],
                        'format_statement_by_exempt_pte_co_exempt_datas': report_val['db_datas']})
            
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        'format_appointment_letter_fname': fields.char('File Name',size=256),
        'format_appointment_letter_datas': fields.binary('Database Data'),
        
        'format_ar_cert_under_s197_fname': fields.char('File Name',size=256),
        'format_ar_cert_under_s197_datas': fields.binary('Database Data'),
        
        'format_declaration_of_directors_fname': fields.char('File Name',size=256),
        'format_declaration_of_directors_datas': fields.binary('Database Data'),
        
        'format_dr_and_agm_fname': fields.char('File Name',size=256),
        'format_dr_and_agm_datas': fields.binary('Database Data'),
        
        'format_letter_of_representation_fname': fields.char('File Name',size=256),
        'format_letter_of_representation_datas': fields.binary('Database Data'),
        
        'format_statement_by_exempt_pte_co_exempt_fname': fields.char('File Name',size=256),
        'format_statement_by_exempt_pte_co_exempt_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_subsequent_year_agm_two()

class report_wizard_agm_strike_off_templates(osv.osv_memory):
    _name = 'report.wizard.agm.strike.off.templates'
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_agm_strike_off_templates, self).default_get(cr, uid, fields, context=context)
        partner_id = False
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
        if context.get('agm_strike_off_templates',False) and context['agm_strike_off_templates']:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
            
#             report_filename='Company Info 20150627'
#             report_extention='.xls'
#             report_name='company_info_20150627'
#             report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
#             res.update({'company_info_20150627_fname': report_val['datas_fname'],
#                         'company_info_20150627_datas': report_val['db_datas']})
            
            report_filename='Strike off_Acra_Resolution'
            report_extention='.doc'
            report_name='strike_off_acra_resolution'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'strike_off_acra_resolution_fname': report_val['datas_fname'],
                        'strike_off_acra_resolution_datas': report_val['db_datas']})
            
            report_filename='Strike off_Agreement Letter'
            report_extention='.doc'
            report_name='strike_off_agreement_letter'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'strike_off_agreement_letter_fname': report_val['datas_fname'],
                        'strike_off_agreement_letter_datas': report_val['db_datas']})
            
            report_filename='strike off_Appointment Letter'
            report_extention='.doc'
            report_name='strike_off_appointment_letter'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'strike_off_appointment_letter_fname': report_val['datas_fname'],
                        'strike_off_appointment_letter_datas': report_val['db_datas']})
            
            report_filename='Strike off_letter'
            report_extention='.doc'
            report_name='strike_off_letter'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'strike_off_letter_fname': report_val['datas_fname'],
                        'strike_off_letter_datas': report_val['db_datas']})
            
            report_filename='Strike off_Letter to IRAS'
            report_extention='.doc'
            report_name='strike_off_letter_to_iras'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'strike_off_letter_to_iras_fname': report_val['datas_fname'],
                        'strike_off_letter_to_iras_datas': report_val['db_datas']})
            
            report_filename='Strike off_Minutes'
            report_extention='.doc'
            report_name='strike_off_minutes'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'strike_off_minutes_fname': report_val['datas_fname'],
                        'strike_off_minutes_datas': report_val['db_datas']})
            
            report_filename='Strike off_Notice'
            report_extention='.doc'
            report_name='strike_off_notice'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'strike_off_notice_fname': report_val['datas_fname'],
                        'strike_off_notice_datas': report_val['db_datas']})
            
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        'company_info_20150627_fname': fields.char('File Name',size=256),
        'company_info_20150627_datas': fields.binary('Database Data'),
        
        'strike_off_acra_resolution_fname': fields.char('File Name',size=256),
        'strike_off_acra_resolution_datas': fields.binary('Database Data'),
        
        'strike_off_agreement_letter_fname': fields.char('File Name',size=256),
        'strike_off_agreement_letter_datas': fields.binary('Database Data'),
        
        'strike_off_appointment_letter_fname': fields.char('File Name',size=256),
        'strike_off_appointment_letter_datas': fields.binary('Database Data'),
        
        'strike_off_letter_fname': fields.char('File Name',size=256),
        'strike_off_letter_datas': fields.binary('Database Data'),
        
        'strike_off_letter_to_iras_fname': fields.char('File Name',size=256),
        'strike_off_letter_to_iras_datas': fields.binary('Database Data'),
        
        'strike_off_minutes_fname': fields.char('File Name',size=256),
        'strike_off_minutes_datas': fields.binary('Database Data'),
        
        'strike_off_notice_fname': fields.char('File Name',size=256),
        'strike_off_notice_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_agm_strike_off_templates()

class report_wizard_agm_ye_blank(osv.osv_memory):
    _name = 'report.wizard.agm.ye.blank'
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_agm_ye_blank, self).default_get(cr, uid, fields, context=context)
        partner_id = False
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
        if context.get('agm_ye_blank',False) and context['agm_ye_blank']:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
            
            report_filename='AR Cert under S197_CompanyName'
            report_extention='.doc'
            report_name='ar_cert_under_s197_companyname'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'ar_cert_under_s197_companyname_fname': report_val['datas_fname'],
                        'ar_cert_under_s197_companyname_datas': report_val['db_datas']})
            
            report_filename='Certificate By An Exempt Pte CompanyName'
            report_extention='.doc'
            report_name='certificate_by_an_exempt_pte_companyname'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'certificate_by_an_exempt_pte_companyname_fname': report_val['datas_fname'],
                        'certificate_by_an_exempt_pte_companyname_datas': report_val['db_datas']})
            
            report_filename='DDF 310814_CompanyName'
            report_extention='.doc'
            report_name='ddf_310814_companyname'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'ddf_310814_companyname_fname': report_val['datas_fname'],
                        'ddf_310814_companyname_datas': report_val['db_datas']})
            
            report_filename='DR and AGM FYE 31.08.2014_CompanyName'
            report_extention='.doc'
            report_name='dr_and_agm_fye_31_08_2014_companyname'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'dr_and_agm_fye_31_08_2014_companyname_fname': report_val['datas_fname'],
                        'dr_and_agm_fye_31_08_2014_companyname_datas': report_val['db_datas']})
            
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        'ar_cert_under_s197_companyname_fname': fields.char('File Name',size=256),
        'ar_cert_under_s197_companyname_datas': fields.binary('Database Data'),
        
        'certificate_by_an_exempt_pte_companyname_fname': fields.char('File Name',size=256),
        'certificate_by_an_exempt_pte_companyname_datas': fields.binary('Database Data'),
        
        'ddf_310814_companyname_fname': fields.char('File Name',size=256),
        'ddf_310814_companyname_datas': fields.binary('Database Data'),
        
        'dr_and_agm_fye_31_08_2014_companyname_fname': fields.char('File Name',size=256),
        'dr_and_agm_fye_31_08_2014_companyname_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_agm_ye_blank()

class report_wizard_eci_template(osv.osv_memory):
    _name = 'report.wizard.eci.template'
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_eci_template, self).default_get(cr, uid, fields, context=context)
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
#         if context.get('eci_template',False) and context['eci_template']:
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
        
        report_filename='ECI Form (For Company) YA 2016 (2)'
        report_extention='.xls'
        report_name='eci_form_for_company_ya_2016'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'eci_form_for_company_ya_2016_fname': report_val['datas_fname'],
                    'eci_form_for_company_ya_2016_datas': report_val['db_datas']})
        
        report_filename='ECI Form (For Tax Agent) YA 2016'
        report_extention='.xls'
        report_name='eci_form_for_tax_agent_ya_2016'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'eci_form_for_tax_agent_ya_2016_fname': report_val['datas_fname'],
                    'eci_form_for_tax_agent_ya_2016_datas': report_val['db_datas']})
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        'eci_form_for_company_ya_2016_fname': fields.char('File Name',size=256),
        'eci_form_for_company_ya_2016_datas': fields.binary('Database Data'),
        
        'eci_form_for_tax_agent_ya_2016_fname': fields.char('File Name',size=256),
        'eci_form_for_tax_agent_ya_2016_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_eci_template()

class report_wizard_appointment_letters(osv.osv_memory):
    _name = 'report.wizard.appointment.letters'
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_appointment_letters, self).default_get(cr, uid, fields, context=context)
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
#         if context.get('eci_template',False) and context['eci_template']:
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
        
        report_filename='Format_Appointment Letter - Responsibilities'
        report_extention='.doc'
        report_name='format_appointment_letter_responsibilities'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'format_appointment_letter_responsibilities_fname': report_val['datas_fname'],
                    'format_appointment_letter_responsibilities_datas': report_val['db_datas']})
        
        report_filename='Format_Corp Sercretary fee'
        report_extention='.doc'
        report_name='format_corp_sercretary_fee'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'format_corp_sercretary_fee_fname': report_val['datas_fname'],
                    'format_corp_sercretary_fee_datas': report_val['db_datas']})
        
        report_filename='Format_Letter of confirmation of accounts'
        report_extention='.doc'
        report_name='format_letter_of_confirmation_of_accounts'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'format_letter_of_confirmation_of_accounts_fname': report_val['datas_fname'],
                    'format_letter_of_confirmation_of_accounts_datas': report_val['db_datas']})
        
        report_filename='Format_Request handover secretary doc'
        report_extention='.doc'
        report_name='format_request_handover_secretary_doc'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'format_request_handover_secretary_doc_fname': report_val['datas_fname'],
                    'format_request_handover_secretary_doc_datas': report_val['db_datas']})
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        'format_appointment_letter_responsibilities_fname': fields.char('File Name',size=256),
        'format_appointment_letter_responsibilities_datas': fields.binary('Database Data'),
        
        'format_corp_sercretary_fee_fname': fields.char('File Name',size=256),
        'format_corp_sercretary_fee_datas': fields.binary('Database Data'),
        
        'format_letter_of_confirmation_of_accounts_fname': fields.char('File Name',size=256),
        'format_letter_of_confirmation_of_accounts_datas': fields.binary('Database Data'),
        
        'format_request_handover_secretary_doc_fname': fields.char('File Name',size=256),
        'format_request_handover_secretary_doc_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_appointment_letters()

class report_wizard_appointment_of_secretary(osv.osv_memory):
    _name = 'report.wizard.appointment.of.secretary'
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_appointment_of_secretary, self).default_get(cr, uid, fields, context=context)
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
#         if context.get('eci_template',False) and context['eci_template']:
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
        
        report_filename='Request handover secretary doc - Han Dian'
        report_extention='.doc'
        report_name='request_handover_secretary_doc_han_dian'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'request_handover_secretary_doc_han_dian_fname': report_val['datas_fname'],
                    'request_handover_secretary_doc_han_dian_datas': report_val['db_datas']})
        
        report_filename='Termination Letter of Corp Sec with Amicorp_Aquavina Investment'
        report_extention='.doc'
        report_name='termination_letter_of_corp_amicorp_aquavina_investment'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'termination_letter_of_corp_amicorp_aquavina_investment_fname': report_val['datas_fname'],
                    'termination_letter_of_corp_amicorp_aquavina_investment_datas': report_val['db_datas']})
        
        report_filename='resigned letter'
        report_extention='.doc'
        report_name='resigned_letter'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'resigned_letter_fname': report_val['datas_fname'],
                    'resigned_letter_datas': report_val['db_datas']})
        
        report_filename='Format_Form 49_Appoint Secretary'
        report_extention='.doc'
        report_name='format_form_49_appoint_secretary'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'format_form_49_appoint_secretary_fname': report_val['datas_fname'],
                    'format_form_49_appoint_secretary_datas': report_val['db_datas']})
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        'request_handover_secretary_doc_han_dian_fname': fields.char('File Name',size=256),
        'request_handover_secretary_doc_han_dian_datas': fields.binary('Database Data'),
        
        'termination_letter_of_corp_amicorp_aquavina_investment_fname': fields.char('File Name',size=256),
        'termination_letter_of_corp_amicorp_aquavina_investment_datas': fields.binary('Database Data'),
        
        'resigned_letter_fname': fields.char('File Name',size=256),
        'resigned_letter_datas': fields.binary('Database Data'),
        
        'format_form_49_appoint_secretary_fname': fields.char('File Name',size=256),
        'format_form_49_appoint_secretary_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_appointment_of_secretary()

class report_wizard_change_of_company_name(osv.osv_memory):
    _name = 'report.wizard.change.of.company.name'
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_change_of_company_name, self).default_get(cr, uid, fields, context=context)
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
#         if context.get('eci_template',False) and context['eci_template']:
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
        
        report_filename='Format_Change Co Name_Attendance List'
        report_extention='.doc'
        report_name='format_change_co_name_attendance_list'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'format_change_co_name_attendance_list_fname': report_val['datas_fname'],
                    'format_change_co_name_attendance_list_datas': report_val['db_datas']})
        
        report_filename='Format_Change Co Name_Minutes'
        report_extention='.doc'
        report_name='format_change_co_name_minutes'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'format_change_co_name_minutes_fname': report_val['datas_fname'],
                    'format_change_co_name_minutes_datas': report_val['db_datas']})
        
        report_filename='Format_Change Co Name__Notice of EGM'
        report_extention='.doc'
        report_name='format_change_co_name_notice_of_egm'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'format_change_co_name_notice_of_egm_fname': report_val['datas_fname'],
                    'format_change_co_name_notice_of_egm_datas': report_val['db_datas']})
        
        report_filename='Format_Change Co Name_Resolution'
        report_extention='.doc'
        report_name='format_change_co_name_resolution'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'format_change_co_name_resolution_fname': report_val['datas_fname'],
                    'format_change_co_name_resolution_datas': report_val['db_datas']})
        
        report_filename='Format_Form 11_Change of Co Name_Notice of Resolution'
        report_extention='.doc'
        report_name='format_form_11_change_of_co_name_notice_of_resolution'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'format_form_11_change_of_co_name_notice_of_resolution_fname': report_val['datas_fname'],
                    'format_form_11_change_of_co_name_notice_of_resolution_datas': report_val['db_datas']})
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        'format_change_co_name_attendance_list_fname': fields.char('File Name',size=256),
        'format_change_co_name_attendance_list_datas': fields.binary('Database Data'),
        
        'format_change_co_name_minutes_fname': fields.char('File Name',size=256),
        'format_change_co_name_minutes_datas': fields.binary('Database Data'),
        
        'format_change_co_name_notice_of_egm_fname': fields.char('File Name',size=256),
        'format_change_co_name_notice_of_egm_datas': fields.binary('Database Data'),
        
        'format_change_co_name_resolution_fname': fields.char('File Name',size=256),
        'format_change_co_name_resolution_datas': fields.binary('Database Data'),
        
        'format_form_11_change_of_co_name_notice_of_resolution_fname': fields.char('File Name',size=256),
        'format_form_11_change_of_co_name_notice_of_resolution_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_change_of_company_name()

class report_wizard_1st_directors_resolution_format(osv.osv_memory):
    _name = 'report.wizard.1st.directors.resolution.format'
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_1st_directors_resolution_format, self).default_get(cr, uid, fields, context=context)
        partner_id = False
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
        if context.get('1st_directors_resolution_format',False) and context['1st_directors_resolution_format']:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
            
            report_filename='1st resolution_One Director'
            report_extention='.doc'
            report_name='1st_resolution_one_director'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'1st_resolution_one_director_fname': report_val['datas_fname'],
                        '1st_resolution_one_director_datas': report_val['db_datas']})
            
            report_filename='1st resolution_Two Directors'
            report_extention='.doc'
            report_name='1st_resolution_two_directors'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'1st_resolution_two_directors_fname': report_val['datas_fname'],
                        '1st_resolution_two_directors_datas': report_val['db_datas']})
            
            report_filename='Format_Statutory Records & Doc - Ack letter'
            report_extention='.doc'
            report_name='format_statutory_records_doc_ack_letter'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'format_statutory_records_doc_ack_letter_fname': report_val['datas_fname'],
                        'format_statutory_records_doc_ack_letter_datas': report_val['db_datas']})
            
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        '1st_resolution_one_director_fname': fields.char('File Name',size=256),
        '1st_resolution_one_director_datas': fields.binary('Database Data'),
        
        '1st_resolution_two_directors_fname': fields.char('File Name',size=256),
        '1st_resolution_two_directors_datas': fields.binary('Database Data'),
        
        'format_statutory_records_doc_ack_letter_fname': fields.char('File Name',size=256),
        'format_statutory_records_doc_ack_letter_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_1st_directors_resolution_format()

class report_wizard_forms_45_49(osv.osv_memory):
    _name = 'report.wizard.forms.45.49'
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_forms_45_49, self).default_get(cr, uid, fields, context=context)
        partner_id = False
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
        if context.get('forms_45_49',False) and context['forms_45_49']:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)

            report_filename='forms_45_491'
            report_extention='.doc'
            report_name='forms_45_491'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'forms_45_491_fname': report_val['datas_fname'],
                        'forms_45_491_datas': report_val['db_datas']})
            
            report_filename='forms_45_492'
            report_extention='.doc'
            report_name='forms_45_492'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'forms_45_492_fname': report_val['datas_fname'],
                        'forms_45_492_datas': report_val['db_datas']})
            
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        'forms_45_491_fname': fields.char('File Name',size=256),
        'forms_45_491_datas': fields.binary('Database Data'),
        
        'forms_45_492_fname': fields.char('File Name',size=256),
        'forms_45_492_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_forms_45_49()

class report_wizard_share_certificates_one(osv.osv_memory):
    _name = 'report.wizard.share.certificates.one'
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_share_certificates_one, self).default_get(cr, uid, fields, context=context)
        partner_id = False
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
        if context.get('share_certificates_one',False) and context['share_certificates_one']:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)

            report_filename='Share cert 1_xx shares_Format03_Our Reg Office'
            report_extention='.doc'
            report_name='share_cert_1_xx_shares_format03_our_reg_office'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'share_cert_1_xx_shares_format03_our_reg_office_fname': report_val['datas_fname'],
                        'share_cert_1_xx_shares_format03_our_reg_office_datas': report_val['db_datas']})
            
            report_filename='Share cert 1_xx shares_Format04'
            report_extention='.doc'
            report_name='share_cert_1_xx_shares_format04'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'share_cert_1_xx_shares_format04_fname': report_val['datas_fname'],
                        'share_cert_1_xx_shares_format04_datas': report_val['db_datas']})
            
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        'share_cert_1_xx_shares_format03_our_reg_office_fname': fields.char('File Name',size=256),
        'share_cert_1_xx_shares_format03_our_reg_office_datas': fields.binary('Database Data'),
        
        'share_cert_1_xx_shares_format04_fname': fields.char('File Name',size=256),
        'share_cert_1_xx_shares_format04_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_share_certificates_one()

class report_wizard_share_certificates_two(osv.osv_memory):
    _name = 'report.wizard.share.certificates.two'
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_share_certificates_two, self).default_get(cr, uid, fields, context=context)
        partner_id = False
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
        if context.get('share_certificates_two',False) and context['share_certificates_two']:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)

            report_filename='Share cert 1_xx shares_Format01'
            report_extention='.doc'
            report_name='share_cert_1_xx_shares_format01'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'share_cert_1_xx_shares_format01_fname': report_val['datas_fname'],
                        'share_cert_1_xx_shares_format01_datas': report_val['db_datas']})
            
            report_filename='Share cert 1_xx shares_Format02_Our Reg Office'
            report_extention='.doc'
            report_name='share_cert_1_xx_shares_format02_our_reg_office'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'share_cert_1_xx_shares_format02_our_reg_office_fname': report_val['datas_fname'],
                        'share_cert_1_xx_shares_format02_our_reg_office_datas': report_val['db_datas']})
            
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        'share_cert_1_xx_shares_format01_fname': fields.char('File Name',size=256),
        'share_cert_1_xx_shares_format01_datas': fields.binary('Database Data'),
        
        'share_cert_1_xx_shares_format02_our_reg_office_fname': fields.char('File Name',size=256),
        'share_cert_1_xx_shares_format02_our_reg_office_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_share_certificates_two()

class report_wizard_issue_shares(osv.osv_memory):
    _name = 'report.wizard.issue.shares'
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_issue_shares, self).default_get(cr, uid, fields, context=context)
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
#         if context.get('eci_template',False) and context['eci_template']:
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
        
        report_filename='Format_Attendance List_ Issue shares'
        report_extention='.doc'
        report_name='format_attendance_list_issue_shares'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'format_attendance_list_issue_shares_fname': report_val['datas_fname'],
                    'format_attendance_list_issue_shares_datas': report_val['db_datas']})
        
        report_filename='Format_Director Resolution_ Issue shares'
        report_extention='.doc'
        report_name='format_director_resolution_issue_shares'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'format_director_resolution_issue_shares_fname': report_val['datas_fname'],
                    'format_director_resolution_issue_shares_datas': report_val['db_datas']})
        
        report_filename='Format_Letter_Consent of Waiver_ Issue shares'
        report_extention='.doc'
        report_name='format_letter_consent_of_waiver_issue_shares'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'format_letter_consent_of_waiver_issue_shares_fname': report_val['datas_fname'],
                    'format_letter_consent_of_waiver_issue_shares_datas': report_val['db_datas']})
        
        report_filename='Format_Minutes of EGM_Issue shares'
        report_extention='.doc'
        report_name='format_minutes_of_egm_issue_shares'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'format_minutes_of_egm_issue_shares_fname': report_val['datas_fname'],
                    'format_minutes_of_egm_issue_shares_datas': report_val['db_datas']})
        
        report_filename='Format_Notice of EGM_ Issue shares'
        report_extention='.doc'
        report_name='format_notice_of_egm_issue_shares'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'format_notice_of_egm_issue_shares_fname': report_val['datas_fname'],
                    'format_notice_of_egm_issue_shares_datas': report_val['db_datas']})
        
        report_filename='Format_Paid-up Capital Application_ ___k shares'
        report_extention='.doc'
        report_name='format_paid_up_capital_application_k_shares'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'format_paid_up_capital_application_k_shares_fname': report_val['datas_fname'],
                    'format_paid_up_capital_application_k_shares_datas': report_val['db_datas']})
        
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        'format_attendance_list_issue_shares_fname': fields.char('File Name',size=256),
        'format_attendance_list_issue_shares_datas': fields.binary('Database Data'),
        
        'format_director_resolution_issue_shares_fname': fields.char('File Name',size=256),
        'format_director_resolution_issue_shares_datas': fields.binary('Database Data'),
        
        'format_letter_consent_of_waiver_issue_shares_fname': fields.char('File Name',size=256),
        'format_letter_consent_of_waiver_issue_shares_datas': fields.binary('Database Data'),
        
        'format_minutes_of_egm_issue_shares_fname': fields.char('File Name',size=256),
        'format_minutes_of_egm_issue_shares_datas': fields.binary('Database Data'),
        
        'format_notice_of_egm_issue_shares_fname': fields.char('File Name',size=256),
        'format_notice_of_egm_issue_shares_datas': fields.binary('Database Data'),
        
        'format_paid_up_capital_application_k_shares_fname': fields.char('File Name',size=256),
        'format_paid_up_capital_application_k_shares_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_issue_shares()

class report_wizard_resignation_director_secretary(osv.osv_memory):
    _name = 'report.wizard.resignation.director.secretary'
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_resignation_director_secretary, self).default_get(cr, uid, fields, context=context)
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
#         if context.get('eci_template',False) and context['eci_template']:
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
        
        report_filename='Format_Resignation letter_Director Name'
        report_extention='.doc'
        report_name='format_resignation_letter_director_name'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'format_resignation_letter_director_name_fname': report_val['datas_fname'],
                    'format_resignation_letter_director_name_datas': report_val['db_datas']})
        
        report_filename='Format_Resolution_Resign Director and Appoint Secretary'
        report_extention='.doc'
        report_name='format_resolution_resign_director_and_appoint_secretary'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'format_resolution_resign_director_and_appoint_secretary_fname': report_val['datas_fname'],
                    'format_resolution_resign_director_and_appoint_secretary_datas': report_val['db_datas']})
        
        report_filename='Format_Form 49_Resigned as Director'
        report_extention='.doc'
        report_name='format_form_49_resigned_as_director'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'format_form_49_resigned_as_director_fname': report_val['datas_fname'],
                    'format_form_49_resigned_as_director_datas': report_val['db_datas']})
        
        report_filename='Format_Form 49_Resigned as Director and Appoint Secretary'
        report_extention='.doc'
        report_name='format_form_49_resigned_as_director_and_appoint_secretary'
        report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
        res.update({'format_form_49_resigned_as_director_and_appoint_secretary_fname': report_val['datas_fname'],
                    'format_form_49_resigned_as_director_and_appoint_secretary_datas': report_val['db_datas']})
        
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        'format_resignation_letter_director_name_fname': fields.char('File Name',size=256),
        'format_resignation_letter_director_name_datas': fields.binary('Database Data'),
        
        'format_resolution_resign_director_and_appoint_secretary_fname': fields.char('File Name',size=256),
        'format_resolution_resign_director_and_appoint_secretary_datas': fields.binary('Database Data'),
        
        'format_form_49_resigned_as_director_fname': fields.char('File Name',size=256),
        'format_form_49_resigned_as_director_datas': fields.binary('Database Data'),
        
        'format_form_49_resigned_as_director_and_appoint_secretary_fname': fields.char('File Name',size=256),
        'format_form_49_resigned_as_director_and_appoint_secretary_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_resignation_director_secretary()

class report_wizard_resolution_form(osv.osv_memory):
    _name = 'report.wizard.resolution.form'
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_resolution_form, self).default_get(cr, uid, fields, context=context)
        partner_id = False
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
#         if context.get('resolution_form_page01',False) and context['resolution_form_page01']:
#             partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
            
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_resolution_form()

class report_wizard_resolution_form_page01(osv.osv_memory):
    _name = 'report.wizard.resolution.form.page01'
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_resolution_form_page01, self).default_get(cr, uid, fields, context=context)
        partner_id = False
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
        if context.get('resolution_form_page01',False) and context['resolution_form_page01']:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
    
            report_filename='resolution_form1'
            report_extention='.doc'
            report_name='resolution_form1'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'resolution_form1_fname': report_val['datas_fname'],
                        'resolution_form1_datas': report_val['db_datas']})
            
            report_filename='resolution_form2'
            report_extention='.doc'
            report_name='resolution_form2'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'resolution_form2_fname': report_val['datas_fname'],
                        'resolution_form2_datas': report_val['db_datas']})
            
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        'resolution_form1_fname': fields.char('File Name',size=256),
        'resolution_form1_datas': fields.binary('Database Data'),
        
        'resolution_form2_fname': fields.char('File Name',size=256),
        'resolution_form2_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_resolution_form_page01()

class report_wizard_resolution_form_page02(osv.osv_memory):
    _name = 'report.wizard.resolution.form.page02'
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_resolution_form_page02, self).default_get(cr, uid, fields, context=context)
        partner_id = False
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
        if context.get('resolution_form_page02',False) and context['resolution_form_page02']:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
    
            report_filename='resolution_form12'
            report_extention='.doc'
            report_name='resolution_form12'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'resolution_form1_fname': report_val['datas_fname'],
                        'resolution_form1_datas': report_val['db_datas']})
            
            report_filename='resolution_form22'
            report_extention='.doc'
            report_name='resolution_form22'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'resolution_form2_fname': report_val['datas_fname'],
                        'resolution_form2_datas': report_val['db_datas']})
            
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        'resolution_form1_fname': fields.char('File Name',size=256),
        'resolution_form1_datas': fields.binary('Database Data'),
        
        'resolution_form2_fname': fields.char('File Name',size=256),
        'resolution_form2_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_resolution_form_page02()

class report_wizard_share_transfer(osv.osv_memory):
    _name = 'report.wizard.share.transfer'
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_share_transfer, self).default_get(cr, uid, fields, context=context)
        partner_id = False
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
        if context.get('share_transfer',False) and context['share_transfer']:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)

            report_filename='share_transfer1'
            report_extention='.doc'
            report_name='share_transfer1'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'share_transfer1_fname': report_val['datas_fname'],
                        'share_transfer1_datas': report_val['db_datas']})
            
            report_filename='share_transfer2'
            report_extention='.doc'
            report_name='share_transfer2'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'share_transfer2_fname': report_val['datas_fname'],
                        'share_transfer2_datas': report_val['db_datas']})
            
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        'share_transfer1_fname': fields.char('File Name',size=256),
        'share_transfer1_datas': fields.binary('Database Data'),
        
        'share_transfer2_fname': fields.char('File Name',size=256),
        'share_transfer2_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_share_transfer()

class report_wizard_format_egm_dated_xxxx(osv.osv_memory):
    _name = 'report.wizard.format.egm.dated.xxxx'
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_format_egm_dated_xxxx, self).default_get(cr, uid, fields, context=context)
        partner_id = False
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
        if context.get('format_egm_dated_xxxx',False) and context['format_egm_dated_xxxx']:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)

            report_filename='Attendance List_Transfer of shares_'
            report_extention='.doc'
            report_name='attendance_list_transfer_of_shares'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'attendance_list_transfer_of_shares_fname': report_val['datas_fname'],
                        'attendance_list_transfer_of_shares_datas': report_val['db_datas']})
            
            report_filename='Letter_Consent of Waiver'
            report_extention='.doc'
            report_name='letter_consent_of_waiver'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'letter_consent_of_waiver_fname': report_val['datas_fname'],
                        'letter_consent_of_waiver_datas': report_val['db_datas']})
            
            report_filename='Minutes_Transfer of Shares'
            report_extention='.doc'
            report_name='minutes_transfer_of_shares'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'minutes_transfer_of_shares_fname': report_val['datas_fname'],
                        'minutes_transfer_of_shares_datas': report_val['db_datas']})
            
            report_filename='Notice of EGM_Transfer of Shares'
            report_extention='.doc'
            report_name='notice_of_egm_transfer_of_shares'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'notice_of_egm_transfer_of_shares_fname': report_val['datas_fname'],
                        'notice_of_egm_transfer_of_shares_datas': report_val['db_datas']})
            
            report_filename='Resolution_Transfer of Shares'
            report_extention='.doc'
            report_name='resolution_transfer_of_shares'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'resolution_transfer_of_shares_fname': report_val['datas_fname'],
                        'resolution_transfer_of_shares_datas': report_val['db_datas']})
            
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        'attendance_list_transfer_of_shares_fname': fields.char('File Name',size=256),
        'attendance_list_transfer_of_shares_datas': fields.binary('Database Data'),
        
        'letter_consent_of_waiver_fname': fields.char('File Name',size=256),
        'letter_consent_of_waiver_datas': fields.binary('Database Data'),
        
        'minutes_transfer_of_shares_fname': fields.char('File Name',size=256),
        'minutes_transfer_of_shares_datas': fields.binary('Database Data'),
        
        'notice_of_egm_transfer_of_shares_fname': fields.char('File Name',size=256),
        'notice_of_egm_transfer_of_shares_datas': fields.binary('Database Data'),
        
        'resolution_transfer_of_shares_fname': fields.char('File Name',size=256),
        'resolution_transfer_of_shares_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_format_egm_dated_xxxx()

class report_wizard_format_share_transfer_form(osv.osv_memory):
    _name = 'report.wizard.format.share.transfer.form'
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_format_share_transfer_form, self).default_get(cr, uid, fields, context=context)
        partner_id = False
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
        if context.get('format_share_transfer_form',False) and context['format_share_transfer_form']:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)

            report_filename='Share transfer form from who to who'
            report_extention='.xls'
            report_name='share_transfer_form_from_who_to_who'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'share_transfer_form_from_who_to_who_fname': report_val['datas_fname'],
                        'share_transfer_form_from_who_to_who_datas': report_val['db_datas']})
            
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        'share_transfer_form_from_who_to_who_fname': fields.char('File Name',size=256),
        'share_transfer_form_from_who_to_who_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_format_share_transfer_form()

class report_wizard_strike_off_egm_templates(osv.osv_memory):
    _name = 'report.wizard.strike.off.egm.templates'
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_strike_off_egm_templates, self).default_get(cr, uid, fields, context=context)
        partner_id = False
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
        if context.get('strike_off_egm_templates',False) and context['strike_off_egm_templates']:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)

            report_filename='Strike off_Acra_Resolution'
            report_extention='.doc'
            report_name='egm_strike_off_acra_resolution'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'egm_strike_off_acra_resolution_fname': report_val['datas_fname'],
                        'egm_strike_off_acra_resolution_datas': report_val['db_datas']})
            
            report_filename='Strike off_Agreement Letter'
            report_extention='.doc'
            report_name='egm_strike_off_agreement_letter'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'egm_strike_off_agreement_letter_fname': report_val['datas_fname'],
                        'egm_strike_off_agreement_letter_datas': report_val['db_datas']})
            
            report_filename='Strike off_Appointment Letter'
            report_extention='.doc'
            report_name='egm_strike_off_appointment_letter'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'egm_strike_off_appointment_letter_fname': report_val['datas_fname'],
                        'egm_strike_off_appointment_letter_datas': report_val['db_datas']})
            
            report_filename='strike off declaration'
            report_extention='.doc'
            report_name='egm_strike_off_declaration'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'egm_strike_off_declaration_fname': report_val['datas_fname'],
                        'egm_strike_off_declaration_datas': report_val['db_datas']})
            
            report_filename='Strike off_letter'
            report_extention='.doc'
            report_name='egm_strike_off_letter'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'egm_strike_off_letter_fname': report_val['datas_fname'],
                        'egm_strike_off_letter_datas': report_val['db_datas']})
            
            report_filename='Strike off_Letter to IRAS'
            report_extention='.doc'
            report_name='egm_strike_off_letter_to_iras'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'egm_strike_off_letter_to_iras_fname': report_val['datas_fname'],
                        'egm_strike_off_letter_to_iras_datas': report_val['db_datas']})
            
            report_filename='Strike off_Minutes'
            report_extention='.doc'
            report_name='egm_strike_off_minutes'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'egm_strike_off_minutes_fname': report_val['datas_fname'],
                        'egm_strike_off_minutes_datas': report_val['db_datas']})
            
            report_filename='Strike off_Notice'
            report_extention='.doc'
            report_name='egm_strike_off_notice'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'egm_strike_off_notice_fname': report_val['datas_fname'],
                        'egm_strike_off_notice_datas': report_val['db_datas']})
            
            report_filename='Healthy Rays_strike off declaration'
            report_extention='.doc'
            report_name='healthy_rays_strike_off_declaration'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'healthy_rays_strike_off_declaration_fname': report_val['datas_fname'],
                        'healthy_rays_strike_off_declaration_datas': report_val['db_datas']})
            
            report_filename='Healty Rays_Strike off_Notice'
            report_extention='.doc'
            report_name='healty_rays_strike_off_notice'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'healty_rays_strike_off_notice_fname': report_val['datas_fname'],
                        'healty_rays_strike_off_notice_datas': report_val['db_datas']})
            
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        'egm_strike_off_acra_resolution_fname': fields.char('File Name',size=256),
        'egm_strike_off_acra_resolution_datas': fields.binary('Database Data'),
        
        'egm_strike_off_agreement_letter_fname': fields.char('File Name',size=256),
        'egm_strike_off_agreement_letter_datas': fields.binary('Database Data'),
        
        'egm_strike_off_appointment_letter_fname': fields.char('File Name',size=256),
        'egm_strike_off_appointment_letter_datas': fields.binary('Database Data'),
        
        'egm_strike_off_declaration_fname': fields.char('File Name',size=256),
        'egm_strike_off_declaration_datas': fields.binary('Database Data'),
        
        'egm_strike_off_letter_fname': fields.char('File Name',size=256),
        'egm_strike_off_letter_datas': fields.binary('Database Data'),
        
        'egm_strike_off_letter_to_iras_fname': fields.char('File Name',size=256),
        'egm_strike_off_letter_to_iras_datas': fields.binary('Database Data'),
        
        'egm_strike_off_minutes_fname': fields.char('File Name',size=256),
        'egm_strike_off_minutes_datas': fields.binary('Database Data'),
        
        'egm_strike_off_notice_fname': fields.char('File Name',size=256),
        'egm_strike_off_notice_datas': fields.binary('Database Data'),
        
        'healthy_rays_strike_off_declaration_fname': fields.char('File Name',size=256),
        'healthy_rays_strike_off_declaration_datas': fields.binary('Database Data'),
        
        'healty_rays_strike_off_notice_fname': fields.char('File Name',size=256),
        'healty_rays_strike_off_notice_datas': fields.binary('Database Data'),
        
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_strike_off_egm_templates()

class report_wizard_strike_off_sample(osv.osv_memory):
    _name = 'report.wizard.strike.off.sample'
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(report_wizard_strike_off_sample, self).default_get(cr, uid, fields, context=context)
        partner_id = False
        if not res.get('partner_id', False) and context.get('active_id',False):
            res.update({'partner_id':context['active_id']})
            partner_id = context['active_id']
        if not partner_id:
            partner_id = res['partner_id']
        if context.get('strike_off_sample',False) and context['strike_off_sample']:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)

            report_filename='Agreement _Strike off'
            report_extention='.doc'
            report_name='agreement_strike_off'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'agreement_strike_off_fname': report_val['datas_fname'],
                        'agreement_strike_off_datas': report_val['db_datas']})
            
            report_filename='Appointment Letter_Flavors Whisky'
            report_extention='.doc'
            report_name='appointment_letter_flavors_whisky'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'appointment_letter_flavors_whisky_fname': report_val['datas_fname'],
                        'appointment_letter_flavors_whisky_datas': report_val['db_datas']})
            
            report_filename='EGM - Notice strike off'
            report_extention='.doc'
            report_name='egm_notice_strike_off'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'egm_notice_strike_off_fname': report_val['datas_fname'],
                        'egm_notice_strike_off_datas': report_val['db_datas']})
            
            report_filename='Flavors Whisky - strike off letter'
            report_extention='.doc'
            report_name='flavors_whisky_strike_off_letter'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'flavors_whisky_strike_off_letter_fname': report_val['datas_fname'],
                        'flavors_whisky_strike_off_letter_datas': report_val['db_datas']})
            
            report_filename='Letter to IRAS'
            report_extention='.doc'
            report_name='letter_to_irsa'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'letter_to_irsa_fname': report_val['datas_fname'],
                        'letter_to_irsa_datas': report_val['db_datas']})
            
            report_filename='Minutes'
            report_extention='.doc'
            report_name='minutes'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'minutes_fname': report_val['datas_fname'],
                        'minutes_datas': report_val['db_datas']})
            
            report_filename='Request handover secretary doc - Flavors Whisky'
            report_extention='.doc'
            report_name='request_handover_secretary_doc_flavors_whisky'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'request_handover_secretary_doc_flavors_whisky_fname': report_val['datas_fname'],
                        'request_handover_secretary_doc_flavors_whisky_datas': report_val['db_datas']})
            
            report_filename='Resolution  strike off EGM'
            report_extention='.doc'
            report_name='resolution_strike_off_egm'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'resolution_strike_off_egm_fname': report_val['datas_fname'],
                        'resolution_strike_off_egm_datas': report_val['db_datas']})
            
            report_filename='strike off declaration_Flavors Apple_Goh Hock Leong'
            report_extention='.doc'
            report_name='strike_off_declaration_flavors_apple_goh_hock_leong'
            report_val = self.cover_print(cr, uid, 'res.partner', partner, report_name, report_filename, report_extention,context)
            res.update({'strike_off_declaration_flavors_apple_goh_hock_leong_fname': report_val['datas_fname'],
                        'strike_off_declaration_flavors_apple_goh_hock_leong_datas': report_val['db_datas']})
            
        return res
    
    _columns = {
        'name': fields.char('Name',size=1024),
        'partner_id': fields.many2one('res.partner','Partner'),
        
        'agreement_strike_off_fname': fields.char('File Name',size=256),
        'agreement_strike_off_datas': fields.binary('Database Data'),
        
        'appointment_letter_flavors_whisky_fname': fields.char('File Name',size=256),
        'appointment_letter_flavors_whisky_datas': fields.binary('Database Data'),
        
        'egm_notice_strike_off_fname': fields.char('File Name',size=256),
        'egm_notice_strike_off_datas': fields.binary('Database Data'),
        
        'flavors_whisky_strike_off_letter_fname': fields.char('File Name',size=256),
        'flavors_whisky_strike_off_letter_datas': fields.binary('Database Data'),
        
        'letter_to_irsa_fname': fields.char('File Name',size=256),
        'letter_to_irsa_datas': fields.binary('Database Data'),
        
        'minutes_fname': fields.char('File Name',size=256),
        'minutes_datas': fields.binary('Database Data'),
        
        'request_handover_secretary_doc_flavors_whisky_fname': fields.char('File Name',size=256),
        'request_handover_secretary_doc_flavors_whisky_datas': fields.binary('Database Data'),
        
        'resolution_strike_off_egm_fname': fields.char('File Name',size=256),
        'resolution_strike_off_egm_datas': fields.binary('Database Data'),
        
        'strike_off_declaration_flavors_apple_goh_hock_leong_fname': fields.char('File Name',size=256),
        'strike_off_declaration_flavors_apple_goh_hock_leong_datas': fields.binary('Database Data'),
    }
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
report_wizard_strike_off_sample()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: