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

import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression
from openerp.tools.translate import _
import time
from openerp.exceptions import except_orm, Warning, RedirectWarning
import base64
from openerp import SUPERUSER_ID
import hashlib
import os
import logging
from openerp.addons.mlg_arap_account import lib_csv 

_logger = logging.getLogger(__name__)

class import_phaithu_chiho_dienthoai(osv.osv):
    _name = 'import.phaithu.chiho.dienthoai'
    def _data_get(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'hr_identities_attachment.location')
        bin_size = context.get('bin_size')
        for attach in self.browse(cr, uid, ids, context=context):
            if location and attach.store_fname:
                result[attach.id] = self._file_read(cr, uid, location, attach.store_fname, bin_size)
            else:
                result[attach.id] = attach.db_datas
        return result

    def _data_set(self, cr, uid, id, name, value, arg, context=None):
        # We dont handle setting data to null
        if not value:
            return True
        if context is None:
            context = {}
        file_size = len(value.decode('base64'))
        super(import_phaithu_chiho_dienthoai, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True

    _columns = {
        'name': fields.date('Date Import', required=True,states={'done': [('readonly', True)]}),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='GL Account', type="binary", nodrop=True,states={'done': [('readonly', True)]}),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True)
    }
    
    _defaults = {
        'state':'draft',
        'name': time.strftime('%Y-%m-%d'),
        
    }
    
    def bt_import(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            location = '/home/phung11764/OpenERP/'
            bin_value = (this.datas).decode('base64')
            filt_path = location+(this.datas_fname or '')
            open(filt_path,'wb').write(bin_value)
            
            path = '/home/phung11764/csv'
            csvUti = lib_csv.csv_ultilities()
            for file_name in csvUti._read_files_folder(path):
                f_path = file_name
                file_data = csvUti._read_file(f_path)
                print file_data
                csvUti._moveFiles([file_name],'/home/phung11764/csv_done')
#             os.rename("path/to/current/file.foo", "path/to/new/desination/for/file.foo")
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return self.write(cr, uid, ids, {'state':'done'})
    
import_phaithu_chiho_dienthoai()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
