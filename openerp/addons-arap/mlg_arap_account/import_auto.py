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
from glob import glob

from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class import_congno_tudong(osv.osv):
    _name = 'import.congno.tudong'

    _columns = {
        'name': fields.date('Tên', required=True),
    }
    
    def import_phaithu_thunoxuong_bdsc(self, cr, uid, context=None):
        import_obj = self.pool.get('cauhinh.thumuc.import.tudong')
        invoice_obj = self.pool.get('account.invoice')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        wf_service = netsvc.LocalService("workflow")
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','thu_no_xuong')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+'/Importing/'
                done_path = dir_path.name+'/Done/'
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    try:
                        file_data = csvUti._read_file(f_path)
                        
                        for data in file_data:
                            if data['so_tien'] <= 0:
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            vals={}
                            account_id = False
                            sql = '''
                                select id from account_account where code='%s' limit 1
                            '''%(data['ma_chi_nhanh'])
                            cr.execute(sql)
                            chinhanh_ids = cr.fetchone()
                            if not chinhanh_ids:
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy chi nhánh')
                            
                            sql = '''
                                select id,bai_giaoca_id,account_ht_id,cmnd,giayphep_kinhdoanh,taixe,nhadautu,nhanvienvanphong
                                    from res_partner where ma_doi_tuong='%s' limit 1
                            '''%(data['ma_doi_tuong'])
                            cr.execute(sql)
                            partner = cr.dictfetchone()
                            if not partner:
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy đối tượng')
                            partner_id = partner and partner['id'] or False
                            bai_giaoca_id = partner and partner['bai_giaoca_id'] or False
                            
                            loai_doituong=''
                            if partner['taixe']==True:
                                loai_doituong='taixe'
                                account_id = partner and partner['account_ht_id'] or False
                            if partner['nhanvienvanphong']==True:
                                loai_doituong='nhanvienvanphong'
                                account_id = partner and partner['account_ht_id'] or False
                            if partner['nhadautu']==True:
                                loai_doituong='nhadautu'
                                sql = '''
                                    select nhom_chinhanh_id from chi_nhanh_line where chinhanh_id=%s and partner_id=%s
                                '''%(chinhanh_ids[0],partner_id)
                                cr.execute(sql)
                                account_ids = [r[0] for r in cr.fetchall()]
                                account_id = account_ids and account_ids[0] or False
                                vals.update({'cmnd': partner['cmnd'],'giayphep_kinhdoanh': partner['giayphep_kinhdoanh'],'chinhanh_ndt_id':chinhanh_ids[0]})
                                
                            journal_ids = self.pool.get('account.journal').search(cr, uid, [('code','=','TG')])
                            
                            bsx = data['bien_so_xe']
                            sql = ''' select id from bien_so_xe where name='%s' '''%(bsx)
                            cr.execute(sql)
                            bien_so_xe_ids = cr.fetchone()
                            if bsx and not bien_so_xe_ids:
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy biển số xe')
                            
                            mx = data['ma_xuong']
                            sql = ''' select id from ma_xuong where code='%s' '''%(mx)
                            cr.execute(sql)
                            ma_xuong_ids = cr.fetchone()
                            if mx and not ma_xuong_ids:
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy mã xưởng')
                            
                            date_invoice=datetime.strptime(data['ngay_giao_dich'],'%d/%m/%Y').strftime('%Y-%m-%d')
                            
                            vals.update({
                                'mlg_type': 'thu_no_xuong',
                                'type': 'out_invoice',
                                'account_id': account_id,
                                'chinhanh_id': chinhanh_ids and chinhanh_ids[0] or False,
                                'loai_doituong': loai_doituong,
                                'partner_id': partner_id,
                                'date_invoice': date_invoice,
                                'so_hop_dong': data['so_hop_dong'],
                                'ma_bang_chiettinh_chiphi_sua': data['ma_chiet_tinh'],
                                'so_tien': data['so_tien'],
                                'dien_giai': data['dien_giai'],
                                'journal_id': journal_ids and journal_ids[0] or False,
                                'bai_giaoca_id': bai_giaoca_id,
                                'bien_so_xe_id': bien_so_xe_ids and bien_so_xe_ids[0] or False,
                                'ma_xuong_id': ma_xuong_ids and ma_xuong_ids[0] or False,
                            })
                            invoice_vals = invoice_obj.onchange_dien_giai_st(cr, uid, [], data['dien_giai'], data['so_tien'], journal_ids and journal_ids[0] or False, context)['value']
                            vals.update(invoice_vals)
                            invoice_id = invoice_obj.create(cr, uid, vals)
                            wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+f_path.split('/')[-1],
                            'loai_giaodich': 'Thu nợ xưởng (BDSC)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        error_path = dir_path.name+'/Error/'
                        csvUti._moveFiles([f_path],error_path)
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,time.strftime('%Y-%m-%d %H:%M:%S'),1,time.strftime('%Y-%m-%d %H:%M:%S'),time.strftime('%Y-%m-%d %H:%M:%S'),
                             error_path+f_path.split('/')[-1],'Thu nợ xưởng (BDSC)','Thu','Nhập','Tự động','Lỗi',''
                        )
                        cr.execute(sql)
                        raise osv.except_osv(_('Warning!'), str(e))
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def import_phaithu_thuphithuonghieu_htkd(self, cr, uid, context=None):
        import_obj = self.pool.get('cauhinh.thumuc.import.tudong')
        invoice_obj = self.pool.get('account.invoice')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        wf_service = netsvc.LocalService("workflow")
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','thu_phi_thuong_hieu_htkd')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+'/Importing/'
                done_path = dir_path.name+'/Done/'
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    try:
                        file_data = csvUti._read_file(f_path)
                        
                        for data in file_data:
                            if data['so_tien'] <= 0:
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            vals={}
                            account_id = False
                            sql = '''
                                select id from account_account where code='%s' limit 1
                            '''%(data['ma_chi_nhanh'])
                            cr.execute(sql)
                            chinhanh_ids = cr.fetchone()
                            if not chinhanh_ids:
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy chi nhánh')
                            
                            sql = '''
                                select id,bai_giaoca_id,account_ht_id,cmnd,giayphep_kinhdoanh,taixe,nhadautu,nhanvienvanphong
                                    from res_partner where ma_doi_tuong='%s' limit 1
                            '''%(data['ma_doi_tuong'])
                            cr.execute(sql)
                            partner = cr.dictfetchone()
                            if not partner:
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy đối tượng')
                            partner_id = partner and partner['id'] or False
                            bai_giaoca_id = partner and partner['bai_giaoca_id'] or False
                            
                            loai_doituong=''
                            if partner['taixe']==True:
                                loai_doituong='taixe'
                                account_id = partner and partner['account_ht_id'] or False
                            if partner['nhanvienvanphong']==True:
                                loai_doituong='nhanvienvanphong'
                                account_id = partner and partner['account_ht_id'] or False
                            if partner['nhadautu']==True:
                                loai_doituong='nhadautu'
                                sql = '''
                                    select nhom_chinhanh_id from chi_nhanh_line where chinhanh_id=%s and partner_id=%s
                                '''%(chinhanh_ids[0],partner_id)
                                cr.execute(sql)
                                account_ids = [r[0] for r in cr.fetchall()]
                                account_id = account_ids and account_ids[0] or False
                                vals.update({'cmnd': partner['cmnd'],'giayphep_kinhdoanh': partner['giayphep_kinhdoanh'],'chinhanh_ndt_id':chinhanh_ids[0]})
                                
                            journal_ids = self.pool.get('account.journal').search(cr, uid, [('code','=','TG')])
                            
                            bsx = data['bien_so_xe']
                            sql = ''' select id from bien_so_xe where name='%s' '''%(bsx)
                            cr.execute(sql)
                            bien_so_xe_ids = cr.fetchone()
                            if bsx and not bien_so_xe_ids:
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy biển số xe')
                            
                            date_invoice=datetime.strptime(data['ngay_giao_dich'],'%d/%m/%Y').strftime('%Y-%m-%d')
                            
                            vals.update({
                                'mlg_type': 'thu_phi_thuong_hieu',
                                'type': 'out_invoice',
                                'account_id': account_id,
                                'chinhanh_id': chinhanh_ids and chinhanh_ids[0] or False,
                                'loai_doituong': loai_doituong,
                                'partner_id': partner_id,
                                'date_invoice': date_invoice,
                                'so_hop_dong': data['so_hop_dong'],
                                'so_tien': data['so_tien'],
                                'dien_giai': data['dien_giai'],
                                'journal_id': journal_ids and journal_ids[0] or False,
                                'bai_giaoca_id': bai_giaoca_id,
                                'bien_so_xe_id': bien_so_xe_ids and bien_so_xe_ids[0] or False,
                            })
                            invoice_vals = invoice_obj.onchange_dien_giai_st(cr, uid, [], data['dien_giai'], data['so_tien'], journal_ids and journal_ids[0] or False, context)['value']
                            vals.update(invoice_vals)
                            invoice_id = invoice_obj.create(cr, uid, vals)
                            wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+f_path.split('/')[-1],
                            'loai_giaodich': 'Thu phí thương hiệu (HTKD)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        error_path = dir_path.name+'/Error/'
                        csvUti._moveFiles([f_path],error_path)
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,time.strftime('%Y-%m-%d %H:%M:%S'),1,time.strftime('%Y-%m-%d %H:%M:%S'),time.strftime('%Y-%m-%d %H:%M:%S'),
                             error_path+f_path.split('/')[-1],'Thu phí thương hiệu (HTKD)','Thu','Nhập','Tự động','Lỗi',''
                        )
                        cr.execute(sql)
                        raise osv.except_osv(_('Warning!'), str(e))
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def import_phaithu_tragopxe_htkd(self, cr, uid, context=None):
        import_obj = self.pool.get('cauhinh.thumuc.import.tudong')
        invoice_obj = self.pool.get('account.invoice')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        wf_service = netsvc.LocalService("workflow")
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','tra_gop_xe_htkd')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+'/Importing/'
                done_path = dir_path.name+'/Done/'
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    try:
                        file_data = csvUti._read_file(f_path)
                        
                        for data in file_data:
                            if data['so_tien'] <= 0:
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            vals={}
                            account_id = False
                            sql = '''
                                select id from account_account where code='%s' limit 1
                            '''%(data['ma_chi_nhanh'])
                            cr.execute(sql)
                            chinhanh_ids = cr.fetchone()
                            if not chinhanh_ids:
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy chi nhánh')
                            
                            sql = '''
                                select id,bai_giaoca_id,account_ht_id,cmnd,giayphep_kinhdoanh,taixe,nhadautu,nhanvienvanphong
                                    from res_partner where ma_doi_tuong='%s' limit 1
                            '''%(data['ma_doi_tuong'])
                            cr.execute(sql)
                            partner = cr.dictfetchone()
                            if not partner:
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy đối tượng')
                            partner_id = partner and partner['id'] or False
                            bai_giaoca_id = partner and partner['bai_giaoca_id'] or False
                            
                            loai_doituong=''
                            if partner['taixe']==True:
                                loai_doituong='taixe'
                                account_id = partner and partner['account_ht_id'] or False
                            if partner['nhanvienvanphong']==True:
                                loai_doituong='nhanvienvanphong'
                                account_id = partner and partner['account_ht_id'] or False
                            if partner['nhadautu']==True:
                                loai_doituong='nhadautu'
                                sql = '''
                                    select nhom_chinhanh_id from chi_nhanh_line where chinhanh_id=%s and partner_id=%s
                                '''%(chinhanh_ids[0],partner_id)
                                cr.execute(sql)
                                account_ids = [r[0] for r in cr.fetchall()]
                                account_id = account_ids and account_ids[0] or False
                                vals.update({'cmnd': partner['cmnd'],'giayphep_kinhdoanh': partner['giayphep_kinhdoanh'],'chinhanh_ndt_id':chinhanh_ids[0]})
                                
                            journal_ids = self.pool.get('account.journal').search(cr, uid, [('code','=','TG')])
                            
                            bsx = data['bien_so_xe']
                            sql = ''' select id from bien_so_xe where name='%s' '''%(bsx)
                            cr.execute(sql)
                            bien_so_xe_ids = cr.fetchone()
                            if bsx and not bien_so_xe_ids:
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy biển số xe')

                            date_invoice=datetime.strptime(data['ngay_phat_sinh'],'%d/%m/%Y').strftime('%Y-%m-%d')
                            
                            donvithuhuong = []
                            if data['don_vi_thu_huong']:
                                sql = '''
                                    select id from res_partner where ma_doi_tuong='%s'
                                '''%(data['don_vi_thu_huong'])
                                cr.execute(sql)
                                donvithuhuong = cr.fetchone()
                            
                            vals.update({
                                'mlg_type': 'tra_gop_xe',
                                'type': 'out_invoice',
                                'account_id': account_id,
                                'chinhanh_id': chinhanh_ids and chinhanh_ids[0] or False,
                                'loai_doituong': loai_doituong,
                                'partner_id': partner_id,
                                'date_invoice': date_invoice,
                                'so_hop_dong': data['so_hop_dong'],
                                'so_tien': data['so_tien'],
                                'dien_giai': data['dien_giai'],
                                'journal_id': journal_ids and journal_ids[0] or False,
                                'bai_giaoca_id': bai_giaoca_id,
                                'bien_so_xe_id': bien_so_xe_ids and bien_so_xe_ids[0] or False,
                                'thu_cho_doituong_id': donvithuhuong and donvithuhuong[0] or False,
                            })
                            invoice_vals = invoice_obj.onchange_dien_giai_st(cr, uid, [], data['dien_giai'], data['so_tien'], journal_ids and journal_ids[0] or False, context)['value']
                            vals.update(invoice_vals)
                            invoice_id = invoice_obj.create(cr, uid, vals)
                            wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+f_path.split('/')[-1],
                            'loai_giaodich': 'Trả góp xe (HTKD)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        error_path = dir_path.name+'/Error/'
                        csvUti._moveFiles([f_path],error_path)
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,time.strftime('%Y-%m-%d %H:%M:%S'),1,time.strftime('%Y-%m-%d %H:%M:%S'),time.strftime('%Y-%m-%d %H:%M:%S'),
                             error_path+f_path.split('/')[-1],'Trả góp xe (HTKD)','Thu','Nhập','Tự động','Lỗi',''
                        )
                        cr.execute(sql)
                        raise osv.except_osv(_('Warning!'), str(e))
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def import_phaithu_thuphithuonghieu_shift(self, cr, uid, context=None):
        import_obj = self.pool.get('cauhinh.thumuc.import.tudong')
        invoice_obj = self.pool.get('account.invoice')
        voucher_obj = self.pool.get('account.voucher')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        wf_service = netsvc.LocalService("workflow")
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','thu_phi_thuong_hieu_shift')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+'/Importing/'
                done_path = dir_path.name+'/Done/'
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for data in file_data:
                            
                            bsx = data['bien_so_xe']
                            sql = ''' select id from bien_so_xe where name='%s' '''%(bsx)
                            cr.execute(sql)
                            bien_so_xe_ids = cr.fetchone()
                            if bsx and not bien_so_xe_ids:
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy biển số xe')
                                
                            sql = '''
                                select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                    from account_invoice where chinhanh_id in (select id from account_account where code='%s')
                                        and partner_id in (select id from res_partner where ma_doi_tuong='%s') and type='out_invoice'
                                        and mlg_type='thu_phi_thuong_hieu' and state='open' 
                            '''%(data['ma_chi_nhanh'],data['ma_doi_tuong'])
                            if data['so_hop_dong']:
                                sql += '''
                                    and so_hop_dong='%s' 
                                '''%(data['so_hop_dong'])
                            if bsx:
                                sql += '''
                                    and bien_so_xe_id=%s 
                                '''%(bien_so_xe_ids[0])
                            sql += '''
                                order by date_invoice
                            '''
                            cr.execute(sql)
                            sotiendathu = float(data['so_tien_da_thu'])
                            if sotiendathu <= 0:
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            for line in cr.dictfetchall():
                                if line['residual']>sotiendathu:
                                    amount = sotiendathu
                                else:
                                    amount = line['residual']
                                    sotiendathu = sotiendathu-line['residual']
                                if not amount:
                                    break
                                journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','cash'),('chinhanh_id','=',line['chinhanh_id'])])
                                
                                ngay_thanh_toan=datetime.strptime(data['ngay_thanh_toan'],'%d/%m/%Y').strftime('%Y-%m-%d')
                                
                                vals = {
                                    'amount': amount,
                                    'partner_id': line['partner_id'],
                                    'reference': line['name'],
                                    'bai_giaoca_id': line['bai_giaoca_id'],
                                    'mlg_type': line['mlg_type'],
                                    'type': 'receipt',
                                    'chinhanh_id': line['chinhanh_id'],
                                    'journal_id': journal_ids[0],
                                    'date': ngay_thanh_toan,
                                }
                                
                                context = {
                                    'payment_expected_currency': line['currency_id'],
                                    'default_partner_id': line['partner_id'],
                                    'default_amount': amount,
                                    'default_reference': line['name'],
                                    'default_bai_giaoca_id': line['bai_giaoca_id'],
                                    'default_mlg_type': line['mlg_type'],
                                    'close_after_process': True,
                                    'invoice_type': line['type'],
                                    'invoice_id': line['id'],
                                    'default_type': 'receipt',
                                    'default_chinhanh_id': line['chinhanh_id'],
                                    'type': 'receipt',
                                }
                                vals_onchange_partner = voucher_obj.onchange_partner_id(cr, uid, [],line['partner_id'],journal_ids[0],amount,line['currency_id'],'receipt',ngay_thanh_toan,context)['value']
                                vals.update(vals_onchange_partner)
                                vals.update(
                                    voucher_obj.onchange_journal(cr, uid, [],journal_ids[0],vals_onchange_partner['line_cr_ids'],False,line['partner_id'],ngay_thanh_toan,amount,'receipt',line['company_id'],context)['value']
                                )
                                line_cr_ids = []
                                for l in vals['line_cr_ids']:
                                    line_cr_ids.append((0,0,l))
                                vals.update({'line_cr_ids':line_cr_ids})
                                voucher_id = voucher_obj.create(cr, uid, vals)
                                voucher_obj.button_proforma_voucher(cr, uid, [voucher_id])
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+f_path.split('/')[-1],
                            'loai_giaodich': 'Thu phí thương hiệu (SHIFT)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        error_path = dir_path.name+'/Error/'
                        csvUti._moveFiles([f_path],error_path)
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,time.strftime('%Y-%m-%d %H:%M:%S'),1,time.strftime('%Y-%m-%d %H:%M:%S'),time.strftime('%Y-%m-%d %H:%M:%S'),
                             error_path+f_path.split('/')[-1],'Thu phí thương hiệu (SHIFT)','Thu','Nhập','Tự động','Lỗi',''
                        )
                        cr.execute(sql)
                        raise osv.except_osv(_('Warning!'), str(e))
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def import_phaithu_tragopxe_shift(self, cr, uid, context=None):
        import_obj = self.pool.get('cauhinh.thumuc.import.tudong')
        invoice_obj = self.pool.get('account.invoice')
        voucher_obj = self.pool.get('account.voucher')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        wf_service = netsvc.LocalService("workflow")
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','tra_gop_xe_shift')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+'/Importing/'
                done_path = dir_path.name+'/Done/'
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for data in file_data:
                                
                            bsx = data['bien_so_xe']
                            sql = ''' select id from bien_so_xe where name='%s' '''%(bsx)
                            cr.execute(sql)
                            bien_so_xe_ids = cr.fetchone()
                            if bsx and not bien_so_xe_ids:
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy biển số xe')

                            sql = '''
                                select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                    from account_invoice where chinhanh_id in (select id from account_account where code='%s')
                                        and partner_id in (select id from res_partner where ma_doi_tuong='%s') and type='out_invoice'
                                        and mlg_type='tra_gop_xe' and state='open' 
                            '''%(data['ma_chi_nhanh'],data['ma_doi_tuong'])
                            if data['so_hop_dong']:
                                sql += '''
                                    and so_hop_dong='%s' 
                                '''%(data['so_hop_dong'])
                            if bsx:
                                sql += '''
                                    and bien_so_xe_id=%s 
                                '''%(bien_so_xe_ids[0])
                            sql += '''
                                order by date_invoice
                            '''
                            cr.execute(sql)
                            sotiendathu = float(data['so_tien_da_thu'])
                            if sotiendathu <= 0:
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            for line in cr.dictfetchall():
                                if line['residual']>sotiendathu:
                                    amount = sotiendathu
                                else:
                                    amount = line['residual']
                                    sotiendathu = sotiendathu-line['residual']
                                if not amount:
                                    break
                                journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','cash'),('chinhanh_id','=',line['chinhanh_id'])])
                                
                                ngay_thanh_toan=datetime.strptime(data['ngay_thanh_toan'],'%d/%m/%Y').strftime('%Y-%m-%d')
                                
                                vals = {
                                    'amount': amount,
                                    'partner_id': line['partner_id'],
                                    'reference': line['name'],
                                    'bai_giaoca_id': line['bai_giaoca_id'],
                                    'mlg_type': line['mlg_type'],
                                    'type': 'receipt',
                                    'chinhanh_id': line['chinhanh_id'],
                                    'journal_id': journal_ids[0],
                                    'date': ngay_thanh_toan,
                                }
                                
                                context = {
                                    'payment_expected_currency': line['currency_id'],
                                    'default_partner_id': line['partner_id'],
                                    'default_amount': amount,
                                    'default_reference': line['name'],
                                    'default_bai_giaoca_id': line['bai_giaoca_id'],
                                    'default_mlg_type': line['mlg_type'],
                                    'close_after_process': True,
                                    'invoice_type': line['type'],
                                    'invoice_id': line['id'],
                                    'default_type': 'receipt',
                                    'default_chinhanh_id': line['chinhanh_id'],
                                    'type': 'receipt',
                                }
                                vals_onchange_partner = voucher_obj.onchange_partner_id(cr, uid, [],line['partner_id'],journal_ids[0],amount,line['currency_id'],'receipt',ngay_thanh_toan,context)['value']
                                vals.update(vals_onchange_partner)
                                vals.update(
                                    voucher_obj.onchange_journal(cr, uid, [],journal_ids[0],vals_onchange_partner['line_cr_ids'],False,line['partner_id'],ngay_thanh_toan,amount,'receipt',line['company_id'],context)['value']
                                )
                                line_cr_ids = []
                                for l in vals['line_cr_ids']:
                                    line_cr_ids.append((0,0,l))
                                vals.update({'line_cr_ids':line_cr_ids})
                                voucher_id = voucher_obj.create(cr, uid, vals)
                                voucher_obj.button_proforma_voucher(cr, uid, [voucher_id])
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+f_path.split('/')[-1],
                            'loai_giaodich': 'Trả góp xe (SHIFT)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        error_path = dir_path.name+'/Error/'
                        csvUti._moveFiles([f_path],error_path)
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,time.strftime('%Y-%m-%d %H:%M:%S'),1,time.strftime('%Y-%m-%d %H:%M:%S'),time.strftime('%Y-%m-%d %H:%M:%S'),
                             error_path+f_path.split('/')[-1],'Trả góp xe (SHIFT)','Thu','Nhập','Tự động','Lỗi',''
                        )
                        cr.execute(sql)
                        raise osv.except_osv(_('Warning!'), str(e))
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def import_phaithu_phatvipham_histaff(self, cr, uid, context=None):
        import_obj = self.pool.get('cauhinh.thumuc.import.tudong')
        invoice_obj = self.pool.get('account.invoice')
        voucher_obj = self.pool.get('account.voucher')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        wf_service = netsvc.LocalService("workflow")
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','phat_vi_pham')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+'/Importing/'
                done_path = dir_path.name+'/Done/'
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for data in file_data:
                            sql = '''
                                select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                    from account_invoice where chinhanh_id in (select id from account_account where code='%s')
                                        and partner_id in (select id from res_partner where ma_doi_tuong='%s') and type='out_invoice'
                                        and mlg_type='phat_vi_pham' and state='open'
                                    order by date_invoice
                            '''%(data['ma_chi_nhanh'],data['ma_doi_tuong'])
                            cr.execute(sql)
                            sotiendathu = float(data['so_tien_da_thu'])
                            if sotiendathu <= 0:
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            for line in cr.dictfetchall():
                                if line['residual']>sotiendathu:
                                    amount = sotiendathu
                                else:
                                    amount = line['residual']
                                    sotiendathu = sotiendathu-line['residual']
                                if not amount:
                                    break
                                journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','cash'),('chinhanh_id','=',line['chinhanh_id'])])
                                
                                ngay_thanh_toan=datetime.strptime(data['ngay_thanh_toan'],'%d/%m/%Y').strftime('%Y-%m-%d')
                                
                                vals = {
                                    'amount': amount,
                                    'partner_id': line['partner_id'],
                                    'reference': line['name'],
                                    'bai_giaoca_id': line['bai_giaoca_id'],
                                    'mlg_type': line['mlg_type'],
                                    'type': 'receipt',
                                    'chinhanh_id': line['chinhanh_id'],
                                    'journal_id': journal_ids[0],
                                    'date': ngay_thanh_toan,
                                }
                                
                                context = {
                                    'payment_expected_currency': line['currency_id'],
                                    'default_partner_id': line['partner_id'],
                                    'default_amount': amount,
                                    'default_reference': line['name'],
                                    'default_bai_giaoca_id': line['bai_giaoca_id'],
                                    'default_mlg_type': line['mlg_type'],
                                    'close_after_process': True,
                                    'invoice_type': line['type'],
                                    'invoice_id': line['id'],
                                    'default_type': 'receipt',
                                    'default_chinhanh_id': line['chinhanh_id'],
                                    'type': 'receipt',
                                }
                                vals_onchange_partner = voucher_obj.onchange_partner_id(cr, uid, [],line['partner_id'],journal_ids[0],amount,line['currency_id'],'receipt',ngay_thanh_toan,context)['value']
                                vals.update(vals_onchange_partner)
                                vals.update(
                                    voucher_obj.onchange_journal(cr, uid, [],journal_ids[0],vals_onchange_partner['line_cr_ids'],False,line['partner_id'],ngay_thanh_toan,amount,'receipt',line['company_id'],context)['value']
                                )
                                line_cr_ids = []
                                for l in vals['line_cr_ids']:
                                    line_cr_ids.append((0,0,l))
                                vals.update({'line_cr_ids':line_cr_ids})
                                voucher_id = voucher_obj.create(cr, uid, vals)
                                voucher_obj.button_proforma_voucher(cr, uid, [voucher_id])
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+f_path.split('/')[-1],
                            'loai_giaodich': 'Phạt vi phạm (HISTAFF)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        error_path = dir_path.name+'/Error/'
                        csvUti._moveFiles([f_path],error_path)
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,time.strftime('%Y-%m-%d %H:%M:%S'),1,time.strftime('%Y-%m-%d %H:%M:%S'),time.strftime('%Y-%m-%d %H:%M:%S'),
                             error_path+f_path.split('/')[-1],'Phạt vi phạm (HISTAFF)','Thu','Nhập','Tự động','Lỗi',''
                        )
                        cr.execute(sql)
                        raise osv.except_osv(_('Warning!'), str(e))
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def import_phaithu_tamung_histaff(self, cr, uid, context=None):
        import_obj = self.pool.get('cauhinh.thumuc.import.tudong')
        invoice_obj = self.pool.get('account.invoice')
        voucher_obj = self.pool.get('account.voucher')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        wf_service = netsvc.LocalService("workflow")
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','hoan_tam_ung')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+'/Importing/'
                done_path = dir_path.name+'/Done/'
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for data in file_data:
                            sql = '''
                                select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                    from account_invoice where chinhanh_id in (select id from account_account where code='%s')
                                        and partner_id in (select id from res_partner where ma_doi_tuong='%s') and type='out_invoice'
                                        and mlg_type='hoan_tam_ung' and state='open'
                                    order by date_invoice
                            '''%(data['ma_chi_nhanh'],data['ma_doi_tuong'])
                            cr.execute(sql)
                            sotiendathu = float(data['so_tien_da_thu'])
                            if sotiendathu <= 0:
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            for line in cr.dictfetchall():
                                if line['residual']>sotiendathu:
                                    amount = sotiendathu
                                else:
                                    amount = line['residual']
                                    sotiendathu = sotiendathu-line['residual']
                                if not amount:
                                    break
                                journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','cash'),('chinhanh_id','=',line['chinhanh_id'])])
                                
                                ngay_thanh_toan=datetime.strptime(data['ngay_thanh_toan'],'%d/%m/%Y').strftime('%Y-%m-%d')
                                
                                vals = {
                                    'amount': amount,
                                    'partner_id': line['partner_id'],
                                    'reference': line['name'],
                                    'bai_giaoca_id': line['bai_giaoca_id'],
                                    'mlg_type': line['mlg_type'],
                                    'type': 'receipt',
                                    'chinhanh_id': line['chinhanh_id'],
                                    'journal_id': journal_ids[0],
                                    'date': ngay_thanh_toan,
                                }
                                
                                context = {
                                    'payment_expected_currency': line['currency_id'],
                                    'default_partner_id': line['partner_id'],
                                    'default_amount': amount,
                                    'default_reference': line['name'],
                                    'default_bai_giaoca_id': line['bai_giaoca_id'],
                                    'default_mlg_type': line['mlg_type'],
                                    'close_after_process': True,
                                    'invoice_type': line['type'],
                                    'invoice_id': line['id'],
                                    'default_type': 'receipt',
                                    'default_chinhanh_id': line['chinhanh_id'],
                                    'type': 'receipt',
                                }
                                vals_onchange_partner = voucher_obj.onchange_partner_id(cr, uid, [],line['partner_id'],journal_ids[0],amount,line['currency_id'],'receipt',ngay_thanh_toan,context)['value']
                                vals.update(vals_onchange_partner)
                                vals.update(
                                    voucher_obj.onchange_journal(cr, uid, [],journal_ids[0],vals_onchange_partner['line_cr_ids'],False,line['partner_id'],ngay_thanh_toan,amount,'receipt',line['company_id'],context)['value']
                                )
                                line_cr_ids = []
                                for l in vals['line_cr_ids']:
                                    line_cr_ids.append((0,0,l))
                                vals.update({'line_cr_ids':line_cr_ids})
                                voucher_id = voucher_obj.create(cr, uid, vals)
                                voucher_obj.button_proforma_voucher(cr, uid, [voucher_id])
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+f_path.split('/')[-1],
                            'loai_giaodich': 'Phải thu tạm ứng (HISTAFF)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        error_path = dir_path.name+'/Error/'
                        csvUti._moveFiles([f_path],error_path)
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,time.strftime('%Y-%m-%d %H:%M:%S'),1,time.strftime('%Y-%m-%d %H:%M:%S'),time.strftime('%Y-%m-%d %H:%M:%S'),
                             error_path+f_path.split('/')[-1],'Phải thu tạm ứng (HISTAFF)','Thu','Nhập','Tự động','Lỗi',''
                        )
                        cr.execute(sql)
                        raise osv.except_osv(_('Warning!'), str(e))
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def import_phaithu_kyquy_histaff(self, cr, uid, context=None):
        import_obj = self.pool.get('cauhinh.thumuc.import.tudong')
        kyquy_obj = self.pool.get('thu.ky.quy')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','phai_thu_ky_quy')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+'/Importing/'
                done_path = dir_path.name+'/Done/'
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for data in file_data:
                            if data['so_tien_da_thu'] <= 0:
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            sql = '''
                                select id from account_account where code='%s' limit 1
                            '''%(data['ma_chi_nhanh'])
                            cr.execute(sql)
                            chinhanh_ids = cr.fetchone()
                            if not chinhanh_ids:
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy chi nhánh')

                            sql = '''
                                select id from thu_ky_quy where partner_id in (select id from res_partner where ma_doi_tuong='%s')
                                    and chinhanh_id=%s and state='draft'
                            '''%(data['ma_doi_tuong'],chinhanh_ids[0])
                            cr.execute(sql)
                            for kyquy in cr.dictfetchall():
                                cr.execute('update thu_ky_quy set so_tien=%s where id=%s',(data['so_tien_da_thu'],kyquy['id'],))
                                kyquy_obj.bt_thu(cr, uid, kyquy['id'])
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+f_path.split('/')[-1],
                            'loai_giaodich': 'Phải thu ký quỹ (HISTAFF)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        error_path = dir_path.name+'/Error/'
                        csvUti._moveFiles([f_path],error_path)
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,time.strftime('%Y-%m-%d %H:%M:%S'),1,time.strftime('%Y-%m-%d %H:%M:%S'),time.strftime('%Y-%m-%d %H:%M:%S'),
                             error_path+f_path.split('/')[-1],'Phải thu ký quỹ (HISTAFF)','Thu','Nhập','Tự động','Lỗi',''
                        )
                        cr.execute(sql)
                        raise osv.except_osv(_('Warning!'), str(e))
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def import_phaithu_fustion_oracle(self, cr, uid, context=None):
        import_obj = self.pool.get('cauhinh.thumuc.import.tudong')
        invoice_obj = self.pool.get('account.invoice')
        voucher_obj = self.pool.get('account.voucher')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        wf_service = netsvc.LocalService("workflow")
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','fustion_phaithu')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+'/Importing/'
                done_path = dir_path.name+'/Done/'
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for data in file_data:
                            if data['ACCTD_AMOUNT'] <= 0:
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            sql = '''
                                select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                    from account_invoice where name='%s' and state='open' and type='out_invoice'
                                    order by date_invoice
                            '''%(data['REQUEST_REF_NUMBER'])
                            cr.execute(sql)
                            invoices = cr.dictfetchall()
                            if not invoices:
                                sql = '''
                                    select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                        from account_invoice where so_hoa_don='%s' and state='open' and type='out_invoice'
                                        order by date_invoice
                                '''%(data['REQUEST_REF_NUMBER'])
                                cr.execute(sql)
                                invoices = cr.dictfetchall()
                            if not invoices:
                                sql = '''
                                    select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                        from account_invoice where bien_so_xe_id in (select id from bien_so_xe where name='%s') and state='open' and type='out_invoice'
                                        order by date_invoice
                                '''%(data['REQUEST_REF_NUMBER'])
                                cr.execute(sql)
                                invoices = cr.dictfetchall()
                            if not invoices:
                                sql = '''
                                    select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                        from account_invoice where ma_bang_chiettinh_chiphi_sua='%s' and state='open' and type='out_invoice'
                                        order by date_invoice
                                '''%(data['REQUEST_REF_NUMBER'])
                                cr.execute(sql)
                                invoices = cr.dictfetchall()
                            if not invoices:
                                sql = '''
                                    select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                        from account_invoice where so_hop_dong='%s' and state='open' and type='out_invoice'
                                        order by date_invoice
                                '''%(data['REQUEST_REF_NUMBER'])
                                cr.execute(sql)
                                invoices = cr.dictfetchall()    
                            if not invoices:
                                raise osv.except_osv(_('Warning!'), 'Không tìm thấy công nợ')
                            
                            sotiendathu = float(data['ACCTD_AMOUNT'])
                            for invoice in invoices:
                                if invoice['residual']>sotiendathu:
                                    amount = sotiendathu
                                else:
                                    amount = invoice['residual']
                                    
                                if not amount or sotiendathu<=0:
                                    break
                                
                                sql='''
                                    update account_invoice set fusion_id='%s' where id=%s
                                '''%(data['TRANSACTION_NUMBER'],invoice['id'])
                                cr.execute(sql)
                                journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','cash'),('chinhanh_id','=',invoice['chinhanh_id'])])
                                
                                ngay_thanh_toan=datetime.strptime(data['GL_DATE'],'%d/%m/%Y').strftime('%Y-%m-%d')
                                
                                vals = {
                                    'amount': amount,
                                    'partner_id': invoice['partner_id'],
                                    'reference': invoice['name'],
                                    'bai_giaoca_id': invoice['bai_giaoca_id'],
                                    'mlg_type': invoice['mlg_type'],
                                    'type': 'receipt',
                                    'chinhanh_id': invoice['chinhanh_id'],
                                    'journal_id': journal_ids[0],
                                    'date': ngay_thanh_toan,
                                }
                                
                                context = {
                                    'payment_expected_currency': invoice['currency_id'],
                                    'default_partner_id': invoice['partner_id'],
                                    'default_amount': amount,
                                    'default_reference': invoice['name'],
                                    'default_bai_giaoca_id': invoice['bai_giaoca_id'],
                                    'default_mlg_type': invoice['mlg_type'],
                                    'close_after_process': True,
                                    'invoice_type': invoice['type'],
                                    'invoice_id': invoice['id'],
                                    'default_type': 'receipt',
                                    'default_chinhanh_id': invoice['chinhanh_id'],
                                    'type': 'receipt',
                                }
                                vals_onchange_partner = voucher_obj.onchange_partner_id(cr, uid, [],invoice['partner_id'],journal_ids[0],amount,invoice['currency_id'],'receipt',ngay_thanh_toan,context)['value']
                                vals.update(vals_onchange_partner)
                                vals.update(
                                    voucher_obj.onchange_journal(cr, uid, [],journal_ids[0],vals_onchange_partner['line_cr_ids'],False,invoice['partner_id'],ngay_thanh_toan,amount,'receipt',invoice['company_id'],context)['value']
                                )
                                line_cr_ids = []
                                for l in vals['line_cr_ids']:
                                    line_cr_ids.append((0,0,l))
                                vals.update({'line_cr_ids':line_cr_ids})
                                voucher_id = voucher_obj.create(cr, uid, vals)
                                voucher_obj.button_proforma_voucher(cr, uid, [voucher_id])
                                
                                sotiendathu = sotiendathu - amount
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+f_path.split('/')[-1],
                            'loai_giaodich': 'Fustion (ORACLE)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        error_path = dir_path.name+'/Error/'
                        csvUti._moveFiles([f_path],error_path)
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,time.strftime('%Y-%m-%d %H:%M:%S'),1,time.strftime('%Y-%m-%d %H:%M:%S'),time.strftime('%Y-%m-%d %H:%M:%S'),
                             error_path+f_path.split('/')[-1],'Fustion (ORACLE)','Thu','Nhập','Tự động','Lỗi',''
                        )
                        cr.execute(sql)
                        raise osv.except_osv(_('Warning!'), str(e))
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def import_phaitra_fustion_oracle(self, cr, uid, context=None):
        import_obj = self.pool.get('cauhinh.thumuc.import.tudong')
        invoice_obj = self.pool.get('account.invoice')
        voucher_obj = self.pool.get('account.voucher')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        wf_service = netsvc.LocalService("workflow")
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','fustion_phaitra')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+'/Importing/'
                done_path = dir_path.name+'/Done/'
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for data in file_data:
                            if data['ACCTD_AMOUNT'] <= 0:
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            sql = '''
                                select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                    from account_invoice where name='%s' and state='open'
                                    order by date_invoice
                            '''%(data['REQUEST_REF_NUMBER'])
                            cr.execute(sql)
                            invoices = cr.dictfetchall()
                            if not invoices:
                                sql = '''
                                    select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                        from account_invoice where so_hoa_don='%s' and state='open' and type='in_invoice'
                                        order by date_invoice
                                '''%(data['REQUEST_REF_NUMBER'])
                                cr.execute(sql)
                                invoices = cr.dictfetchall()
                            if not invoices:
                                sql = '''
                                    select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                        from account_invoice where bien_so_xe_id in (select id from bien_so_xe where name='%s') and state='open' and type='in_invoice'
                                        order by date_invoice
                                '''%(data['REQUEST_REF_NUMBER'])
                                cr.execute(sql)
                                invoices = cr.dictfetchall()
                            if not invoices:
                                sql = '''
                                    select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                        from account_invoice where ma_bang_chiettinh_chiphi_sua='%s' and state='open' and type='in_invoice'
                                        order by date_invoice
                                '''%(data['REQUEST_REF_NUMBER'])
                                cr.execute(sql)
                                invoices = cr.dictfetchall()
                            if not invoices:
                                sql = '''
                                    select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                        from account_invoice where so_hop_dong='%s' and state='open' and type='in_invoice'
                                        order by date_invoice
                                '''%(data['REQUEST_REF_NUMBER'])
                                cr.execute(sql)
                                invoices = cr.dictfetchall()    
                            if not invoices:
                                raise osv.except_osv(_('Warning!'), 'Không tìm thấy công nợ')
                            
                            sotiendathu = float(data['ACCTD_AMOUNT'])
                            for invoice in invoices:
                                if invoice['residual']>sotiendathu:
                                    amount = sotiendathu
                                else:
                                    amount = invoice['residual']
                                if not amount or sotiendathu<=0:
                                    break
                                sql='''
                                    update account_invoice set fusion_id='%s' where id=%s
                                '''%(data['TRANSACTION_NUMBER'],invoice['id'])
                                cr.execute(sql)
                                journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','cash'),('chinhanh_id','=',invoice['chinhanh_id'])])
                                
                                ngay_thanh_toan=datetime.strptime(data['GL_DATE'],'%d/%m/%Y').strftime('%Y-%m-%d')
                                
                                vals = {
                                    'amount': amount,
                                    'partner_id': invoice['partner_id'],
                                    'reference': invoice['name'],
                                    'bai_giaoca_id': invoice['bai_giaoca_id'],
                                    'mlg_type': invoice['mlg_type'],
                                    'type': 'payment',
                                    'chinhanh_id': invoice['chinhanh_id'],
                                    'journal_id': journal_ids[0],
                                    'date': ngay_thanh_toan,
                                }
                                
                                context = {
                                    'payment_expected_currency': invoice['currency_id'],
                                    'default_partner_id': invoice['partner_id'],
                                    'default_amount': amount,
                                    'default_reference': invoice['name'],
                                    'default_bai_giaoca_id': invoice['bai_giaoca_id'],
                                    'default_mlg_type': invoice['mlg_type'],
                                    'close_after_process': True,
                                    'invoice_type': invoice['type'],
                                    'invoice_id': invoice['id'],
                                    'default_type': 'payment',
                                    'default_chinhanh_id': invoice['chinhanh_id'],
                                    'type': 'payment',
                                }
                                vals_onchange_partner = voucher_obj.onchange_partner_id(cr, uid, [],invoice['partner_id'],journal_ids[0],amount,invoice['currency_id'],'payment',ngay_thanh_toan,context)['value']
                                vals.update(vals_onchange_partner)
                                vals.update(
                                    voucher_obj.onchange_journal(cr, uid, [],journal_ids[0],vals_onchange_partner['line_cr_ids'],False,invoice['partner_id'],ngay_thanh_toan,amount,'payment',invoice['company_id'],context)['value']
                                )
                                line_cr_ids = []
                                for l in vals['line_cr_ids']:
                                    line_cr_ids.append((0,0,l))
                                vals.update({'line_cr_ids':line_cr_ids})
                                voucher_id = voucher_obj.create(cr, uid, vals)
                                voucher_obj.button_proforma_voucher(cr, uid, [voucher_id])
                                sotiendathu = sotiendathu - amount
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+f_path.split('/')[-1],
                            'loai_giaodich': 'Fustion (ORACLE)',
                            'thu_tra': 'Trả',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        error_path = dir_path.name+'/Error/'
                        csvUti._moveFiles([f_path],error_path)
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,time.strftime('%Y-%m-%d %H:%M:%S'),1,time.strftime('%Y-%m-%d %H:%M:%S'),time.strftime('%Y-%m-%d %H:%M:%S'),
                             error_path+f_path.split('/')[-1],'Fustion (ORACLE)','Trả','Nhập','Tự động','Lỗi',''
                        )
                        cr.execute(sql)
                        raise osv.except_osv(_('Warning!'), str(e))
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def import_phaitra_chigopxe_htkd(self, cr, uid, context=None):
        import_obj = self.pool.get('cauhinh.thumuc.import.tudong')
        invoice_obj = self.pool.get('account.invoice')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        wf_service = netsvc.LocalService("workflow")
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','chi_ho')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+'/Importing/'
                done_path = dir_path.name+'/Done/'
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for data in file_data:
                            if data['so_tien'] <= 0:
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            vals={}
                            account_id = False
                            sql = '''
                                select id from account_account where code='%s' limit 1
                            '''%(data['ma_chi_nhanh'])
                            cr.execute(sql)
                            chinhanh_ids = cr.fetchone()
                            if not chinhanh_ids:
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy chi nhánh')
                            
                            sql = '''
                                select id,bai_giaoca_id,account_ht_id,cmnd,giayphep_kinhdoanh,taixe,nhadautu,nhanvienvanphong
                                    from res_partner where ma_doi_tuong='%s' limit 1
                            '''%(data['ma_doi_tuong'])
                            cr.execute(sql)
                            partner = cr.dictfetchone()
                            if not partner:
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy đối tượng')
                            partner_id = partner and partner['id'] or False
                            bai_giaoca_id = partner and partner['bai_giaoca_id'] or False
                            
                            loai_doituong=''
                            if partner['taixe']==True:
                                loai_doituong='taixe'
                                account_id = partner and partner['account_ht_id'] or False
                            if partner['nhanvienvanphong']==True:
                                loai_doituong='nhanvienvanphong'
                                account_id = partner and partner['account_ht_id'] or False
                            if partner['nhadautu']==True:
                                loai_doituong='nhadautu'
                                sql = '''
                                    select nhom_chinhanh_id from chi_nhanh_line where chinhanh_id=%s and partner_id=%s
                                '''%(chinhanh_ids[0],partner_id)
                                cr.execute(sql)
                                account_ids = [r[0] for r in cr.fetchall()]
                                account_id = account_ids and account_ids[0] or False
                                vals.update({'cmnd': partner['cmnd'],'giayphep_kinhdoanh': partner['giayphep_kinhdoanh'],'chinhanh_ndt_id':chinhanh_ids[0]})
                                
                            journal_ids = self.pool.get('account.journal').search(cr, uid, [('code','=','TG')])
                            
                            bsx = data['bien_so_xe']
                            sql = ''' select id from bien_so_xe where name='%s' '''%(bsx)
                            cr.execute(sql)
                            bien_so_xe_ids = cr.fetchone()
                            if bsx and not bien_so_xe_ids:
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy biển số xe')
                            
                            date_invoice=datetime.strptime(data['ngay_phat_sinh'],'%d/%m/%Y').strftime('%Y-%m-%d')
                            
                            vals.update({
                                'mlg_type': 'chi_ho',
                                'type': 'in_invoice',
                                'account_id': account_id,
                                'chinhanh_id': chinhanh_ids and chinhanh_ids[0] or False,
                                'loai_doituong': loai_doituong,
                                'partner_id': partner_id,
                                'date_invoice': date_invoice,
                                'so_hop_dong': data['so_hop_dong'],
                                'so_tien': data['so_tien'],
                                'dien_giai': data['dien_giai'],
                                'journal_id': journal_ids and journal_ids[0] or False,
                                'bai_giaoca_id': bai_giaoca_id,
                                'bien_so_xe_id': bien_so_xe_ids and bien_so_xe_ids[0] or False,
                            })
                            invoice_vals = invoice_obj.onchange_dien_giai_st(cr, uid, [], data['dien_giai'], data['so_tien'], journal_ids and journal_ids[0] or False, context)['value']
                            vals.update(invoice_vals)
                            invoice_id = invoice_obj.create(cr, uid, vals)
                            wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+f_path.split('/')[-1],
                            'loai_giaodich': 'Chi góp xe (HTKD)',
                            'thu_tra': 'Trả',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        error_path = dir_path.name+'/Error/'
                        csvUti._moveFiles([f_path],error_path)
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,time.strftime('%Y-%m-%d %H:%M:%S'),1,time.strftime('%Y-%m-%d %H:%M:%S'),time.strftime('%Y-%m-%d %H:%M:%S'),
                             error_path+f_path.split('/')[-1],'Chi góp xe (HTKD)','Trả','Nhập','Tự động','Lỗi',''
                        )
                        cr.execute(sql)
                        raise osv.except_osv(_('Warning!'), str(e))
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
import_congno_tudong()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
