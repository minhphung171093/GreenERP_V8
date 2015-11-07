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
from openerp import netsvc

# from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class import_congno(osv.osv):
    _name = 'import.congno'
    
    def _data_get(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        bin_size = context.get('bin_size')
        for attach in self.browse(cr, uid, ids, context=context):
            result[attach.id] = attach.db_datas
        return result

    def _data_set(self, cr, uid, id, name, value, arg, context=None):
        # We dont handle setting data to null
        if not value:
            return True
        if context is None:
            context = {}
        file_size = len(value.decode('base64'))
        super(import_congno, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True

    _columns = {
        'name': fields.date('Ngày', required=True,states={'done': [('readonly', True)]}),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='GL Account', type="binary", nodrop=True,states={'done': [('readonly', True)]}),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'state':fields.selection([('draft', 'Mới tạo'),('done', 'Đã nhập')],'Trạng thái', readonly=True)
    }
    
    _defaults = {
        'state':'draft',
        'name': time.strftime('%Y-%m-%d'),
    }
    
    def bt_import_thuchi_ho_dienthoai(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        import_obj = self.pool.get('cauhinh.thumuc.import')
        invoice_obj = self.pool.get('account.invoice')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        wf_service = netsvc.LocalService("workflow")
        if context.get('import_loai_congno',False):
            try:
                import_ids = import_obj.search(cr, uid, [('mlg_type','=',context['import_loai_congno'])])
                if not import_ids:
                    raise osv.except_osv(_('Cảnh báo!'), 'Chưa cấu hình thư mục để nhập vào')
                dir_path = import_obj.browse(cr, uid, import_ids[0]).name
                path = dir_path+'/Importing/'
                done_path = dir_path+'/Done/'
                bin_value = (this.datas).decode('base64')
                f_name = this.datas_fname and (this.datas_fname[:-4]+'_'+time.strftime('%Y-%m-%d %H:%M:%S')+this.datas_fname[-4:]) or ''
                file_path = path+f_name
                open(file_path,'wb').write(bin_value)
                
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    
                    try:
                        file_data = csvUti._read_file(f_path)
                    except Exception, e:
                        error_path = dir_path+'/Error/'
                        csvUti._moveFiles([file_name],error_path)
                        continue
                    
                    for data in file_data:
                        print data
                        sql = '''
                            select id from account_account where code='%s' limit 1
                        '''%(data['MÃ CHI NHÁNH'])
                        cr.execute(sql)
                        chinhanh_ids = cr.fetchone()
                        
                        sql = '''
                            select id,bai_giaoca_id,account_ht_id from res_partner where chinhanh_id=%s and ma_doi_tuong='%s' limit 1
                        '''%(chinhanh_ids[0],data['MÃ ĐỐI TƯỢNG'])
                        cr.execute(sql)
                        partner = cr.fetchone()
                        partner_id = partner and partner[0] or False
                        account_id = partner and partner[2] or False
                        bai_giaoca_id = partner and partner[1] or False
                        
                        ldt = data['LOẠI ĐỐI TƯỢNG']
                        loai_doituong=''
                        if ldt=='Lái xe':
                            loai_doituong='taixe'
                        if ldt=='Nhân viên văn phòng':
                            loai_doituong='taixe'
                            
                        journal_ids = self.pool.get('account.journal').search(cr, uid, [('code','=','TG')])
                        
                        vals = {
                            'mlg_type': 'chi_ho_dien_thoai',
                            'type': 'out_invoice',
                            'account_id': account_id,
                            'chinhanh_id': chinhanh_ids and chinhanh_ids[0] or False,
                            'loai_doituong': loai_doituong,
                            'partner_id': partner_id,
                            'date_invoice': data['NGÀY GIAO DỊCH'],
                            'so_hoa_don': data['SỐ HÓA ĐƠN'],
                            'so_dien_thoai': data['SỐ ĐIỆN THOẠI'],
                            'so_tien': data['SỐ TIỀN'],
                            'dien_giai': data['DIỄN GIẢI'],
                            'journal_id': journal_ids and journal_ids[0] or False,
                            'bai_giaoca_id': bai_giaoca_id,
                        }
                        invoice_vals = invoice_obj.onchange_dien_giai_st(cr, uid, [], data['DIỄN GIẢI'], data['SỐ TIỀN'], journal_ids and journal_ids[0] or False, context)['value']
                        vals.update(invoice_vals)
                        invoice_id = invoice_obj.create(cr, uid, vals)
                        wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
                    csvUti._moveFiles([file_name],done_path)
#                 os.rename("path/to/current/file.foo", "path/to/new/desination/for/file.foo")-> chuyen doi thu muc
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e))
        return self.write(cr, uid, ids, {'state':'done'})
#         return True
    
import_congno()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
