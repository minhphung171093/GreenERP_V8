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

{
    'name': 'Green ERP',
    'version': '1.0',
    'category': 'Green ERP',
    'sequence': 14,
    'author': 'nguyentoanit@gmail.com',
    'website' : 'http://www.incomtech.com.vn',
    'depends': ['base','crm','sale','purchase','account','account_voucher','hr','account_analytic_analysis','hr_holidays','hr_payroll','product','stock','procurement','email_template'],
    'data': [
             'security/sale_security.xml',
             'crm_lead_view.xml',
             'accounting_view.xml',
             'purchase_view.xml',
             'warehouse_view.xml',
             'human_resources_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
