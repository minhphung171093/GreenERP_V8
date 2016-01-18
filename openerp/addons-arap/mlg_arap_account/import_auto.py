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
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

_logger = logging.getLogger(__name__)
IMPORTING = '/importing/'
DONE = '/done/'
ERROR = '/error/'
class import_congno_tudong(osv.osv):
    _name = 'import.congno.tudong'

    _columns = {
        'name': fields.date('Tên', required=True),
    }
    
    def send_mail(self, cr, uid, lead_email, msg_id,context=None):
        mail_message_pool = self.pool.get('mail.message')
        mail_mail = self.pool.get('mail.mail')
        msg = mail_message_pool.browse(cr, SUPERUSER_ID, msg_id, context=context)
        body_html = msg.body
        # email_from: partner-user alias or partner email or mail.message email_from
        if msg.author_id and msg.author_id.user_ids and msg.author_id.user_ids[0].alias_domain and msg.author_id.user_ids[0].alias_name:
            email_from = '%s <%s@%s>' % (msg.author_id.name, msg.author_id.user_ids[0].alias_name, msg.author_id.user_ids[0].alias_domain)
        elif msg.author_id:
            email_from = '%s <%s>' % (msg.author_id.name, msg.author_id.email)
        else:
            email_from = msg.email_from

        references = False
        if msg.parent_id:
            references = msg.parent_id.message_id

        mail_values = {
            'mail_message_id': msg.id,
            'auto_delete': True,
            'body_html': body_html,
            'email_from': email_from,
            'email_to' : lead_email,
            'references': references,
        }
        email_notif_id = mail_mail.create(cr, uid, mail_values, context=context)
        try:
             mail_mail.send(cr, uid, [email_notif_id], context=context)
        except Exception:
            a = 1
        return True
    
    def import_phaithu_thunoxuong_bdsc(self, cr, uid, context=None):
        import_obj = self.pool.get('cauhinh.thumuc.import.tudong')
        invoice_obj = self.pool.get('account.invoice')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        wf_service = netsvc.LocalService("workflow")
        date_now = time.strftime('%Y-%m-%d')
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','thu_no_xuong')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+IMPORTING
                done_path = dir_path.name+DONE
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    seq = False
                    try:
                        file_data = csvUti._read_file(f_path)
                        
                        for seq,data in enumerate(file_data):
                            noidung_loi = ''
                            try:
                                st = float(data['so_tien'])
                            except Exception, e:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không đúng định dạng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                            if float(data['so_tien']) <= 0:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            vals={}
                            account_id = False
                            sql = '''
                                select id from account_account where upper(code)='%s' limit 1
                            '''%(data['ma_chi_nhanh'].upper())
                            cr.execute(sql)
                            chinhanh_ids = cr.fetchone()
                            if not chinhanh_ids:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy chi nhánh'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy chi nhánh')
                            
                            sql = '''
                                select id,bai_giaoca_id,account_ht_id,cmnd,giayphep_kinhdoanh,taixe,nhadautu,nhanvienvanphong,chinhanh_id
                                    from res_partner where upper(ma_doi_tuong)='%s' limit 1
                            '''%(data['ma_doi_tuong'].upper())
                            cr.execute(sql)
                            partner = cr.dictfetchone()
                            if not partner:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy đối tượng')
                            partner_id = partner and partner['id'] or False
                            bai_giaoca_id = partner and partner['bai_giaoca_id'] or False
                            
                            loai_doituong=''
                            if partner['taixe']==True:
                                if chinhanh_ids[0]!=partner['chinhanh_id']:
                                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của đối tượng')
                                loai_doituong='taixe'
                                account_id = partner and partner['account_ht_id'] or False
                            if partner['nhanvienvanphong']==True:
                                if chinhanh_ids[0]!=partner['chinhanh_id']:
                                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của đối tượng')
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
                            sql = ''' select id from bien_so_xe where upper(name)='%s' '''%(bsx.upper())
                            cr.execute(sql)
                            bien_so_xe_ids = cr.fetchone()
                            if bsx and not bien_so_xe_ids:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy biển số xe'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy biển số xe')
                            
                            mx = data['ma_xuong']
                            sql = ''' select id from ma_xuong where upper(code)='%s' '''%(mx.upper())
                            cr.execute(sql)
                            ma_xuong_ids = cr.fetchone()
                            if mx and not ma_xuong_ids:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy mã xưởng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy mã xưởng')
                            
                            if not data['ngay_giao_dich']:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy ngày giao dịch'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy ngày giao dịch')
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
                                'so_tien': float(data['so_tien']),
                                'dien_giai': data['dien_giai'],
                                'journal_id': journal_ids and journal_ids[0] or False,
                                'bai_giaoca_id': bai_giaoca_id,
                                'bien_so_xe_id': bien_so_xe_ids and bien_so_xe_ids[0] or False,
                                'ma_xuong_id': ma_xuong_ids and ma_xuong_ids[0] or False,
                                'loai_giaodich': 'Giao dịch nhập từ BDSC',
                            })
                            invoice_vals = invoice_obj.onchange_dien_giai_st(cr, uid, [], data['dien_giai'], data['so_tien'], journal_ids and journal_ids[0] or False, context)['value']
                            vals.update(invoice_vals)
                            invoice_id = invoice_obj.create(cr, uid, vals)
                            wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+date_now+'/'+f_path.split('/')[-1],
                            'loai_giaodich': 'Thu nợ xưởng (BDSC)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        cr.rollback()
                        if not noidung_loi:
                            noidung_loi = str(e).replace("'","''")
                            if seq:
                                noidung_loi = 'Dòng "%s": '%(seq+2) + noidung_loi
                        error_path = dir_path.name+ERROR
                        csvUti._moveFiles([f_path],error_path)
                        ngay = time.strftime('%Y-%m-%d %H:%M:%S')
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,ngay,1,ngay,ngay,
                             error_path+date_now+'/'+f_path.split('/')[-1],'Thu nợ xưởng (BDSC)','Thu','Nhập','Tự động','Lỗi',noidung_loi
                        )
                        cr.execute(sql)
                        
                        body='''
                            <p>Ngày: %s</p>
                            <p>Tên file: %s</p>
                            <p>Loại giao dịch: %s</p>
                            <p>Ghi chú: %s</p>
                        '''%(ngay,error_path+date_now+'/'+f_path.split('/')[-1],'Thu nợ xưởng (BDSC)',noidung_loi)
                        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID)
                        partner = user.partner_id
                        partner.signup_prepare()
                        post_values = {
                            'subject': 'Lỗi nhập tự động "Thu nợ xưởng (BDSC)"',
                            'body': body,
                            'partner_ids': [],
                            }
                        lead_email = partner.email
                        msg_id = self.pool.get('res.partner').message_post(cr, uid, [partner.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, lead_email, msg_id, context)
                        cr.commit()
#                         raise osv.except_osv(_('Warning!'), str(e))
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
        date_now = time.strftime('%Y-%m-%d')
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','thu_phi_thuong_hieu_htkd')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+IMPORTING
                done_path = dir_path.name+DONE
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    seq = False
                    try:
                        file_data = csvUti._read_file(f_path)
                        
                        for seq,data in enumerate(file_data):
                            noidung_loi = ''
                            try:
                                st = float(data['so_tien'])
                            except Exception, e:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không đúng định dạng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                            if float(data['so_tien']) <= 0:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            vals={}
                            account_id = False
                            sql = '''
                                select id from account_account where upper(code)='%s' limit 1
                            '''%(data['ma_chi_nhanh'].upper())
                            cr.execute(sql)
                            chinhanh_ids = cr.fetchone()
                            if not chinhanh_ids:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy chi nhánh'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy chi nhánh')
                            
                            sql = '''
                                select id,bai_giaoca_id,account_ht_id,cmnd,giayphep_kinhdoanh,taixe,nhadautu,nhanvienvanphong,chinhanh_id
                                    from res_partner where upper(ma_doi_tuong)='%s' limit 1
                            '''%(data['ma_doi_tuong'].upper())
                            cr.execute(sql)
                            partner = cr.dictfetchone()
                            if not partner:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy đối tượng')
                            partner_id = partner and partner['id'] or False
                            bai_giaoca_id = partner and partner['bai_giaoca_id'] or False
                            
                            loai_doituong=''
                            if partner['taixe']==True:
                                if chinhanh_ids[0]!=partner['chinhanh_id']:
                                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của đối tượng')
                                loai_doituong='taixe'
                                account_id = partner and partner['account_ht_id'] or False
                            if partner['nhanvienvanphong']==True:
                                if chinhanh_ids[0]!=partner['chinhanh_id']:
                                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của đối tượng')
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
                            sql = ''' select id from bien_so_xe where upper(name)='%s' '''%(bsx.upper())
                            cr.execute(sql)
                            bien_so_xe_ids = cr.fetchone()
                            if bsx and not bien_so_xe_ids:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy biển số xe'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy biển số xe')
                            
                            if not data['ngay_giao_dich']:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy ngày giao dịch'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy ngày giao dịch')
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
                                'so_tien': float(data['so_tien']),
                                'dien_giai': data['dien_giai'],
                                'journal_id': journal_ids and journal_ids[0] or False,
                                'bai_giaoca_id': bai_giaoca_id,
                                'bien_so_xe_id': bien_so_xe_ids and bien_so_xe_ids[0] or False,
                                'loai_giaodich': 'Giao dịch nhập từ HTKD',
                            })
                            invoice_vals = invoice_obj.onchange_dien_giai_st(cr, uid, [], data['dien_giai'], data['so_tien'], journal_ids and journal_ids[0] or False, context)['value']
                            vals.update(invoice_vals)
                            invoice_id = invoice_obj.create(cr, uid, vals)
                            wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+date_now+'/'+f_path.split('/')[-1],
                            'loai_giaodich': 'Thu phí thương hiệu (HTKD)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        cr.rollback()
                        if not noidung_loi:
                            noidung_loi = str(e).replace("'","''")
                            if seq:
                                noidung_loi = 'Dòng "%s": '%(seq+2) + noidung_loi
                        error_path = dir_path.name+ERROR
                        csvUti._moveFiles([f_path],error_path)
                        ngay = time.strftime('%Y-%m-%d %H:%M:%S')
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,ngay,1,ngay,ngay,
                             error_path+date_now+'/'+f_path.split('/')[-1],'Thu phí thương hiệu (HTKD)','Thu','Nhập','Tự động','Lỗi',noidung_loi
                        )
                        cr.execute(sql)
                        
                        body='''
                            <p>Ngày: %s</p>
                            <p>Tên file: %s</p>
                            <p>Loại giao dịch: %s</p>
                            <p>Ghi chú: %s</p>
                        '''%(ngay,error_path+date_now+'/'+f_path.split('/')[-1],'Thu phí thương hiệu (HTKD)',noidung_loi)
                        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID)
                        partner = user.partner_id
                        partner.signup_prepare()
                        post_values = {
                            'subject': 'Lỗi nhập tự động "Thu phí thương hiệu (HTKD)"',
                            'body': body,
                            'partner_ids': [],
                            }
                        lead_email = partner.email
                        msg_id = self.pool.get('res.partner').message_post(cr, uid, [partner.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, lead_email, msg_id, context)
                        cr.commit()
#                         raise osv.except_osv(_('Warning!'), str(e))
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
        date_now = time.strftime('%Y-%m-%d')
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','tra_gop_xe_htkd')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+IMPORTING
                done_path = dir_path.name+DONE
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    seq = False
                    try:
                        file_data = csvUti._read_file(f_path)
                        
                        for seq,data in enumerate(file_data):
                            noidung_loi=''
                            try:
                                st = float(data['so_tien'])
                            except Exception, e:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không đúng định dạng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                            if float(data['so_tien']) <= 0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            vals={}
                            account_id = False
                            sql = '''
                                select id from account_account where upper(code)='%s' limit 1
                            '''%(data['ma_chi_nhanh'].upper())
                            cr.execute(sql)
                            chinhanh_ids = cr.fetchone()
                            if not chinhanh_ids:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy chi nhánh'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy chi nhánh')
                            
                            sql = '''
                                select id,bai_giaoca_id,account_ht_id,cmnd,giayphep_kinhdoanh,taixe,nhadautu,nhanvienvanphong,chinhanh_id
                                    from res_partner where upper(ma_doi_tuong)='%s' limit 1
                            '''%(data['ma_doi_tuong'].upper())
                            cr.execute(sql)
                            partner = cr.dictfetchone()
                            if not partner:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy đối tượng')
                            partner_id = partner and partner['id'] or False
                            bai_giaoca_id = partner and partner['bai_giaoca_id'] or False
                            
                            loai_doituong=''
                            if partner['taixe']==True:
                                if chinhanh_ids[0]!=partner['chinhanh_id']:
                                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của đối tượng')
                                loai_doituong='taixe'
                                account_id = partner and partner['account_ht_id'] or False
                            if partner['nhanvienvanphong']==True:
                                if chinhanh_ids[0]!=partner['chinhanh_id']:
                                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của đối tượng')
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
                            if not bsx:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy biển số xe trên template'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy biển số xe trên template')
                            sql = ''' select id from bien_so_xe where upper(name)='%s' '''%(bsx.upper())
                            cr.execute(sql)
                            bien_so_xe_ids = cr.fetchone()
                            if bsx and not bien_so_xe_ids:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy biển số xe'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy biển số xe')
                            
                            if not data['ngay_giao_dich']:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy ngày giao dịch'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy ngày giao dịch')
                            date_invoice=datetime.strptime(data['ngay_giao_dich'],'%d/%m/%Y').strftime('%Y-%m-%d')
                            
                            donvithuhuong = []
                            if data['don_vi_thu_huong']:
                                sql = '''
                                    select id from res_partner where upper(ma_doi_tuong)='%s'
                                '''%(data['don_vi_thu_huong'].upper())
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
                                'sotien_lai': data['so_tien_lai'],
                                'so_tien': float(data['so_tien']),
                                'dien_giai': data['dien_giai'],
                                'journal_id': journal_ids and journal_ids[0] or False,
                                'bai_giaoca_id': bai_giaoca_id,
                                'bien_so_xe_id': bien_so_xe_ids and bien_so_xe_ids[0] or False,
                                'thu_cho_doituong_id': donvithuhuong and donvithuhuong[0] or False,
                                'loai_giaodich': 'Giao dịch nhập từ HTKD',
                            })
                            invoice_vals = invoice_obj.onchange_dien_giai_st(cr, uid, [], data['dien_giai'], data['so_tien'], journal_ids and journal_ids[0] or False, context)['value']
                            vals.update(invoice_vals)
                            invoice_id = invoice_obj.create(cr, uid, vals)
                            wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+date_now+'/'+f_path.split('/')[-1],
                            'loai_giaodich': 'Trả góp xe (HTKD)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        cr.rollback()
                        if not noidung_loi:
                            noidung_loi = str(e).replace("'","''")
                            if seq:
                                noidung_loi = 'Dòng "%s": '%(seq+2) + noidung_loi
                        error_path = dir_path.name+ERROR
                        csvUti._moveFiles([f_path],error_path)
                        ngay = time.strftime('%Y-%m-%d %H:%M:%S')
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,ngay,1,ngay,ngay,
                             error_path+date_now+'/'+f_path.split('/')[-1],'Trả góp xe (HTKD)','Thu','Nhập','Tự động','Lỗi',noidung_loi
                        )
                        cr.execute(sql)
                        
                        body='''
                            <p>Ngày: %s</p>
                            <p>Tên file: %s</p>
                            <p>Loại giao dịch: %s</p>
                            <p>Ghi chú: %s</p>
                        '''%(ngay,error_path+date_now+'/'+f_path.split('/')[-1],'Trả góp xe (HTKD)',noidung_loi)
                        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID)
                        partner = user.partner_id
                        partner.signup_prepare()
                        post_values = {
                            'subject': 'Lỗi nhập tự động "Trả góp xe (HTKD)"',
                            'body': body,
                            'partner_ids': [],
                            }
                        lead_email = partner.email
                        msg_id = self.pool.get('res.partner').message_post(cr, uid, [partner.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, lead_email, msg_id, context)
                        cr.commit()
#                         raise osv.except_osv(_('Warning!'), str(e))
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def import_phaithu_nodoanhthu_shift_in(self, cr, uid, context=None):
        import_obj = self.pool.get('cauhinh.thumuc.import.tudong')
        invoice_obj = self.pool.get('account.invoice')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        wf_service = netsvc.LocalService("workflow")
        date_now = time.strftime('%Y-%m-%d')
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','no_doanh_thu_shift_in')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+IMPORTING
                done_path = dir_path.name+DONE
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    seq = False
                    try:
                        file_data = csvUti._read_file(f_path)
                        
                        for seq,data in enumerate(file_data):
                            noidung_loi = ''
                            try:
                                st = float(data['so_tien'])
                            except Exception, e:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không đúng định dạng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                            if float(data['so_tien']) <= 0:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            vals={}
                            account_id = False
                            sql = '''
                                select id from account_account where upper(code)='%s' limit 1
                            '''%(data['ma_chi_nhanh'].upper())
                            cr.execute(sql)
                            chinhanh_ids = cr.fetchone()
                            if not chinhanh_ids:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy chi nhánh'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy chi nhánh')
                            
                            sql = '''
                                select id,bai_giaoca_id,account_ht_id,cmnd,giayphep_kinhdoanh,taixe,nhadautu,nhanvienvanphong,chinhanh_id
                                    from res_partner where upper(ma_doi_tuong)='%s' limit 1
                            '''%(data['ma_doi_tuong'].upper())
                            cr.execute(sql)
                            partner = cr.dictfetchone()
                            if not partner:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy đối tượng')
                            partner_id = partner and partner['id'] or False
                            bai_giaoca_id = partner and partner['bai_giaoca_id'] or False
                            
                            loai_doituong=''
                            if partner['taixe']==True:
                                if chinhanh_ids[0]!=partner['chinhanh_id']:
                                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của đối tượng')
                                loai_doituong='taixe'
                                account_id = partner and partner['account_ht_id'] or False
                            if partner['nhanvienvanphong']==True:
                                if chinhanh_ids[0]!=partner['chinhanh_id']:
                                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của đối tượng')
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
                            
                            loai_dt_bh_al = data['loai_dt_bh_al']
                            if not loai_dt_bh_al:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy loại DT-BH-AL trên template'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy loại DT-BH-AL trên template')
                            sql = ''' select id from loai_no_doanh_thu where upper(code)='%s' '''%(loai_dt_bh_al.upper())
                            cr.execute(sql)
                            loai_dt_bh_al_ids = cr.fetchone()
                            if loai_dt_bh_al and not loai_dt_bh_al_ids:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy loại DT-BH-AL'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy loại DT-BH-AL')
                            
                            if not data['ngay_giao_dich']:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy ngày giao dịch'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy ngày giao dịch')                            
                            date_invoice=datetime.strptime(data['ngay_giao_dich'],'%d/%m/%Y').strftime('%Y-%m-%d')
                            
                            vals.update({
                                'mlg_type': 'no_doanh_thu',
                                'type': 'out_invoice',
                                'account_id': account_id,
                                'chinhanh_id': chinhanh_ids and chinhanh_ids[0] or False,
                                'loai_doituong': loai_doituong,
                                'partner_id': partner_id,
                                'date_invoice': date_invoice,
                                'so_tien': float(data['so_tien']),
                                'dien_giai': data['dien_giai'],
                                'journal_id': journal_ids and journal_ids[0] or False,
                                'bai_giaoca_id': bai_giaoca_id,
                                'loai_nodoanhthu_id': loai_dt_bh_al_ids and loai_dt_bh_al_ids[0] or False,
                                'loai_giaodich': 'Giao dịch nhập từ SHIFT',
                            })
                            invoice_vals = invoice_obj.onchange_dien_giai_st(cr, uid, [], data['dien_giai'], data['so_tien'], journal_ids and journal_ids[0] or False, context)['value']
                            vals.update(invoice_vals)
                            invoice_id = invoice_obj.create(cr, uid, vals)
                            wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+date_now+'/'+f_path.split('/')[-1],
                            'loai_giaodich': 'Nợ DT-BH-AL (SHIFT) IN',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        cr.rollback()
                        if not noidung_loi:
                            noidung_loi = str(e).replace("'","''")
                            if seq:
                                noidung_loi = 'Dòng "%s": '%(seq+2) + noidung_loi
                        error_path = dir_path.name+ERROR
                        csvUti._moveFiles([f_path],error_path)
                        ngay = time.strftime('%Y-%m-%d %H:%M:%S')
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,ngay,1,ngay,ngay,
                             error_path+date_now+'/'+f_path.split('/')[-1],'Nợ DT-BH-AL (SHIFT) IN','Thu','Nhập','Tự động','Lỗi',noidung_loi
                        )
                        cr.execute(sql)
                        
                        body='''
                            <p>Ngày: %s</p>
                            <p>Tên file: %s</p>
                            <p>Loại giao dịch: %s</p>
                            <p>Ghi chú: %s</p>
                        '''%(ngay,error_path+date_now+'/'+f_path.split('/')[-1],'Nợ DT-BH-AL (SHIFT) IN',noidung_loi)
                        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID)
                        partner = user.partner_id
                        partner.signup_prepare()
                        post_values = {
                            'subject': 'Lỗi nhập tự động "Nợ DT-BH-AL (SHIFT) IN"',
                            'body': body,
                            'partner_ids': [],
                            }
                        lead_email = partner.email
                        msg_id = self.pool.get('res.partner').message_post(cr, uid, [partner.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, lead_email, msg_id, context)
                        cr.commit()
#                         raise osv.except_osv(_('Warning!'), str(e))
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def import_phaithu_nodoanhthu_shift(self, cr, uid, context=None):
        import_obj = self.pool.get('cauhinh.thumuc.import.tudong')
        invoice_obj = self.pool.get('account.invoice')
        voucher_obj = self.pool.get('account.voucher')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        wf_service = netsvc.LocalService("workflow")
        date_now = time.strftime('%Y-%m-%d')
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','no_doanh_thu_shift')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+IMPORTING
                done_path = dir_path.name+DONE
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    seq = False
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for seq,data in enumerate(file_data):
                            noidung_loi=''
                            try:
                                st = float(data['so_tien_da_thu'])
                            except Exception, e:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không đúng định dạng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                            sotiendathu = float(data['so_tien_da_thu'])
                            if sotiendathu <= 0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            sql = '''
                                select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                    from account_invoice where chinhanh_id in (select id from account_account where upper(code)='%s')
                                        and partner_id in (select id from res_partner where upper(ma_doi_tuong)='%s') and type='out_invoice'
                                        and mlg_type='no_doanh_thu' and state='open' 
                            '''%(data['ma_chi_nhanh'].upper(),data['ma_doi_tuong'].upper())
                            cr.execute(sql)
                            
                            for line in cr.dictfetchall():
                                if line['residual']>sotiendathu:
                                    amount = sotiendathu
                                    sotiendathu = 0
                                else:
                                    amount = line['residual']
                                    sotiendathu = sotiendathu-line['residual']
                                if not amount:
                                    break
                                journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','cash'),('chinhanh_id','=',line['chinhanh_id'])])
                                
                                if not data['ngay_thanh_toan']:
                                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy ngày thanh toán'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy ngày thanh toán')
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
                                    'loai_giaodich': 'Giao dịch cấn trừ từ SHIFT',
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
                                voucher_id = voucher_obj.create(cr, uid, vals, context)
                                voucher_obj.button_proforma_voucher(cr, uid, [voucher_id], context)
                                
                            if sotiendathu>0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền đã thu lớn hơn số tiền đề nghị phải thu'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền đã thu lớn hơn số tiền đề nghị phải thu')
                            
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+date_now+'/'+f_path.split('/')[-1],
                            'loai_giaodich': 'Nợ DT-BH-AL (SHIFT)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        cr.rollback()
                        if not noidung_loi:
                            noidung_loi = str(e).replace("'","''")
                            if seq:
                                noidung_loi = 'Dòng "%s": '%(seq+2) + noidung_loi
                        error_path = dir_path.name+ERROR
                        csvUti._moveFiles([f_path],error_path)
                        ngay = time.strftime('%Y-%m-%d %H:%M:%S')
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,ngay,1,ngay,ngay,
                             error_path+date_now+'/'+f_path.split('/')[-1],'Nợ DT-BH-AL (SHIFT)','Thu','Nhập','Tự động','Lỗi',noidung_loi
                        )
                        cr.execute(sql)
                        
                        body='''
                            <p>Ngày: %s</p>
                            <p>Tên file: %s</p>
                            <p>Loại giao dịch: %s</p>
                            <p>Ghi chú: %s</p>
                        '''%(ngay,error_path+date_now+'/'+f_path.split('/')[-1],'Nợ DT-BH-AL (SHIFT)',noidung_loi)
                        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID)
                        partner = user.partner_id
                        partner.signup_prepare()
                        post_values = {
                            'subject': 'Lỗi nhập tự động "Nợ DT-BH-AL (SHIFT)"',
                            'body': body,
                            'partner_ids': [],
                            }
                        lead_email = partner.email
                        msg_id = self.pool.get('res.partner').message_post(cr, uid, [partner.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, lead_email, msg_id, context)
                        cr.commit()
#                         raise osv.except_osv(_('Warning!'), str(e))
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def import_phaithu_chihodienthoai_shift(self, cr, uid, context=None):
        import_obj = self.pool.get('cauhinh.thumuc.import.tudong')
        invoice_obj = self.pool.get('account.invoice')
        voucher_obj = self.pool.get('account.voucher')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        wf_service = netsvc.LocalService("workflow")
        date_now = time.strftime('%Y-%m-%d')
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','chi_ho_dien_thoai_shift')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+IMPORTING
                done_path = dir_path.name+DONE
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    seq = False
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for seq,data in enumerate(file_data):
                            noidung_loi=''
                            try:
                                st = float(data['so_tien_da_thu'])
                            except Exception, e:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không đúng định dạng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                            sotiendathu = float(data['so_tien_da_thu'])
                            if sotiendathu <= 0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            sql = '''
                                select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                    from account_invoice where chinhanh_id in (select id from account_account where upper(code)='%s')
                                        and partner_id in (select id from res_partner where upper(ma_doi_tuong)='%s') and type='out_invoice'
                                        and mlg_type='chi_ho_dien_thoai' and state='open' 
                            '''%(data['ma_chi_nhanh'].upper(),data['ma_doi_tuong'].upper())
                            if data['so_hoa_don']:
                                sql += '''
                                    and upper(so_hoa_don)='%s' 
                                '''%(data['so_hoa_don'].upper())
                            if data['so_dien_thoai']:
                                sql += '''
                                    and upper(so_dien_thoai)='%s' 
                                '''%(data['so_dien_thoai'].upper())
                            sql += '''
                                order by date_invoice
                            '''
                            cr.execute(sql)
                            for line in cr.dictfetchall():
                                if line['residual']>sotiendathu:
                                    amount = sotiendathu
                                    sotiendathu = 0
                                else:
                                    amount = line['residual']
                                    sotiendathu = sotiendathu-line['residual']
                                if not amount:
                                    break
                                journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','cash'),('chinhanh_id','=',line['chinhanh_id'])])
                                
                                if not data['ngay_thanh_toan']:
                                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy ngày thanh toán'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy ngày thanh toán')
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
                                    'loai_giaodich': 'Giao dịch cấn trừ từ SHIFT',
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
                                voucher_id = voucher_obj.create(cr, uid, vals, context)
                                voucher_obj.button_proforma_voucher(cr, uid, [voucher_id], context)
                                
                            if sotiendathu>0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền đã thu lớn hơn số tiền đề nghị phải thu'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền đã thu lớn hơn số tiền đề nghị phải thu')
                            
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+date_now+'/'+f_path.split('/')[-1],
                            'loai_giaodich': 'Phải thu chi hộ điện thoại (SHIFT)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        cr.rollback()
                        if not noidung_loi:
                            noidung_loi = str(e).replace("'","''")
                            if seq:
                                noidung_loi = 'Dòng "%s": '%(seq+2) + noidung_loi
                        error_path = dir_path.name+ERROR
                        csvUti._moveFiles([f_path],error_path)
                        ngay = time.strftime('%Y-%m-%d %H:%M:%S')
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,ngay,1,ngay,ngay,
                             error_path+date_now+'/'+f_path.split('/')[-1],'Phải thu chi hộ điện thoại (SHIFT)','Thu','Nhập','Tự động','Lỗi',noidung_loi
                        )
                        cr.execute(sql)
                        
                        body='''
                            <p>Ngày: %s</p>
                            <p>Tên file: %s</p>
                            <p>Loại giao dịch: %s</p>
                            <p>Ghi chú: %s</p>
                        '''%(ngay,error_path+date_now+'/'+f_path.split('/')[-1],'Phải thu chi hộ điện thoại (SHIFT)',noidung_loi)
                        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID)
                        partner = user.partner_id
                        partner.signup_prepare()
                        post_values = {
                            'subject': 'Lỗi nhập tự động "Phải thu chi hộ điện thoại (SHIFT)"',
                            'body': body,
                            'partner_ids': [],
                            }
                        lead_email = partner.email
                        msg_id = self.pool.get('res.partner').message_post(cr, uid, [partner.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, lead_email, msg_id, context)
                        cr.commit()
#                         raise osv.except_osv(_('Warning!'), str(e))
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def import_phaithu_phaithubaohiem_shift(self, cr, uid, context=None):
        import_obj = self.pool.get('cauhinh.thumuc.import.tudong')
        invoice_obj = self.pool.get('account.invoice')
        voucher_obj = self.pool.get('account.voucher')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        wf_service = netsvc.LocalService("workflow")
        date_now = time.strftime('%Y-%m-%d')
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','phai_thu_bao_hiem_shift')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+IMPORTING
                done_path = dir_path.name+DONE
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    seq = False
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for seq,data in enumerate(file_data):
                            noidung_loi=''
                            try:
                                st = float(data['so_tien_da_thu'])
                            except Exception, e:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không đúng định dạng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                            sotiendathu = float(data['so_tien_da_thu'])
                            if sotiendathu <= 0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            bsx = data['bien_so_xe']
                            sql = ''' select id from bien_so_xe where upper(name)='%s' '''%(bsx.upper())
                            cr.execute(sql)
                            bien_so_xe_ids = cr.fetchone()
                            if bsx and not bien_so_xe_ids:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy biển số xe'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy biển số xe')
                                
                            sql = '''
                                select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                    from account_invoice where chinhanh_id in (select id from account_account where upper(code)='%s')
                                        and partner_id in (select id from res_partner where upper(ma_doi_tuong)='%s') and type='out_invoice'
                                        and mlg_type='phai_thu_bao_hiem' and state='open' 
                            '''%(data['ma_chi_nhanh'].upper(),data['ma_doi_tuong'].upper())
                            if data['so_hoa_don']:
                                sql += '''
                                    and upper(so_hoa_don)='%s' 
                                '''%(data['so_hoa_don'].upper())
                            if bsx:
                                sql += '''
                                    and bien_so_xe_id=%s 
                                '''%(bien_so_xe_ids[0])
                            sql += '''
                                order by date_invoice
                            '''
                            cr.execute(sql)
                            for line in cr.dictfetchall():
                                if line['residual']>sotiendathu:
                                    amount = sotiendathu
                                    sotiendathu = 0
                                else:
                                    amount = line['residual']
                                    sotiendathu = sotiendathu-line['residual']
                                if not amount:
                                    break
                                journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','cash'),('chinhanh_id','=',line['chinhanh_id'])])
                                
                                if not data['ngay_thanh_toan']:
                                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy ngày thanh toán'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy ngày thanh toán')
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
                                    'loai_giaodich': 'Giao dịch cấn trừ từ SHIFT',
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
                                voucher_id = voucher_obj.create(cr, uid, vals, context)
                                voucher_obj.button_proforma_voucher(cr, uid, [voucher_id], context)
                                
                            if sotiendathu>0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền đã thu lớn hơn số tiền đề nghị phải thu'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền đã thu lớn hơn số tiền đề nghị phải thu')
                            
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+date_now+'/'+f_path.split('/')[-1],
                            'loai_giaodich': 'Phải thu bảo hiểm (SHIFT)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        cr.rollback()
                        if not noidung_loi:
                            noidung_loi = str(e).replace("'","''")
                            if seq:
                                noidung_loi = 'Dòng "%s": '%(seq+2) + noidung_loi
                        error_path = dir_path.name+ERROR
                        csvUti._moveFiles([f_path],error_path)
                        ngay = time.strftime('%Y-%m-%d %H:%M:%S')
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,ngay,1,ngay,ngay,
                             error_path+date_now+'/'+f_path.split('/')[-1],'Phải thu bảo hiểm (SHIFT)','Thu','Nhập','Tự động','Lỗi',noidung_loi
                        )
                        cr.execute(sql)
                        
                        body='''
                            <p>Ngày: %s</p>
                            <p>Tên file: %s</p>
                            <p>Loại giao dịch: %s</p>
                            <p>Ghi chú: %s</p>
                        '''%(ngay,error_path+date_now+'/'+f_path.split('/')[-1],'Phải thu bảo hiểm (SHIFT)',noidung_loi)
                        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID)
                        partner = user.partner_id
                        partner.signup_prepare()
                        post_values = {
                            'subject': 'Lỗi nhập tự động "Phải thu bảo hiểm (SHIFT)"',
                            'body': body,
                            'partner_ids': [],
                            }
                        lead_email = partner.email
                        msg_id = self.pool.get('res.partner').message_post(cr, uid, [partner.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, lead_email, msg_id, context)
                        cr.commit()
#                         raise osv.except_osv(_('Warning!'), str(e))
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def import_phaithu_phatvipham_shift(self, cr, uid, context=None):
        import_obj = self.pool.get('cauhinh.thumuc.import.tudong')
        invoice_obj = self.pool.get('account.invoice')
        voucher_obj = self.pool.get('account.voucher')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        wf_service = netsvc.LocalService("workflow")
        date_now = time.strftime('%Y-%m-%d')
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','phat_vi_pham_shift')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+IMPORTING
                done_path = dir_path.name+DONE
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    seq = False
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for seq,data in enumerate(file_data):
                            noidung_loi=''
                            try:
                                st = float(data['so_tien_da_thu'])
                            except Exception, e:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không đúng định dạng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                            sotiendathu = float(data['so_tien_da_thu'])
                            if sotiendathu <= 0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            sql = '''
                                select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                    from account_invoice where chinhanh_id in (select id from account_account where upper(code)='%s')
                                        and partner_id in (select id from res_partner where upper(ma_doi_tuong)='%s') and type='out_invoice'
                                        and mlg_type='phat_vi_pham' and state='open' 
                            '''%(data['ma_chi_nhanh'].upper(),data['ma_doi_tuong'].upper())
                            cr.execute(sql)
                            for line in cr.dictfetchall():
                                if line['residual']>sotiendathu:
                                    amount = sotiendathu
                                    sotiendathu = 0
                                else:
                                    amount = line['residual']
                                    sotiendathu = sotiendathu-line['residual']
                                if not amount:
                                    break
                                journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','cash'),('chinhanh_id','=',line['chinhanh_id'])])
                                
                                if not data['ngay_thanh_toan']:
                                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy ngày thanh toán'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy ngày thanh toán')
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
                                    'loai_giaodich': 'Giao dịch cấn trừ từ SHIFT',
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
                                voucher_id = voucher_obj.create(cr, uid, vals, context)
                                voucher_obj.button_proforma_voucher(cr, uid, [voucher_id], context)
                                
                            if sotiendathu>0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền đã thu lớn hơn số tiền đề nghị phải thu'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền đã thu lớn hơn số tiền đề nghị phải thu')
                            
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+date_now+'/'+f_path.split('/')[-1],
                            'loai_giaodich': 'Phạt vi phạm (SHIFT)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        cr.rollback()
                        if not noidung_loi:
                            noidung_loi = str(e).replace("'","''")
                            if seq:
                                noidung_loi = 'Dòng "%s": '%(seq+2) + noidung_loi
                        error_path = dir_path.name+ERROR
                        csvUti._moveFiles([f_path],error_path)
                        ngay = time.strftime('%Y-%m-%d %H:%M:%S')
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,ngay,1,ngay,ngay,
                             error_path+date_now+'/'+f_path.split('/')[-1],'Phạt vi phạm (SHIFT)','Thu','Nhập','Tự động','Lỗi',noidung_loi
                        )
                        cr.execute(sql)
                        
                        body='''
                            <p>Ngày: %s</p>
                            <p>Tên file: %s</p>
                            <p>Loại giao dịch: %s</p>
                            <p>Ghi chú: %s</p>
                        '''%(ngay,error_path+date_now+'/'+f_path.split('/')[-1],'Phạt vi phạm (SHIFT)',noidung_loi)
                        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID)
                        partner = user.partner_id
                        partner.signup_prepare()
                        post_values = {
                            'subject': 'Lỗi nhập tự động "Phạt vi phạm (SHIFT)"',
                            'body': body,
                            'partner_ids': [],
                            }
                        lead_email = partner.email
                        msg_id = self.pool.get('res.partner').message_post(cr, uid, [partner.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, lead_email, msg_id, context)
                        cr.commit()
#                         raise osv.except_osv(_('Warning!'), str(e))
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def import_phaithu_thunoxuong_shift(self, cr, uid, context=None):
        import_obj = self.pool.get('cauhinh.thumuc.import.tudong')
        invoice_obj = self.pool.get('account.invoice')
        voucher_obj = self.pool.get('account.voucher')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        wf_service = netsvc.LocalService("workflow")
        date_now = time.strftime('%Y-%m-%d')
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','thu_no_xuong_shift')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+IMPORTING
                done_path = dir_path.name+DONE
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    seq = False
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for seq,data in enumerate(file_data):
                            noidung_loi=''
                            try:
                                st = float(data['so_tien_da_thu'])
                            except Exception, e:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không đúng định dạng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                            sotiendathu = float(data['so_tien_da_thu'])
                            if sotiendathu <= 0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            bsx = data['bien_so_xe']
                            sql = ''' select id from bien_so_xe where upper(name)='%s' '''%(bsx.upper())
                            cr.execute(sql)
                            bien_so_xe_ids = cr.fetchone()
                            if bsx and not bien_so_xe_ids:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy biển số xe'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy biển số xe')
                            
                            mx = data['ma_xuong']
                            sql = ''' select id from ma_xuong where upper(code)='%s' '''%(mx.upper())
                            cr.execute(sql)
                            ma_xuong_ids = cr.fetchone()
                            if mx and not ma_xuong_ids:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy mã xưởng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy mã xưởng')
                                
                            sql = '''
                                select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                    from account_invoice where chinhanh_id in (select id from account_account where upper(code)='%s')
                                        and partner_id in (select id from res_partner where upper(ma_doi_tuong)='%s') and type='out_invoice'
                                        and mlg_type='thu_no_xuong' and state='open'
                            '''%(data['ma_chi_nhanh'].upper(),data['ma_doi_tuong'].upper())
                            if data['so_hop_dong']:
                                sql += '''
                                    and upper(so_hop_dong)='%s' 
                                '''%(data['so_hop_dong'].upper())
                            if data['ma_chiet_tinh']:
                                sql += '''
                                    and upper(ma_bang_chiettinh_chiphi_sua)='%s' 
                                '''%(data['ma_chiet_tinh'].upper())
                            if bsx:
                                sql += '''
                                    and bien_so_xe_id=%s 
                                '''%(bien_so_xe_ids[0])
                            if mx:
                                sql += '''
                                    and ma_xuong_id=%s 
                                '''%(ma_xuong_ids[0])
                            sql += '''
                                order by date_invoice
                            '''
                            cr.execute(sql)
                            for line in cr.dictfetchall():
                                if line['residual']>sotiendathu:
                                    amount = sotiendathu
                                    sotiendathu = 0
                                else:
                                    amount = line['residual']
                                    sotiendathu = sotiendathu-line['residual']
                                if not amount:
                                    break
                                journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','cash'),('chinhanh_id','=',line['chinhanh_id'])])
                                
                                if not data['ngay_thanh_toan']:
                                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy ngày thanh toán'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy ngày thanh toán')
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
                                    'loai_giaodich': 'Giao dịch cấn trừ từ SHIFT',
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
                                voucher_id = voucher_obj.create(cr, uid, vals, context)
                                voucher_obj.button_proforma_voucher(cr, uid, [voucher_id], context)
                                
                            if sotiendathu>0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền đã thu lớn hơn số tiền đề nghị phải thu'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền đã thu lớn hơn số tiền đề nghị phải thu')
                            
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+date_now+'/'+f_path.split('/')[-1],
                            'loai_giaodich': 'Thu nợ xưởng (SHIFT)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        cr.rollback()
                        if not noidung_loi:
                            noidung_loi = str(e).replace("'","''")
                            if seq:
                                noidung_loi = 'Dòng "%s": '%(seq+2) + noidung_loi
                        error_path = dir_path.name+ERROR
                        csvUti._moveFiles([f_path],error_path)
                        ngay = time.strftime('%Y-%m-%d %H:%M:%S')
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,ngay,1,ngay,ngay,
                             error_path+date_now+'/'+f_path.split('/')[-1],'Thu nợ xưởng (SHIFT)','Thu','Nhập','Tự động','Lỗi',noidung_loi
                        )
                        cr.execute(sql)
                        
                        body='''
                            <p>Ngày: %s</p>
                            <p>Tên file: %s</p>
                            <p>Loại giao dịch: %s</p>
                            <p>Ghi chú: %s</p>
                        '''%(ngay,error_path+date_now+'/'+f_path.split('/')[-1],'Thu nợ xưởng (SHIFT)',noidung_loi)
                        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID)
                        partner = user.partner_id
                        partner.signup_prepare()
                        post_values = {
                            'subject': 'Lỗi nhập tự động "Thu nợ xưởng (SHIFT)"',
                            'body': body,
                            'partner_ids': [],
                            }
                        lead_email = partner.email
                        msg_id = self.pool.get('res.partner').message_post(cr, uid, [partner.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, lead_email, msg_id, context)
                        cr.commit()
#                         raise osv.except_osv(_('Warning!'), str(e))
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
        date_now = time.strftime('%Y-%m-%d')
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','thu_phi_thuong_hieu_shift')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+IMPORTING
                done_path = dir_path.name+DONE
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    seq = False
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for seq,data in enumerate(file_data):
                            noidung_loi=''
                            try:
                                st = float(data['so_tien_da_thu'])
                            except Exception, e:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không đúng định dạng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                            sotiendathu = float(data['so_tien_da_thu'])
                            if sotiendathu <= 0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            bsx = data['bien_so_xe']
                            sql = ''' select id from bien_so_xe where upper(name)='%s' '''%(bsx.upper())
                            cr.execute(sql)
                            bien_so_xe_ids = cr.fetchone()
                            if bsx and not bien_so_xe_ids:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy biển số xe'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy biển số xe')
                                
                            sql = '''
                                select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                    from account_invoice where chinhanh_id in (select id from account_account where upper(code)='%s')
                                        and partner_id in (select id from res_partner where upper(ma_doi_tuong)='%s') and type='out_invoice'
                                        and mlg_type='thu_phi_thuong_hieu' and state='open' 
                            '''%(data['ma_chi_nhanh'].upper(),data['ma_doi_tuong'].upper())
                            if data['so_hop_dong']:
                                sql += '''
                                    and upper(so_hop_dong)='%s' 
                                '''%(data['so_hop_dong'].upper())
                            if bsx:
                                sql += '''
                                    and bien_so_xe_id=%s 
                                '''%(bien_so_xe_ids[0])
                            sql += '''
                                order by date_invoice
                            '''
                            cr.execute(sql)
                            for line in cr.dictfetchall():
                                if line['residual']>sotiendathu:
                                    amount = sotiendathu
                                    sotiendathu = 0
                                else:
                                    amount = line['residual']
                                    sotiendathu = sotiendathu-line['residual']
                                if not amount:
                                    break
                                journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','cash'),('chinhanh_id','=',line['chinhanh_id'])])
                                
                                if not data['ngay_thanh_toan']:
                                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy ngày thanh toán'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy ngày thanh toán')
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
                                    'loai_giaodich': 'Giao dịch cấn trừ từ SHIFT',
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
                                voucher_id = voucher_obj.create(cr, uid, vals, context)
                                voucher_obj.button_proforma_voucher(cr, uid, [voucher_id], context)
                                
                            if sotiendathu>0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền đã thu lớn hơn số tiền đề nghị phải thu'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền đã thu lớn hơn số tiền đề nghị phải thu')
                            
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+date_now+'/'+f_path.split('/')[-1],
                            'loai_giaodich': 'Thu phí thương hiệu (SHIFT)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        cr.rollback()
                        if not noidung_loi:
                            noidung_loi = str(e).replace("'","''")
                            if seq:
                                noidung_loi = 'Dòng "%s": '%(seq+2) + noidung_loi
                        error_path = dir_path.name+ERROR
                        csvUti._moveFiles([f_path],error_path)
                        ngay = time.strftime('%Y-%m-%d %H:%M:%S')
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,ngay,1,ngay,ngay,
                             error_path+date_now+'/'+f_path.split('/')[-1],'Thu phí thương hiệu (SHIFT)','Thu','Nhập','Tự động','Lỗi',noidung_loi
                        )
                        cr.execute(sql)
                        
                        body='''
                            <p>Ngày: %s</p>
                            <p>Tên file: %s</p>
                            <p>Loại giao dịch: %s</p>
                            <p>Ghi chú: %s</p>
                        '''%(ngay,error_path+date_now+'/'+f_path.split('/')[-1],'Thu phí thương hiệu (SHIFT)',noidung_loi)
                        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID)
                        partner = user.partner_id
                        partner.signup_prepare()
                        post_values = {
                            'subject': 'Lỗi nhập tự động "Thu phí thương hiệu (SHIFT)"',
                            'body': body,
                            'partner_ids': [],
                            }
                        lead_email = partner.email
                        msg_id = self.pool.get('res.partner').message_post(cr, uid, [partner.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, lead_email, msg_id, context)
                        cr.commit()
#                         raise osv.except_osv(_('Warning!'), str(e))
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
        date_now = time.strftime('%Y-%m-%d')
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','tra_gop_xe_shift')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+IMPORTING
                done_path = dir_path.name+DONE
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    seq = False
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for seq,data in enumerate(file_data):
                            noidung_loi=''
                            try:
                                st = float(data['so_tien_da_thu'])
                            except Exception, e:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không đúng định dạng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                            sotiendathu = float(data['so_tien_da_thu'])
                            if sotiendathu <= 0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            bsx = data['bien_so_xe']
                            sql = ''' select id from bien_so_xe where upper(name)='%s' '''%(bsx.upper())
                            cr.execute(sql)
                            bien_so_xe_ids = cr.fetchone()
                            if bsx and not bien_so_xe_ids:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy biển số xe'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy biển số xe')

                            sql = '''
                                select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id,sotien_lai_conlai
                                    from account_invoice where chinhanh_id in (select id from account_account where upper(code)='%s')
                                        and partner_id in (select id from res_partner where upper(ma_doi_tuong)='%s') and type='out_invoice'
                                        and mlg_type='tra_gop_xe' and state='open' 
                            '''%(data['ma_chi_nhanh'].upper(),data['ma_doi_tuong'].upper())
                            if data['so_hop_dong']:
                                sql += '''
                                    and upper(so_hop_dong)='%s' 
                                '''%(data['so_hop_dong'].upper())
                            if bsx:
                                sql += '''
                                    and bien_so_xe_id=%s 
                                '''%(bien_so_xe_ids[0])
                            sql += '''
                                order by date_invoice
                            '''
                            cr.execute(sql)
                            for line in cr.dictfetchall():
                                if (line['residual']+line['sotien_lai_conlai'])>sotiendathu:
                                    amount = sotiendathu
                                    sotien_tragopxe = sotiendathu
                                    sotiendathu = 0
                                else:
                                    amount = line['residual']+line['sotien_lai_conlai']
                                    sotien_tragopxe = line['residual']+line['sotien_lai_conlai']
                                    sotiendathu = sotiendathu-(line['residual']+line['sotien_lai_conlai'])
                                if not amount:
                                    break
                                journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','cash'),('chinhanh_id','=',line['chinhanh_id'])])
                                
                                if not data['ngay_thanh_toan']:
                                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy ngày thanh toán'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy ngày thanh toán')
                                ngay_thanh_toan=datetime.strptime(data['ngay_thanh_toan'],'%d/%m/%Y').strftime('%Y-%m-%d')
                                
                                sotientra = amount
                                sotienlai = line['sotien_lai_conlai']
                                if sotientra>=sotienlai:
                                    sotientra = sotientra-sotienlai
                                else:
                                    sotientra = 0
                                amount = sotientra
                                
                                vals = {
                                    'amount': amount,
                                    'sotien_tragopxe': sotien_tragopxe,
                                    'sotien_lai_conlai': line['sotien_lai_conlai'],
                                    'partner_id': line['partner_id'],
                                    'reference': line['name'],
                                    'bai_giaoca_id': line['bai_giaoca_id'],
                                    'mlg_type': line['mlg_type'],
                                    'type': 'receipt',
                                    'chinhanh_id': line['chinhanh_id'],
                                    'journal_id': journal_ids[0],
                                    'date': ngay_thanh_toan,
                                    'loai_giaodich': 'Giao dịch cấn trừ từ SHIFT',
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
                                    'loai_giaodich': 'Giao dịch cấn trừ từ SHIFT',
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
                                voucher_id = voucher_obj.create(cr, uid, vals,context)
                                voucher_obj.button_proforma_voucher(cr, uid, [voucher_id],context)
                            if sotiendathu>0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền đã thu lớn hơn số tiền đề nghị phải thu'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền đã thu lớn hơn số tiền đề nghị phải thu')
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+date_now+'/'+f_path.split('/')[-1],
                            'loai_giaodich': 'Trả góp xe (SHIFT)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        cr.rollback()
                        if not noidung_loi:
                            noidung_loi = str(e).replace("'","''")
                            if seq:
                                noidung_loi = 'Dòng "%s": '%(seq+2) + noidung_loi
                        error_path = dir_path.name+ERROR
                        csvUti._moveFiles([f_path],error_path)
                        ngay = time.strftime('%Y-%m-%d %H:%M:%S')
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,ngay,1,ngay,ngay,
                             error_path+date_now+'/'+f_path.split('/')[-1],'Trả góp xe (SHIFT)','Thu','Nhập','Tự động','Lỗi',noidung_loi
                        )
                        cr.execute(sql)
                        
                        body='''
                            <p>Ngày: %s</p>
                            <p>Tên file: %s</p>
                            <p>Loại giao dịch: %s</p>
                            <p>Ghi chú: %s</p>
                        '''%(ngay,error_path+date_now+'/'+f_path.split('/')[-1],'Trả góp xe (SHIFT)',noidung_loi)
                        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID)
                        partner = user.partner_id
                        partner.signup_prepare()
                        post_values = {
                            'subject': 'Lỗi nhập tự động "Trả góp xe (SHIFT)"',
                            'body': body,
                            'partner_ids': [],
                            }
                        lead_email = partner.email
                        msg_id = self.pool.get('res.partner').message_post(cr, uid, [partner.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, lead_email, msg_id, context)
                        cr.commit()
#                         raise osv.except_osv(_('Warning!'), str(e))
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def import_phaithu_nodoanhthu_histaff(self, cr, uid, context=None):
        import_obj = self.pool.get('cauhinh.thumuc.import.tudong')
        invoice_obj = self.pool.get('account.invoice')
        voucher_obj = self.pool.get('account.voucher')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        wf_service = netsvc.LocalService("workflow")
        date_now = time.strftime('%Y-%m-%d')
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','no_doanh_thu_histaff')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+IMPORTING
                done_path = dir_path.name+DONE
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    seq = False
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for seq,data in enumerate(file_data):
                            noidung_loi=''
                            try:
                                st = float(data['so_tien_da_thu'])
                            except Exception, e:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không đúng định dạng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                            sotiendathu = float(data['so_tien_da_thu'])
                            if sotiendathu <= 0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            sql = '''
                                select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                    from account_invoice where chinhanh_id in (select id from account_account where upper(code)='%s')
                                        and partner_id in (select id from res_partner where upper(ma_doi_tuong)='%s') and type='out_invoice'
                                        and mlg_type='no_doanh_thu' and state='open' 
                            '''%(data['ma_chi_nhanh'].upper(),data['ma_doi_tuong'].upper())
                            cr.execute(sql)
                            
                            for line in cr.dictfetchall():
                                if line['residual']>sotiendathu:
                                    amount = sotiendathu
                                    sotiendathu = 0
                                else:
                                    amount = line['residual']
                                    sotiendathu = sotiendathu-line['residual']
                                if not amount:
                                    break
                                journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','cash'),('chinhanh_id','=',line['chinhanh_id'])])
                                
                                if not data['ngay_thanh_toan']:
                                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy ngày thanh toán'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy ngày thanh toán')
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
                                    'loai_giaodich': 'Giao dịch cấn trừ từ SHIFT',
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
                                voucher_id = voucher_obj.create(cr, uid, vals, context)
                                voucher_obj.button_proforma_voucher(cr, uid, [voucher_id], context)
                                
                            if sotiendathu>0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền đã thu lớn hơn số tiền đề nghị phải thu'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền đã thu lớn hơn số tiền đề nghị phải thu')
                            
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+date_now+'/'+f_path.split('/')[-1],
                            'loai_giaodich': 'Nợ DT-BH-AL (HISTAFF)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        cr.rollback()
                        if not noidung_loi:
                            noidung_loi = str(e).replace("'","''")
                            if seq:
                                noidung_loi = 'Dòng "%s": '%(seq+2) + noidung_loi
                        error_path = dir_path.name+ERROR
                        csvUti._moveFiles([f_path],error_path)
                        ngay = time.strftime('%Y-%m-%d %H:%M:%S')
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,ngay,1,ngay,ngay,
                             error_path+date_now+'/'+f_path.split('/')[-1],'Nợ DT-BH-AL (HISTAFF)','Thu','Nhập','Tự động','Lỗi',noidung_loi
                        )
                        cr.execute(sql)
                        
                        body='''
                            <p>Ngày: %s</p>
                            <p>Tên file: %s</p>
                            <p>Loại giao dịch: %s</p>
                            <p>Ghi chú: %s</p>
                        '''%(ngay,error_path+date_now+'/'+f_path.split('/')[-1],'Nợ DT-BH-AL (HISTAFF)',noidung_loi)
                        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID)
                        partner = user.partner_id
                        partner.signup_prepare()
                        post_values = {
                            'subject': 'Lỗi nhập tự động "Nợ DT-BH-AL (HISTAFF)"',
                            'body': body,
                            'partner_ids': [],
                            }
                        lead_email = partner.email
                        msg_id = self.pool.get('res.partner').message_post(cr, uid, [partner.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, lead_email, msg_id, context)
                        cr.commit()
#                         raise osv.except_osv(_('Warning!'), str(e))
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def import_phaithu_phaithutamung_shift(self, cr, uid, context=None):
        import_obj = self.pool.get('cauhinh.thumuc.import.tudong')
        invoice_obj = self.pool.get('account.invoice')
        voucher_obj = self.pool.get('account.voucher')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        wf_service = netsvc.LocalService("workflow")
        date_now = time.strftime('%Y-%m-%d')
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','hoan_tam_ung_shift')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+IMPORTING
                done_path = dir_path.name+DONE
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    seq = False
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for seq,data in enumerate(file_data):
                            noidung_loi=''
                            try:
                                st = float(data['so_tien_da_thu'])
                            except Exception, e:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không đúng định dạng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                            sotiendathu = float(data['so_tien_da_thu'])
                            if sotiendathu <= 0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            sql = '''
                                select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                    from account_invoice where chinhanh_id in (select id from account_account where upper(code)='%s')
                                        and partner_id in (select id from res_partner where upper(ma_doi_tuong)='%s') and type='out_invoice'
                                        and mlg_type='hoan_tam_ung' and state='open' 
                            '''%(data['ma_chi_nhanh'].upper(),data['ma_doi_tuong'].upper())
                            cr.execute(sql)
                            for line in cr.dictfetchall():
                                if line['residual']>sotiendathu:
                                    amount = sotiendathu
                                    sotiendathu = 0
                                else:
                                    amount = line['residual']
                                    sotiendathu = sotiendathu-line['residual']
                                if not amount:
                                    break
                                journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','cash'),('chinhanh_id','=',line['chinhanh_id'])])
                                
                                if not data['ngay_thanh_toan']:
                                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy ngày thanh toán'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy ngày thanh toán')
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
                                    'loai_giaodich': 'Giao dịch cấn trừ từ SHIFT',
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
                                voucher_id = voucher_obj.create(cr, uid, vals, context)
                                voucher_obj.button_proforma_voucher(cr, uid, [voucher_id], context)
                                
                            if sotiendathu>0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền đã thu lớn hơn số tiền đề nghị phải thu'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền đã thu lớn hơn số tiền đề nghị phải thu')
                            
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+date_now+'/'+f_path.split('/')[-1],
                            'loai_giaodich': 'Phải thu tạm ứng (SHIFT)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        cr.rollback()
                        if not noidung_loi:
                            noidung_loi = str(e).replace("'","''")
                            if seq:
                                noidung_loi = 'Dòng "%s": '%(seq+2) + noidung_loi
                        error_path = dir_path.name+ERROR
                        csvUti._moveFiles([f_path],error_path)
                        ngay = time.strftime('%Y-%m-%d %H:%M:%S')
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,ngay,1,ngay,ngay,
                             error_path+date_now+'/'+f_path.split('/')[-1],'Phải thu tạm ứng (SHIFT)','Thu','Nhập','Tự động','Lỗi',noidung_loi
                        )
                        cr.execute(sql)
                        
                        body='''
                            <p>Ngày: %s</p>
                            <p>Tên file: %s</p>
                            <p>Loại giao dịch: %s</p>
                            <p>Ghi chú: %s</p>
                        '''%(ngay,error_path+date_now+'/'+f_path.split('/')[-1],'Phải thu tạm ứng (SHIFT)',noidung_loi)
                        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID)
                        partner = user.partner_id
                        partner.signup_prepare()
                        post_values = {
                            'subject': 'Lỗi nhập tự động "Phải thu tạm ứng (SHIFT)"',
                            'body': body,
                            'partner_ids': [],
                            }
                        lead_email = partner.email
                        msg_id = self.pool.get('res.partner').message_post(cr, uid, [partner.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, lead_email, msg_id, context)
                        cr.commit()
#                         raise osv.except_osv(_('Warning!'), str(e))
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def import_phaithu_kyquy_shift(self, cr, uid, context=None):
        import_obj = self.pool.get('cauhinh.thumuc.import.tudong')
        kyquy_obj = self.pool.get('thu.ky.quy')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        date_now = time.strftime('%Y-%m-%d')
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','phai_thu_ky_quy_shift')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+IMPORTING
                done_path = dir_path.name+DONE
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    seq = False
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for seq,data in enumerate(file_data):
                            noidung_loi=''
                            try:
                                st = float(data['so_tien_da_thu'])
                            except Exception, e:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không đúng định dạng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                            if float(data['so_tien_da_thu']) <= 0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            sql = '''
                                select id from account_account where upper(code)='%s' limit 1
                            '''%(data['ma_chi_nhanh'].upper())
                            cr.execute(sql)
                            chinhanh_ids = cr.fetchone()
                            if not chinhanh_ids:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy chi nhánh'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy chi nhánh')
                            
                            lkq = data['loai_ky_quy']
                            if not lkq:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chưa nhập loại ký quỹ'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Chưa nhập loại ký quỹ')
                            
                            sql = '''
                                select id from loai_ky_quy where upper(code)='%s' limit 1
                            '''%(lkq.upper())
                            cr.execute(sql)
                            loai_kq_ids = [r[0] for r in cr.fetchall()]
                            if not loai_kq_ids:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy loại ký quỹ'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy loại ký quỹ')
                            
                            sql = '''
                                select nhadautu from res_partner where upper(ma_doi_tuong)='%s'
                            '''%(data['ma_doi_tuong'].upper())
                            cr.execute(sql)
                            ndt = cr.fetchone()
                            if not ndt:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy đối tượng')
                            bsx_ids = []
                            if ndt[0]:
                                bsx = data['bien_so_xe']
                                if not bsx:
                                    noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy biển số xe đối với loại đối tượng nhà đầu tư'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy biển số xe đối với loại đối tượng nhà đầu tư')
                                sql = '''
                                    select id from bien_so_xe where upper(name)='%s' limit 1
                                '''%(bsx.upper())
                                cr.execute(sql)
                                bsx_ids = [r[0] for r in cr.fetchall()]
                                if not bsx_ids:
                                    noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy biển số xe'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy biển số xe đối')
                            
                            sql = '''
                                select id from thu_ky_quy where partner_id in (select id from res_partner where ma_doi_tuong='%s')
                                    and chinhanh_id=%s and state='draft' and loai_kyquy_id=%s 
                            '''%(data['ma_doi_tuong'],chinhanh_ids[0],loai_kq_ids[0])
                            cr.execute(sql)
                            for kyquy in cr.dictfetchall():
                                if bsx_ids:
                                    cr.execute('update thu_ky_quy set so_tien=%s,sotien_conlai=%s,bien_so_xe_id=%s where id=%s',(data['so_tien_da_thu'],data['so_tien_da_thu'],bsx_ids[0],kyquy['id'],))
                                else:
                                    cr.execute('update thu_ky_quy set so_tien=%s,sotien_conlai=%s where id=%s',(data['so_tien_da_thu'],data['so_tien_da_thu'],kyquy['id'],))
                                kyquy_obj.bt_thu(cr, uid, kyquy['id'])
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+date_now+'/'+f_path.split('/')[-1],
                            'loai_giaodich': 'Phải thu ký quỹ (SHIFT)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        cr.rollback()
                        if not noidung_loi:
                            noidung_loi = str(e).replace("'","''")
                            if seq:
                                noidung_loi = 'Dòng "%s": '%(seq+2) + noidung_loi
                        error_path = dir_path.name+ERROR
                        csvUti._moveFiles([f_path],error_path)
                        ngay = time.strftime('%Y-%m-%d %H:%M:%S')
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,ngay,1,ngay,ngay,
                             error_path+date_now+'/'+f_path.split('/')[-1],'Phải thu ký quỹ (SHIFT)','Thu','Nhập','Tự động','Lỗi',noidung_loi
                        )
                        cr.execute(sql)
                        
                        body='''
                            <p>Ngày: %s</p>
                            <p>Tên file: %s</p>
                            <p>Loại giao dịch: %s</p>
                            <p>Ghi chú: %s</p>
                        '''%(ngay,error_path+date_now+'/'+f_path.split('/')[-1],'Phải thu ký quỹ (SHIFT)',noidung_loi)
                        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID)
                        partner = user.partner_id
                        partner.signup_prepare()
                        post_values = {
                            'subject': 'Lỗi nhập tự động "Phải thu ký quỹ (SHIFT)"',
                            'body': body,
                            'partner_ids': [],
                            }
                        lead_email = partner.email
                        msg_id = self.pool.get('res.partner').message_post(cr, uid, [partner.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, lead_email, msg_id, context)
                        cr.commit()
#                         raise osv.except_osv(_('Warning!'), str(e))
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
        date_now = time.strftime('%Y-%m-%d')
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','phat_vi_pham')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+IMPORTING
                done_path = dir_path.name+DONE
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    seq = False
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for seq,data in enumerate(file_data):
                            noidung_loi=''
                            try:
                                st = float(data['so_tien_da_thu'])
                            except Exception, e:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không đúng định dạng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                            sotiendathu = float(data['so_tien_da_thu'])
                            if sotiendathu <= 0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            sql = '''
                                select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                    from account_invoice where chinhanh_id in (select id from account_account where upper(code)='%s')
                                        and partner_id in (select id from res_partner where upper(ma_doi_tuong)='%s') and type='out_invoice'
                                        and mlg_type='phat_vi_pham' and state='open'
                                    order by date_invoice
                            '''%(data['ma_chi_nhanh'].upper(),data['ma_doi_tuong'].upper())
                            cr.execute(sql)
                            
                            for line in cr.dictfetchall():
                                if line['residual']>sotiendathu:
                                    amount = sotiendathu
                                    sotiendathu = 0
                                else:
                                    amount = line['residual']
                                    sotiendathu = sotiendathu-line['residual']
                                if not amount:
                                    break
                                journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','cash'),('chinhanh_id','=',line['chinhanh_id'])])
                                
                                if not data['ngay_thanh_toan']:
                                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy ngày thanh toán'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy ngày thanh toán')
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
                                    'loai_giaodich': 'Giao dịch cấn trừ từ HISTAFF',
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
                                voucher_id = voucher_obj.create(cr, uid, vals, context)
                                voucher_obj.button_proforma_voucher(cr, uid, [voucher_id], context)
                            if sotiendathu>0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền đã thu lớn hơn số tiền đề nghị phải thu'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền đã thu lớn hơn số tiền đề nghị phải thu')
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+date_now+'/'+f_path.split('/')[-1],
                            'loai_giaodich': 'Phạt vi phạm (HISTAFF)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        cr.rollback()
                        if not noidung_loi:
                            noidung_loi = str(e).replace("'","''")
                            if seq:
                                noidung_loi = 'Dòng "%s": '%(seq+2) + noidung_loi
                        error_path = dir_path.name+ERROR
                        csvUti._moveFiles([f_path],error_path)
                        ngay = time.strftime('%Y-%m-%d %H:%M:%S')
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,ngay,1,ngay,ngay,
                             error_path+date_now+'/'+f_path.split('/')[-1],'Phạt vi phạm (HISTAFF)','Thu','Nhập','Tự động','Lỗi',noidung_loi
                        )
                        cr.execute(sql)
                        
                        body='''
                            <p>Ngày: %s</p>
                            <p>Tên file: %s</p>
                            <p>Loại giao dịch: %s</p>
                            <p>Ghi chú: %s</p>
                        '''%(ngay,error_path+date_now+'/'+f_path.split('/')[-1],'Phạt vi phạm (HISTAFF)',noidung_loi)
                        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID)
                        partner = user.partner_id
                        partner.signup_prepare()
                        post_values = {
                            'subject': 'Lỗi nhập tự động "Phạt vi phạm (HISTAFF)"',
                            'body': body,
                            'partner_ids': [],
                            }
                        lead_email = partner.email
                        msg_id = self.pool.get('res.partner').message_post(cr, uid, [partner.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, lead_email, msg_id, context)
                        cr.commit()
#                         raise osv.except_osv(_('Warning!'), str(e))
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
        date_now = time.strftime('%Y-%m-%d')
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','hoan_tam_ung')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+IMPORTING
                done_path = dir_path.name+DONE
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    seq = False
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for seq,data in enumerate(file_data):
                            noidung_loi=''
                            try:
                                st = float(data['so_tien_da_thu'])
                            except Exception, e:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không đúng định dạng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                            sotiendathu = float(data['so_tien_da_thu'])
                            if sotiendathu <= 0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            sql = '''
                                select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                    from account_invoice where chinhanh_id in (select id from account_account where upper(code)='%s')
                                        and partner_id in (select id from res_partner where upper(ma_doi_tuong)='%s') and type='out_invoice'
                                        and mlg_type='hoan_tam_ung' and state='open'
                                    order by date_invoice
                            '''%(data['ma_chi_nhanh'].upper(),data['ma_doi_tuong'].upper())
                            cr.execute(sql)
                            for line in cr.dictfetchall():
                                if line['residual']>sotiendathu:
                                    amount = sotiendathu
                                    sotiendathu = 0
                                else:
                                    amount = line['residual']
                                    sotiendathu = sotiendathu-line['residual']
                                if not amount:
                                    break
                                journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','cash'),('chinhanh_id','=',line['chinhanh_id'])])
                                
                                if not data['ngay_thanh_toan']:
                                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy ngày thanh toán'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy ngày thanh toán')
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
                                    'loai_giaodich': 'Giao dịch cấn trừ từ HISTAFF',
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
                                voucher_id = voucher_obj.create(cr, uid, vals, context)
                                voucher_obj.button_proforma_voucher(cr, uid, [voucher_id], context)
                            if sotiendathu>0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền đã thu lớn hơn số tiền đề nghị phải thu'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền đã thu lớn hơn số tiền đề nghị phải thu')
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+date_now+'/'+f_path.split('/')[-1],
                            'loai_giaodich': 'Phải thu tạm ứng (HISTAFF)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        cr.rollback()
                        if not noidung_loi:
                            noidung_loi = str(e).replace("'","''")
                            if seq:
                                noidung_loi = 'Dòng "%s": '%(seq+2) + noidung_loi
                        error_path = dir_path.name+ERROR
                        csvUti._moveFiles([f_path],error_path)
                        ngay = time.strftime('%Y-%m-%d %H:%M:%S')
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,ngay,1,ngay,ngay,
                             error_path+date_now+'/'+f_path.split('/')[-1],'Phải thu tạm ứng (HISTAFF)','Thu','Nhập','Tự động','Lỗi',noidung_loi
                        )
                        cr.execute(sql)
                        
                        body='''
                            <p>Ngày: %s</p>
                            <p>Tên file: %s</p>
                            <p>Loại giao dịch: %s</p>
                            <p>Ghi chú: %s</p>
                        '''%(ngay,error_path+date_now+'/'+f_path.split('/')[-1],'Phải thu tạm ứng (HISTAFF)',noidung_loi)
                        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID)
                        partner = user.partner_id
                        partner.signup_prepare()
                        post_values = {
                            'subject': 'Lỗi nhập tự động "Phải thu tạm ứng (HISTAFF)"',
                            'body': body,
                            'partner_ids': [],
                            }
                        lead_email = partner.email
                        msg_id = self.pool.get('res.partner').message_post(cr, uid, [partner.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, lead_email, msg_id, context)
                        cr.commit()
#                         raise osv.except_osv(_('Warning!'), str(e))
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def import_phaithu_kyquy_histaff(self, cr, uid, context=None):
        import_obj = self.pool.get('cauhinh.thumuc.import.tudong')
        kyquy_obj = self.pool.get('thu.ky.quy')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        date_now = time.strftime('%Y-%m-%d')
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','phai_thu_ky_quy')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+IMPORTING
                done_path = dir_path.name+DONE
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    seq = False
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for seq,data in enumerate(file_data):
                            noidung_loi=''
                            try:
                                st = float(data['so_tien_da_thu'])
                            except Exception, e:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không đúng định dạng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                            if float(data['so_tien_da_thu']) <= 0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            sql = '''
                                select id from account_account where upper(code)='%s' limit 1
                            '''%(data['ma_chi_nhanh'].upper())
                            cr.execute(sql)
                            chinhanh_ids = cr.fetchone()
                            if not chinhanh_ids:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy chi nhánh'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy chi nhánh')

                            sql = '''
                                select id from thu_ky_quy where partner_id in (select id from res_partner where upper(ma_doi_tuong)='%s')
                                    and chinhanh_id=%s and state='draft'
                            '''%(data['ma_doi_tuong'].upper(),chinhanh_ids[0])
                            cr.execute(sql)
                            for kyquy in cr.dictfetchall():
                                cr.execute('update thu_ky_quy set so_tien=%s,sotien_conlai=%s where id=%s',(data['so_tien_da_thu'],data['so_tien_da_thu'],kyquy['id'],))
                                kyquy_obj.bt_thu(cr, uid, kyquy['id'])
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+date_now+'/'+f_path.split('/')[-1],
                            'loai_giaodich': 'Phải thu ký quỹ (HISTAFF)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        cr.rollback()
                        if not noidung_loi:
                            noidung_loi = str(e).replace("'","''")
                            if seq:
                                noidung_loi = 'Dòng "%s": '%(seq+2) + noidung_loi
                        error_path = dir_path.name+ERROR
                        csvUti._moveFiles([f_path],error_path)
                        ngay = time.strftime('%Y-%m-%d %H:%M:%S')
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,ngay,1,ngay,ngay,
                             error_path+date_now+'/'+f_path.split('/')[-1],'Phải thu ký quỹ (HISTAFF)','Thu','Nhập','Tự động','Lỗi',noidung_loi
                        )
                        cr.execute(sql)
                        
                        body='''
                            <p>Ngày: %s</p>
                            <p>Tên file: %s</p>
                            <p>Loại giao dịch: %s</p>
                            <p>Ghi chú: %s</p>
                        '''%(ngay,error_path+date_now+'/'+f_path.split('/')[-1],'Phải thu ký quỹ (HISTAFF)',noidung_loi)
                        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID)
                        partner = user.partner_id
                        partner.signup_prepare()
                        post_values = {
                            'subject': 'Lỗi nhập tự động "Phải thu ký quỹ (HISTAFF)"',
                            'body': body,
                            'partner_ids': [],
                            }
                        lead_email = partner.email
                        msg_id = self.pool.get('res.partner').message_post(cr, uid, [partner.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, lead_email, msg_id, context)
                        cr.commit()
#                         raise osv.except_osv(_('Warning!'), str(e))
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
        thukyquy_obj = self.pool.get('thu.ky.quy')
        trakyquy_obj = self.pool.get('tra.ky.quy')
        wf_service = netsvc.LocalService("workflow")
        date_now = time.strftime('%Y-%m-%d')
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','fustion_phaithu')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+IMPORTING
                done_path = dir_path.name+DONE
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for data in file_data:
                            noidung_loi=''
                            request_ref_number = ''
                            thukyquys = []
                            trakyquys = []
                            
                            try:
                                request_ref_number = str(data['REQUEST_REF_NUMBER'])
                            except Exception, e:
                                noidung_loi = 'REQUEST_REF_NUMBER "%s" không đúng định dạng'%(data['REQUEST_REF_NUMBER'])
                                raise osv.except_osv(_('Cảnh báo!'), 'REQUEST_REF_NUMBER không đúng định dạng')
                            
                            try:
                                st = float(data['ACCTD_AMOUNT'])
                            except Exception, e:
                                noidung_loi = 'REQUEST_REF_NUMBER "%s": Số tiền không đúng định dạng'%(request_ref_number)
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                            
                            sotiendathu = float(data['ACCTD_AMOUNT'])
                            if sotiendathu <= 0:
                                noidung_loi='REQUEST_REF_NUMBER "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(request_ref_number)
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            sql = '''
                                select id,partner_id,so_tien,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id,state,sotien_lai_conlai
                                    from account_invoice where upper(name)='%s' and type='out_invoice'
                                    order by date_invoice
                            '''%(request_ref_number.strip().upper())
                            cr.execute(sql)
                            invoices = cr.dictfetchall()
                            if not invoices:
                                sql = '''
                                    select id,partner_id,so_tien,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id,state,sotien_lai_conlai
                                        from account_invoice where upper(ref_number)='%s' and type='out_invoice'
                                        order by date_invoice
                                '''%(request_ref_number.strip().upper())
                                cr.execute(sql)
                                invoices = cr.dictfetchall()
                            
                            if not invoices:
                                sql = '''
                                    select id,so_tien,state from thu_ky_quy where upper(name)='%s'
                                '''%(request_ref_number.strip().upper())
                                cr.execute(sql)
                                thukyquys = cr.dictfetchall()
                            if not thukyquys:
                                sql = '''
                                    select id,so_tien,state from tra_ky_quy where upper(name)='%s'
                                '''%(request_ref_number.strip().upper())
                                cr.execute(sql)
                                trakyquys = cr.dictfetchall()      
                            
#                             if not invoices:
#                                 sql = '''
#                                     select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id,state
#                                         from account_invoice where so_hoa_don='%s' and type='out_invoice'
#                                         order by date_invoice
#                                 '''%(request_ref_number.strip())
#                                 cr.execute(sql)
#                                 invoices = cr.dictfetchall()
#                             if not invoices:
#                                 sql = '''
#                                     select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id,state
#                                         from account_invoice where bien_so_xe_id in (select id from bien_so_xe where name='%s') and type='out_invoice'
#                                         order by date_invoice
#                                 '''%(request_ref_number.strip())
#                                 cr.execute(sql)
#                                 invoices = cr.dictfetchall()
#                             if not invoices:
#                                 sql = '''
#                                     select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id,state
#                                         from account_invoice where ma_bang_chiettinh_chiphi_sua='%s' and type='out_invoice'
#                                         order by date_invoice
#                                 '''%(request_ref_number.strip())
#                                 cr.execute(sql)
#                                 invoices = cr.dictfetchall()
#                             if not invoices:
#                                 sql = '''
#                                     select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id,state
#                                         from account_invoice where so_hop_dong='%s' and type='out_invoice'
#                                         order by date_invoice
#                                 '''%(request_ref_number.strip())
#                                 cr.execute(sql)
#                                 invoices = cr.dictfetchall()    
                            if not invoices and not thukyquys and not trakyquys:
                                noidung_loi='REQUEST_REF_NUMBER "%s": Không tìm thấy công nợ'%(request_ref_number)
                                raise osv.except_osv(_('Warning!'), 'Không tìm thấy công nợ')
                            
                            loai = data['TYPE']
                            if not loai and loai not in ['Thu','thu','chi','Chi']:
                                noidung_loi='REQUEST_REF_NUMBER "%s": Không tìm thấy TYPE'%(request_ref_number)
                                raise osv.except_osv(_('Warning!'), 'Không tìm thấy TYPE')
                            
                            for thukyquy in thukyquys:
                                if loai in ['Thu','thu'] and thukyquy['state']!='draft':
                                    noidung_loi='REQUEST_REF_NUMBER "%s": Phiếu đã thu rồi'%(request_ref_number)
                                    raise osv.except_osv(_('Warning!'), 'Phiếu đã thu rồi')
                                if loai in ['Chi','chi']:
                                    noidung_loi='REQUEST_REF_NUMBER "%s": TYPE bị sai'%(request_ref_number)
                                    raise osv.except_osv(_('Warning!'), 'TYPE bị sai')
                                if sotiendathu != thukyquy['so_tien']:
                                    noidung_loi='REQUEST_REF_NUMBER "%s": Số tiền đã thu khác với số tiền đề nghị thu'%(request_ref_number)
                                    raise osv.except_osv(_('Warning!'), 'Số tiền đã thu khác với số tiền đề nghị thu')
                                thukyquy_obj.bt_thu(cr, uid, [thukyquy['id']])
                                sql = '''
                                    update thu_ky_quy set fusion_id='%s' where id=%s
                                '''%(data['TRANSACTION_NUMBER'],thukyquy['id'])
                                cr.execute(sql)
                                sotiendathu = 0
                                
                            for trakyquy in trakyquys:
                                if loai in ['Chi','chi'] and trakyquy['state']!='draft':
                                    noidung_loi='REQUEST_REF_NUMBER "%s": Phiếu đã chi rồi'%(request_ref_number)
                                    raise osv.except_osv(_('Warning!'), 'Phiếu đã chi rồi')
                                if loai in ['Thu','thu']:
                                    noidung_loi='REQUEST_REF_NUMBER "%s": TYPE bị sai'%(request_ref_number)
                                    raise osv.except_osv(_('Warning!'), 'TYPE bị sai')
                                if sotiendathu != trakyquy['so_tien']:
                                    noidung_loi='REQUEST_REF_NUMBER "%s": Số tiền đã chi khác với số tiền đề nghị chi'%(request_ref_number)
                                    raise osv.except_osv(_('Warning!'), 'Số tiền đã chi khác với số tiền đề nghị chi')
                                trakyquy_obj.bt_tra(cr, uid, [trakyquy['id']])
                                sql = '''
                                    update tra_ky_quy set fusion_id='%s' where id=%s
                                '''%(data['TRANSACTION_NUMBER'],trakyquy['id'])
                                cr.execute(sql)
                                sotiendathu = 0
                            
                            for invoice in invoices:
                                if loai in ['Chi','chi'] and invoice['state']!='draft':
                                    noidung_loi='REQUEST_REF_NUMBER "%s": Phiếu đã chi rồi'%(request_ref_number)
                                    raise osv.except_osv(_('Warning!'), 'Phiếu đã chi rồi')
                                if loai in ['Chi','chi'] and invoice['state']=='draft':
                                    if sotiendathu<(invoice['so_tien']+invoice['sotien_lai_conlai']):
                                        noidung_loi='REQUEST_REF_NUMBER "%s": Số tiền chi không được nhỏ hơn số tiền đề nghị chi'%(request_ref_number)
                                        raise osv.except_osv(_('Warning!'), 'Số tiền chi không được nhỏ hơn số tiền đề nghị chi')
                                    else:
                                        sotiendathu = sotiendathu-(invoice['so_tien']+invoice['sotien_lai_conlai'])
                                    wf_service.trg_validate(uid, 'account.invoice', invoice['id'], 'invoice_open', cr)
                                    sql = '''
                                        update account_invoice set fusion_id='%s' where id=%s
                                    '''%(data['TRANSACTION_NUMBER'],invoice['id'])
                                    cr.execute(sql)
                                
                                if loai in ['Thu','thu'] and invoice['state']!='open':
                                    noidung_loi='REQUEST_REF_NUMBER "%s": Phiếu chưa được chi'%(request_ref_number)
                                    raise osv.except_osv(_('Warning!'), 'Phiếu chưa được chi')
                                if loai in ['Thu','thu'] and invoice['state']=='open':
                                    
                                    sql = '''
                                        select id from account_move_line where upper(ref)='%s' and upper(fusion_id)='%s'
                                    '''%(invoice['name'].upper(),data['TRANSACTION_NUMBER'].upper())
                                    cr.execute(sql)
                                    move_line_ids = [r[0] for r in cr.fetchall()]
                                    if move_line_ids:
                                        noidung_loi = 'REQUEST_REF_NUMBER "%s" đã được cấn trừ bởi Fusion "%s"'%(request_ref_number,data['TRANSACTION_NUMBER'])
                                        raise osv.except_osv(_('Cảnh báo!'), 'đã được cấn trừ')
                                    
                                    if (invoice['residual']+invoice['sotien_lai_conlai'])>sotiendathu:
                                        amount = sotiendathu
                                        sotien_tragopxe = sotiendathu
                                    else:
                                        amount = invoice['residual']+invoice['sotien_lai_conlai']
                                        sotien_tragopxe = invoice['residual']+invoice['sotien_lai_conlai']
                                        
                                    if not amount or sotiendathu<=0:
                                        break
                                    
                                    journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','cash'),('chinhanh_id','=',invoice['chinhanh_id'])])
                                    
                                    if not data['GL_DATE']:
                                        noidung_loi = 'REQUEST_REF_NUMBER "%s": Không tìm thấy ngày thanh toán'%(request_ref_number)
                                        raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy ngày thanh toán')
                                    ngay_thanh_toan=datetime.strptime(data['GL_DATE'],'%d/%m/%Y').strftime('%Y-%m-%d')
                                    
                                    sotientra = amount
                                    sotienlai = invoice['sotien_lai_conlai']
                                    if sotientra>=sotienlai:
                                        sotientra = sotientra-sotienlai
                                    else:
                                        sotientra = 0
                                    vals = {
                                        'amount': sotientra,
                                        
                                        'sotien_tragopxe': sotien_tragopxe,
                                        'sotien_lai_conlai': invoice['sotien_lai_conlai'],
                                        
                                        'partner_id': invoice['partner_id'],
                                        'reference': invoice['name'],
                                        'bai_giaoca_id': invoice['bai_giaoca_id'],
                                        'mlg_type': invoice['mlg_type'],
                                        'type': 'receipt',
                                        'chinhanh_id': invoice['chinhanh_id'],
                                        'journal_id': journal_ids[0],
                                        'date': ngay_thanh_toan,
                                        'fusion_id': data['TRANSACTION_NUMBER'],
                                        'loai_giaodich': 'Giao dịch cấn trừ từ ORACLE',
                                    }
                                    
                                    context = {
                                        'payment_expected_currency': invoice['currency_id'],
                                        'default_partner_id': invoice['partner_id'],
                                        'default_amount': sotientra,
                                        'default_reference': invoice['name'],
                                        'default_bai_giaoca_id': invoice['bai_giaoca_id'],
                                        'default_mlg_type': invoice['mlg_type'],
                                        'close_after_process': True,
                                        'invoice_type': invoice['type'],
                                        'invoice_id': invoice['id'],
                                        'default_type': 'receipt',
                                        'default_chinhanh_id': invoice['chinhanh_id'],
                                        'type': 'receipt',
                                        'loai_giaodich': 'Giao dịch cấn trừ từ ORACLE',
                                    }
                                    vals_onchange_partner = voucher_obj.onchange_partner_id(cr, uid, [],invoice['partner_id'],journal_ids[0],sotientra,invoice['currency_id'],'receipt',ngay_thanh_toan,context)['value']
                                    vals.update(vals_onchange_partner)
                                    vals.update(
                                        voucher_obj.onchange_journal(cr, uid, [],journal_ids[0],vals_onchange_partner['line_cr_ids'],False,invoice['partner_id'],ngay_thanh_toan,sotientra,'receipt',invoice['company_id'],context)['value']
                                    )
                                    line_cr_ids = []
                                    for l in vals['line_cr_ids']:
                                        line_cr_ids.append((0,0,l))
                                    vals.update({'line_cr_ids':line_cr_ids})
                                    voucher_id = voucher_obj.create(cr, uid, vals,context)
                                    voucher_obj.button_proforma_voucher(cr, uid, [voucher_id],context)
                                    
                                    sotiendathu = sotiendathu - amount
                            if sotiendathu>0:
                                noidung_loi='REQUEST_REF_NUMBER "%s": Số tiền đã thu/chi lớn hơn số tiền đề nghị phải thu/chi'%(request_ref_number)
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền đã thu/chi lớn hơn số tiền đề nghị phải thu/chi')
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+date_now+'/'+f_path.split('/')[-1],
                            'loai_giaodich': 'Fustion (ORACLE)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        cr.rollback()
                        if not noidung_loi:
                            noidung_loi = str(e).replace("'","''")
                            if request_ref_number:
                                noidung_loi = 'REQUEST_REF_NUMBER "%s": '%request_ref_number+noidung_loi
                        error_path = dir_path.name+ERROR
                        csvUti._moveFiles([f_path],error_path)
                        ngay = time.strftime('%Y-%m-%d %H:%M:%S')
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,ngay,1,ngay,ngay,
                             error_path+date_now+'/'+f_path.split('/')[-1],'Fustion (ORACLE)','Thu','Nhập','Tự động','Lỗi',noidung_loi
                        )
                        cr.execute(sql)
                        
                        body='''
                            <p>Ngày: %s</p>
                            <p>Tên file: %s</p>
                            <p>Loại giao dịch: %s</p>
                            <p>Ghi chú: %s</p>
                        '''%(ngay,error_path+date_now+'/'+f_path.split('/')[-1],'Fustion (ORACLE)',noidung_loi)
                        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID)
                        partner = user.partner_id
                        partner.signup_prepare()
                        post_values = {
                            'subject': 'Lỗi nhập tự động "Phải thu Fustion (ORACLE)"',
                            'body': body,
                            'partner_ids': [],
                            }
                        lead_email = partner.email
                        msg_id = self.pool.get('res.partner').message_post(cr, uid, [partner.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, lead_email, msg_id, context)
                        cr.commit()
#                         raise osv.except_osv(_('Warning!'), str(e))
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
        date_now = time.strftime('%Y-%m-%d')
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','fustion_phaitra')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+IMPORTING
                done_path = dir_path.name+DONE
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for data in file_data:
                            noidung_loi=''
                            request_ref_number = ''
                            try:
                                request_ref_number = str(data['REQUEST_REF_NUMBER'])
                            except Exception, e:
                                noidung_loi = 'REQUEST_REF_NUMBER "%s": không đúng định dạng'%(data['REQUEST_REF_NUMBER'])
                                raise osv.except_osv(_('Cảnh báo!'), 'REQUEST_REF_NUMBER không đúng định dạng')
                            
                            try:
                                st = float(data['ACCTD_AMOUNT'])
                            except Exception, e:
                                noidung_loi = 'REQUEST_REF_NUMBER "%s": Số tiền không đúng định dạng'%(request_ref_number)
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                            
                            sotiendathu = float(data['ACCTD_AMOUNT'])
                            if sotiendathu <= 0:
                                noidung_loi='REQUEST_REF_NUMBER "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(request_ref_number)
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            sql = '''
                                select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
                                    from account_invoice where upper(name)='%s' and state='open'
                                    order by date_invoice
                            '''%(request_ref_number.strip().upper())
                            cr.execute(sql)
                            invoices = cr.dictfetchall()
#                             if not invoices:
#                                 sql = '''
#                                     select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
#                                         from account_invoice where so_hoa_don='%s' and state='open' and type='in_invoice'
#                                         order by date_invoice
#                                 '''%(request_ref_number.strip())
#                                 cr.execute(sql)
#                                 invoices = cr.dictfetchall()
#                             if not invoices:
#                                 sql = '''
#                                     select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
#                                         from account_invoice where bien_so_xe_id in (select id from bien_so_xe where name='%s') and state='open' and type='in_invoice'
#                                         order by date_invoice
#                                 '''%(request_ref_number.strip())
#                                 cr.execute(sql)
#                                 invoices = cr.dictfetchall()
#                             if not invoices:
#                                 sql = '''
#                                     select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
#                                         from account_invoice where ma_bang_chiettinh_chiphi_sua='%s' and state='open' and type='in_invoice'
#                                         order by date_invoice
#                                 '''%(request_ref_number.strip())
#                                 cr.execute(sql)
#                                 invoices = cr.dictfetchall()
#                             if not invoices:
#                                 sql = '''
#                                     select id,partner_id,residual,name,bai_giaoca_id,mlg_type,type,chinhanh_id,currency_id,company_id
#                                         from account_invoice where so_hop_dong='%s' and state='open' and type='in_invoice'
#                                         order by date_invoice
#                                 '''%(request_ref_number.strip())
#                                 cr.execute(sql)
#                                 invoices = cr.dictfetchall()    
                            if not invoices:
                                noidung_loi='REQUEST_REF_NUMBER "%s": Không tìm thấy công nợ'%(request_ref_number)
                                raise osv.except_osv(_('Warning!'), 'Không tìm thấy công nợ')
                            
                            sotiendathu = float(data['ACCTD_AMOUNT'])
                            for invoice in invoices:
                                if invoice['residual']>sotiendathu:
                                    amount = sotiendathu
                                else:
                                    amount = invoice['residual']
                                if not amount or sotiendathu<=0:
                                    break
#                                 sql='''
#                                     update account_invoice set fusion_id='%s' where id=%s
#                                 '''%(data['TRANSACTION_NUMBER'],invoice['id'])
#                                 cr.execute(sql)
                                journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','cash'),('chinhanh_id','=',invoice['chinhanh_id'])])
                                
                                if not data['GL_DATE']:
                                    noidung_loi = 'REQUEST_REF_NUMBER "%s": Không tìm thấy ngày thanh toán'%(request_ref_number)
                                    raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy ngày thanh toán')
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
                                    'fusion_id': data['TRANSACTION_NUMBER'],
                                    'loai_giaodich': 'Giao dịch cấn trừ từ ORACLE',
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
                                voucher_id = voucher_obj.create(cr, uid, vals, context)
                                voucher_obj.button_proforma_voucher(cr, uid, [voucher_id], context)
                                sotiendathu = sotiendathu - amount
                            if sotiendathu>0:
                                noidung_loi='REQUEST_REF_NUMBER "%s": Số tiền đã thu lớn hơn số tiền đề nghị phải thu'%(request_ref_number)
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền đã thu lớn hơn số tiền đề nghị phải thu')
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+date_now+'/'+f_path.split('/')[-1],
                            'loai_giaodich': 'Fustion (ORACLE)',
                            'thu_tra': 'Trả',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        cr.rollback()
                        if not noidung_loi:
                            noidung_loi = str(e).replace("'","''")
                            if request_ref_number:
                                noidung_loi = 'REQUEST_REF_NUMBER "%s": '%request_ref_number+noidung_loi
                        error_path = dir_path.name+ERROR
                        csvUti._moveFiles([f_path],error_path)
                        ngay = time.strftime('%Y-%m-%d %H:%M:%S')
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,ngay,1,ngay,ngay,
                             error_path+date_now+'/'+f_path.split('/')[-1],'Fustion (ORACLE)','Trả','Nhập','Tự động','Lỗi',noidung_loi
                        )
                        cr.execute(sql)
                        
                        body='''
                            <p>Ngày: %s</p>
                            <p>Tên file: %s</p>
                            <p>Loại giao dịch: %s</p>
                            <p>Ghi chú: %s</p>
                        '''%(ngay,error_path+date_now+'/'+f_path.split('/')[-1],'Fustion (ORACLE)',noidung_loi)
                        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID)
                        partner = user.partner_id
                        partner.signup_prepare()
                        post_values = {
                            'subject': 'Lỗi nhập tự động "Phải trả Fustion (ORACLE)"',
                            'body': body,
                            'partner_ids': [],
                            }
                        lead_email = partner.email
                        msg_id = self.pool.get('res.partner').message_post(cr, uid, [partner.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, lead_email, msg_id, context)
                        cr.commit()
#                         raise osv.except_osv(_('Warning!'), str(e))
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
        date_now = time.strftime('%Y-%m-%d')
        try:
            import_ids = import_obj.search(cr, uid, [('mlg_type','=','chi_ho')])

            for dir_path in import_obj.browse(cr, uid, import_ids):
                path = dir_path.name+IMPORTING
                done_path = dir_path.name+DONE
    
                csvUti = lib_csv.csv_ultilities()
                for file_name in csvUti._read_files_folder(path):
                    f_path = file_name
                    seq = False
                    try:
                        file_data = csvUti._read_file(f_path)
                    
                        for seq,data in enumerate(file_data):
                            noidung_loi=''
                            try:
                                st = float(data['so_tien'])
                            except Exception, e:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không đúng định dạng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                            if float(data['so_tien']) <= 0:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                            vals={}
                            account_id = False
                            sql = '''
                                select id from account_account where upper(code)='%s' limit 1
                            '''%(data['ma_chi_nhanh'].upper())
                            cr.execute(sql)
                            chinhanh_ids = cr.fetchone()
                            if not chinhanh_ids:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy chi nhánh'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy chi nhánh')
                            
                            sql = '''
                                select id,bai_giaoca_id,account_ht_id,cmnd,giayphep_kinhdoanh,taixe,nhadautu,nhanvienvanphong,chinhanh_id
                                    from res_partner where upper(ma_doi_tuong)='%s' limit 1
                            '''%(data['ma_doi_tuong'].upper())
                            cr.execute(sql)
                            partner = cr.dictfetchone()
                            if not partner:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy đối tượng')
                            partner_id = partner and partner['id'] or False
                            bai_giaoca_id = partner and partner['bai_giaoca_id'] or False
                            
                            loai_doituong=''
                            if partner['taixe']==True:
                                if chinhanh_ids[0]!=partner['chinhanh_id']:
                                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của đối tượng')
                                loai_doituong='taixe'
                                account_id = partner and partner['account_ht_id'] or False
                            if partner['nhanvienvanphong']==True:
                                if chinhanh_ids[0]!=partner['chinhanh_id']:
                                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                    raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của đối tượng')
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
                            sql = ''' select id from bien_so_xe where upper(name)='%s' '''%(bsx.upper())
                            cr.execute(sql)
                            bien_so_xe_ids = cr.fetchone()
                            if bsx and not bien_so_xe_ids:
                                noidung_loi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy biển số xe'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy biển số xe')
                            
                            if not data['ngay_giao_dich']:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy ngày giao dịch'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy ngày giao dịch')
                            date_invoice=datetime.strptime(data['ngay_giao_dich'],'%d/%m/%Y').strftime('%Y-%m-%d')
                            
                            vals.update({
                                'mlg_type': 'chi_ho',
                                'type': 'in_invoice',
                                'account_id': account_id,
                                'chinhanh_id': chinhanh_ids and chinhanh_ids[0] or False,
                                'loai_doituong': loai_doituong,
                                'partner_id': partner_id,
                                'date_invoice': date_invoice,
                                'so_hop_dong': data['so_hop_dong'],
                                'so_tien': float(data['so_tien']),
                                'dien_giai': data['dien_giai'],
                                'journal_id': journal_ids and journal_ids[0] or False,
                                'bai_giaoca_id': bai_giaoca_id,
                                'bien_so_xe_id': bien_so_xe_ids and bien_so_xe_ids[0] or False,
                                'loai_giaodich': 'Giao dịch nhập từ HTKD',
                            })
                            invoice_vals = invoice_obj.onchange_dien_giai_st(cr, uid, [], data['dien_giai'], data['so_tien'], journal_ids and journal_ids[0] or False, context)['value']
                            vals.update(invoice_vals)
                            invoice_id = invoice_obj.create(cr, uid, vals)
                            wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
                        csvUti._moveFiles([f_path],done_path)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': done_path+date_now+'/'+f_path.split('/')[-1],
                            'loai_giaodich': 'Chi góp xe (HTKD)',
                            'thu_tra': 'Trả',
                            'nhap_xuat': 'Nhập',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    except Exception, e:
                        cr.rollback()
                        if not noidung_loi:
                            noidung_loi = str(e).replace("'","''")
                            if seq:
                                noidung_loi = 'Dòng "%s": '%(seq+2) + noidung_loi
                        error_path = dir_path.name+ERROR
                        csvUti._moveFiles([f_path],error_path)
                        ngay = time.strftime('%Y-%m-%d %H:%M:%S')
                        sql = '''
                            insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                            values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                            commit;
                        '''%(
                             1,ngay,1,ngay,ngay,
                             error_path+date_now+'/'+f_path.split('/')[-1],'Chi góp xe (HTKD)','Trả','Nhập','Tự động','Lỗi',noidung_loi
                        )
                        cr.execute(sql)
                        
                        body='''
                            <p>Ngày: %s</p>
                            <p>Tên file: %s</p>
                            <p>Loại giao dịch: %s</p>
                            <p>Ghi chú: %s</p>
                        '''%(ngay,error_path+date_now+'/'+f_path.split('/')[-1],'Chi góp xe (HTKD)',noidung_loi)
                        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID)
                        partner = user.partner_id
                        partner.signup_prepare()
                        post_values = {
                            'subject': 'Lỗi nhập tự động "Chi góp xe (HTKD)"',
                            'body': body,
                            'partner_ids': [],
                            }
                        lead_email = partner.email
                        msg_id = self.pool.get('res.partner').message_post(cr, uid, [partner.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, lead_email, msg_id, context)
                        cr.commit()
#                         raise osv.except_osv(_('Warning!'), str(e))
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
import_congno_tudong()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
