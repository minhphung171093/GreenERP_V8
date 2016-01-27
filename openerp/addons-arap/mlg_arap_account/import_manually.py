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
from datetime import datetime, timedelta
import logging
from openerp.addons.mlg_arap_account import lib_csv
from openerp import netsvc
from glob import glob
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)
IMPORTING = '/importing/'
DONE = '/done/'
ERROR = '/error/'
class import_congno_manually(osv.osv):
    _name = 'import.congno.manually'
    _order = 'name desc'
    
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
        super(import_congno_manually, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True

    _columns = {
        'name': fields.date('Ngày', required=False,states={'done': [('readonly', True)]}),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='Chọn tập tin', type="binary", nodrop=True,states={'done': [('readonly', True)]}),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'state':fields.selection([('draft', 'Mới tạo'),('done', 'Đã xử lý')],'Trạng thái', readonly=True),
        'mlg_type': fields.selection([('no_doanh_thu','Nợ DT-BH-AL'),
                                      ('chi_ho_dien_thoai','Chi hộ điện thoại'),
                                      ('phai_thu_bao_hiem','Phải thu bảo hiểm'),
                                      ('phai_thu_ky_quy','Phải thu ký quỹ'),
                                      ('phat_vi_pham','Phạt vi phạm'),
                                      ('thu_no_xuong','Thu nợ xưởng'),
                                      ('thu_phi_thuong_hieu','Thu phí thương hiệu'),
                                      ('tra_gop_xe','Trả góp xe'),
                                      ('hoan_tam_ung','Hoàn tạm ứng'),
                                      ('chi_no_doanh_thu','Chi nợ doanh thu'),
                                      ('chi_dien_thoai','Chi điện thoại'),
                                      ('chi_bao_hiem','Chi bảo hiểm'),
                                      ('phai_tra_ky_quy','Phải trả ký quỹ'),
                                      ('tam_ung','Tạm ứng'),
                                      ('chi_ho','Chi hộ'),],'Loại công nợ', readonly=True, states={'draft': [('readonly', False)]}),
    }
    
    _defaults = {
        'state':'draft',
        'name': time.strftime('%Y-%m-%d'),
    }
    
    def bt_import_phaithu_nodoanhthu(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        import_obj = self.pool.get('cauhinh.thumuc.import')
        invoice_obj = self.pool.get('account.invoice')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        user = self.pool.get('res.users').browse(cr, uid, uid)
        noidungloi = ''
        wf_service = netsvc.LocalService("workflow")
        if context.get('import_loai_congno',False):
            try:
                import_ids = import_obj.search(cr, uid, [('mlg_type','=',context['import_loai_congno'])])
                if not import_ids:
                    noidungloi = 'Chưa cấu hình thư mục để nhập vào'
                    raise osv.except_osv(_('Cảnh báo!'), 'Chưa cấu hình thư mục để nhập vào')
                dir_path = import_obj.browse(cr, uid, import_ids[0]).name
                path = dir_path+IMPORTING
                done_path = dir_path+DONE
                bin_value = (this.datas).decode('base64')
                f_name = this.datas_fname and (this.datas_fname[:-4]+'_'+time.strftime('%Y%m%d%H%M%S')+this.datas_fname[-4:]) or ''
                file_path = path+f_name
                open(file_path,'wb').write(bin_value)
                
                csvUti = lib_csv.csv_ultilities()
                seq = False
                try:
                    file_data = csvUti._read_file(file_path)
                
                    for seq,data in enumerate(file_data):
                        vals = {}
                        try:
                            st = float(data['so_tien'])
                        except Exception, e:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không đúng định dạng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                        if float(data['so_tien']) <= 0:
                            noidungloi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                        sql = '''
                            select id from account_account where upper(code)='%s' limit 1
                        '''%(data['ma_chi_nhanh'].upper())
                        cr.execute(sql)
                        chinhanh_ids = cr.fetchone()
                        if not chinhanh_ids:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy chi nhánh'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy chi nhánh')
                        if user.chinhanh_id.id != chinhanh_ids[0]:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của user đang đăng nhập'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của user đang đăng nhập')
                        sql = '''
                            select id,bai_giaoca_id,account_ht_id,cmnd,giayphep_kinhdoanh,taixe,nhadautu,nhanvienvanphong,chinhanh_id
                                from res_partner where upper(ma_doi_tuong)='%s' limit 1
                        '''%(data['ma_doi_tuong'].upper())
                        cr.execute(sql)
                        partner = cr.dictfetchone()
                        if not partner:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy đối tượng')
                        partner_id = partner and partner['id'] or False
                        bai_giaoca_id = partner and partner['bai_giaoca_id'] or False
                        
                        loai_doituong=''
                        if partner['taixe']==True:
                            if chinhanh_ids[0]!=partner['chinhanh_id']:
                                noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của đối tượng')
                            loai_doituong='taixe'
                            account_id = partner and partner['account_ht_id'] or False
                        if partner['nhanvienvanphong']==True:
                            if chinhanh_ids[0]!=partner['chinhanh_id']:
                                noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
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
                            if not account_ids:
                                noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của đối tượng')
                            account_id = account_ids and account_ids[0] or False
                            vals.update({'cmnd': partner['cmnd'],'giayphep_kinhdoanh': partner['giayphep_kinhdoanh'],'chinhanh_ndt_id':chinhanh_ids[0]})
                        
                        if loai_doituong not in ['taixe','nhanvienvanphong']:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Loại đối tượng cho công nợ "Nợ DT-BH-AL" chỉ được tạo cho "Lái xe" hoặc "Nhân viên văn phòng"'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Loại đối tượng cho công nợ "Nợ DT-BH-AL" chỉ được tạo cho "Lái xe" hoặc "Nhân viên văn phòng"')
                        
                        journal_ids = self.pool.get('account.journal').search(cr, uid, [('code','=','TG')])
                        if not journal_ids:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy journal trung gian'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy journal trung gian')
                        
                        loai_dt_bh_al = data['loai_dt_bh_al']
                        if not loai_dt_bh_al:
                            noidungloi='Không tìm thấy loại DT-BH-AL trên template'
                            raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy loại DT-BH-AL trên template')
                        if loai_doituong=='nhanvienvanphong' and loai_dt_bh_al.upper()=='NO_DOANH_THU':
                            noidungloi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Loại DT-BH-AL "Nợ doanh thu" chỉ dành cho đối tượng lái xe'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Loại DT-BH-AL "Nợ doanh thu" chỉ dành cho đối tượng lái xe')
                        sql = ''' select id from loai_no_doanh_thu where upper(code)='%s' '''%(loai_dt_bh_al.upper())
                        cr.execute(sql)
                        loai_dt_bh_al_ids = cr.fetchone()
                        if loai_dt_bh_al and not loai_dt_bh_al_ids:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy loại DT-BH-AL'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy loại DT-BH-AL')
                        
                        if not data['ngay_giao_dich']:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy ngày giao dịch'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy ngày giao dịch')
                        
                        vals.update({
                            'mlg_type': 'no_doanh_thu',
                            'type': 'out_invoice',
                            'account_id': account_id,
                            'chinhanh_id': chinhanh_ids and chinhanh_ids[0] or False,
                            'loai_doituong': loai_doituong,
                            'partner_id': partner_id,
                            'date_invoice': datetime.strptime(data['ngay_giao_dich'],'%d/%m/%Y').strftime('%Y-%m-%d'),
                            'so_tien': float(data['so_tien']),
                            'dien_giai': data['dien_giai'],
                            'loai_nodoanhthu_id': loai_dt_bh_al_ids and loai_dt_bh_al_ids[0] or False,
                            'journal_id': journal_ids and journal_ids[0] or False,
                            'bai_giaoca_id': bai_giaoca_id,
                            'loai_giaodich': 'Giao dịch nhập từ file',
                        })
                        invoice_vals = invoice_obj.onchange_dien_giai_st(cr, uid, [], data['dien_giai'], data['so_tien'], journal_ids and journal_ids[0] or False, context)['value']
                        vals.update(invoice_vals)
                        invoice_id = invoice_obj.create(cr, uid, vals)
                        wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
                    csvUti._moveFiles([file_path],done_path)
                    lichsu_obj.create(cr, uid, {
                        'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'ten_file': done_path+f_name,
                        'loai_giaodich': 'Nợ DT-BH-AL',
                        'thu_tra': 'Thu',
                        'nhap_xuat': 'Nhập',
                        'tudong_bangtay': 'Bằng tay',
                        'trang_thai': 'Thành công',
                        'noidung_loi': '',
                    })
                except Exception, e:
                    cr.rollback()
                    if not noidungloi:
                        noidungloi = str(e).replace("'","''")
                        if seq:
                            noidungloi = 'Dòng "%s": '%(seq+2) + noidungloi
                    error_path = dir_path+ERROR
                    csvUti._moveFiles([file_path],error_path)
                    sql = '''
                        insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                        values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                        commit;
                    '''%(
                         1,time.strftime('%Y-%m-%d %H:%M:%S'),1,time.strftime('%Y-%m-%d %H:%M:%S'),time.strftime('%Y-%m-%d %H:%M:%S'),
                         error_path+f_name.split('/')[-1],'Nợ DT-BH-AL','Thu','Nhập','Bằng tay','Lỗi',noidungloi
                    )
                    cr.execute(sql)
                    cr.commit()
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e))
        return self.write(cr, uid, ids, {'state':'done'})
    
    def bt_import_thuchi_ho_dienthoai(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        import_obj = self.pool.get('cauhinh.thumuc.import')
        invoice_obj = self.pool.get('account.invoice')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        user = self.pool.get('res.users').browse(cr, uid, uid)
        noidungloi = ''
        wf_service = netsvc.LocalService("workflow")
        if context.get('import_loai_congno',False):
            try:
                import_ids = import_obj.search(cr, uid, [('mlg_type','=',context['import_loai_congno'])])
                if not import_ids:
                    noidungloi = 'Chưa cấu hình thư mục để nhập vào'
                    raise osv.except_osv(_('Cảnh báo!'), 'Chưa cấu hình thư mục để nhập vào')
                dir_path = import_obj.browse(cr, uid, import_ids[0]).name
                path = dir_path+IMPORTING
                done_path = dir_path+DONE
                bin_value = (this.datas).decode('base64')
                f_name = this.datas_fname and (this.datas_fname[:-4]+'_'+time.strftime('%Y%m%d%H%M%S')+this.datas_fname[-4:]) or ''
                file_path = path+f_name
                open(file_path,'wb').write(bin_value)
                
                csvUti = lib_csv.csv_ultilities()
                seq = False
                try:
                    file_data = csvUti._read_file(file_path)
                
                    for seq,data in enumerate(file_data):
                        vals = {}
                        try:
                            st = float(data['so_tien'])
                        except Exception, e:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không đúng định dạng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                        if float(data['so_tien']) <= 0:
                            noidungloi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                        sql = '''
                            select id from account_account where upper(code)='%s' limit 1
                        '''%(data['ma_chi_nhanh'].upper())
                        cr.execute(sql)
                        chinhanh_ids = cr.fetchone()
                        if not chinhanh_ids:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy chi nhánh'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy chi nhánh')
                        if user.chinhanh_id.id != chinhanh_ids[0]:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của user đang đăng nhập'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của user đang đăng nhập')
                        sql = '''
                            select id,bai_giaoca_id,account_ht_id,cmnd,giayphep_kinhdoanh,taixe,nhadautu,nhanvienvanphong,chinhanh_id
                                from res_partner where upper(ma_doi_tuong)='%s' limit 1
                        '''%(data['ma_doi_tuong'].upper())
                        cr.execute(sql)
                        partner = cr.dictfetchone()
                        if not partner:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy đối tượng')
                        partner_id = partner and partner['id'] or False
                        bai_giaoca_id = partner and partner['bai_giaoca_id'] or False
                        
                        loai_doituong=''
                        if partner['taixe']==True:
                            if chinhanh_ids[0]!=partner['chinhanh_id']:
                                noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của đối tượng')
                            loai_doituong='taixe'
                            account_id = partner and partner['account_ht_id'] or False
                        if partner['nhanvienvanphong']==True:
                            if chinhanh_ids[0]!=partner['chinhanh_id']:
                                noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
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
                            if not account_ids:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của đối tượng')
                            account_id = account_ids and account_ids[0] or False
                            vals.update({'cmnd': partner['cmnd'],'giayphep_kinhdoanh': partner['giayphep_kinhdoanh'],'chinhanh_ndt_id':chinhanh_ids[0]})
                            
                        if loai_doituong not in ['taixe','nhanvienvanphong']:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Loại đối tượng cho công nợ "Phải thu chi hộ điện thoại" chỉ được tạo cho "Lái xe" hoặc "Nhân viên văn phòng"'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Loại đối tượng cho công nợ "Phải thu chi hộ điện thoại" chỉ được tạo cho "Lái xe" hoặc "Nhân viên văn phòng"')
                            
                        journal_ids = self.pool.get('account.journal').search(cr, uid, [('code','=','TG')])
                        if not journal_ids:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy journal trung gian'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy journal trung gian')
                        
                        if not data['ngay_giao_dich']:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy ngày giao dịch'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy ngày giao dịch')
                        vals.update({
                            'mlg_type': 'chi_ho_dien_thoai',
                            'type': 'out_invoice',
                            'account_id': account_id,
                            'chinhanh_id': chinhanh_ids and chinhanh_ids[0] or False,
                            'loai_doituong': loai_doituong,
                            'partner_id': partner_id,
                            'date_invoice': datetime.strptime(data['ngay_giao_dich'],'%d/%m/%Y').strftime('%Y-%m-%d'),
                            'so_hoa_don': data['so_hoa_don'],
                            'so_dien_thoai': data['so_dien_thoai'],
                            'so_tien': float(data['so_tien']),
                            'dien_giai': data['dien_giai'],
                            'journal_id': journal_ids and journal_ids[0] or False,
                            'bai_giaoca_id': bai_giaoca_id,
                            'loai_giaodich': 'Giao dịch nhập từ file',
                        })
                        invoice_vals = invoice_obj.onchange_dien_giai_st(cr, uid, [], data['dien_giai'], data['so_tien'], journal_ids and journal_ids[0] or False, context)['value']
                        vals.update(invoice_vals)
                        invoice_id = invoice_obj.create(cr, uid, vals)
#                         wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
                    csvUti._moveFiles([file_path],done_path)
                    lichsu_obj.create(cr, uid, {
                        'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'ten_file': done_path+f_name,
                        'loai_giaodich': 'Phải thu chi hộ điện thoại',
                        'thu_tra': 'Thu',
                        'nhap_xuat': 'Nhập',
                        'tudong_bangtay': 'Bằng tay',
                        'trang_thai': 'Thành công',
                        'noidung_loi': '',
                    })
                except Exception, e:
                    cr.rollback()
                    if not noidungloi:
                        noidungloi = str(e).replace("'","''")
                        if seq:
                            noidungloi = 'Dòng "%s": '%(seq+2) + noidungloi
                    error_path = dir_path+ERROR
                    csvUti._moveFiles([file_path],error_path)
                    sql = '''
                        insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                        values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                        commit;
                    '''%(
                         1,time.strftime('%Y-%m-%d %H:%M:%S'),1,time.strftime('%Y-%m-%d %H:%M:%S'),time.strftime('%Y-%m-%d %H:%M:%S'),
                         error_path+f_name.split('/')[-1],'Phải thu chi hộ điện thoại','Thu','Nhập','Bằng tay','Lỗi',noidungloi
                    )
                    cr.execute(sql)
                    cr.commit()
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e))
        return self.write(cr, uid, ids, {'state':'done'})
    
    def bt_import_phaithu_baohiem(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        import_obj = self.pool.get('cauhinh.thumuc.import')
        invoice_obj = self.pool.get('account.invoice')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        user = self.pool.get('res.users').browse(cr, uid, uid)
        wf_service = netsvc.LocalService("workflow")
        noidungloi = ''
        if context.get('import_loai_congno',False):
            try:
                import_ids = import_obj.search(cr, uid, [('mlg_type','=',context['import_loai_congno'])])
                if not import_ids:
                    noidungloi = 'Chưa cấu hình thư mục để nhập vào'
                    raise osv.except_osv(_('Cảnh báo!'), 'Chưa cấu hình thư mục để nhập vào')
                dir_path = import_obj.browse(cr, uid, import_ids[0]).name
                path = dir_path+IMPORTING
                done_path = dir_path+DONE
                bin_value = (this.datas).decode('base64')
                f_name = this.datas_fname and (this.datas_fname[:-4]+'_'+time.strftime('%Y%m%d%H%M%S')+this.datas_fname[-4:]) or ''
                file_path = path+f_name
                open(file_path,'wb').write(bin_value)
                
                csvUti = lib_csv.csv_ultilities()
                seq = False
                try:
                    file_data = csvUti._read_file(file_path)
                
                    for seq,data in enumerate(file_data):
                        try:
                            st = float(data['so_tien'])
                        except Exception, e:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không đúng định dạng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                        if float(data['so_tien']) <= 0:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                        vals = {}
                        sql = '''
                            select id from account_account where upper(code)='%s' limit 1
                        '''%(data['ma_chi_nhanh'].upper())
                        cr.execute(sql)
                        chinhanh_ids = cr.fetchone()
                        if not chinhanh_ids:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy chi nhánh'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy chi nhánh')
                        
                        if user.chinhanh_id.id != chinhanh_ids[0]:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của user đang đăng nhập'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của user đang đăng nhập')
                        
                        sql = '''
                            select id,bai_giaoca_id,account_ht_id,cmnd,giayphep_kinhdoanh,taixe,nhadautu,nhanvienvanphong,chinhanh_id
                                from res_partner where upper(ma_doi_tuong)='%s' limit 1
                        '''%(data['ma_doi_tuong'].upper())
                        cr.execute(sql)
                        partner = cr.dictfetchone()
                        if not partner:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy đối tượng')
                        partner_id = partner and partner['id'] or False
                        bai_giaoca_id = partner and partner['bai_giaoca_id'] or False
                        
                        loai_doituong=''
                        if partner['taixe']==True:
                            if chinhanh_ids[0]!=partner['chinhanh_id']:
                                noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của đối tượng')
                            loai_doituong='taixe'
                            account_id = partner and partner['account_ht_id'] or False
                        if partner['nhanvienvanphong']==True:
                            if chinhanh_ids[0]!=partner['chinhanh_id']:
                                noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
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
                            if not account_ids:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của đối tượng')
                            account_id = account_ids and account_ids[0] or False
                            vals.update({'cmnd': partner['cmnd'],'giayphep_kinhdoanh': partner['giayphep_kinhdoanh'],'chinhanh_ndt_id':chinhanh_ids[0]})
                            
                        if loai_doituong not in ['nhadautu']:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Loại đối tượng cho công nợ "Phải thu bảo hiểm" chỉ được tạo cho "Nhà đầu tư"'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Loại đối tượng cho công nợ "Phải thu bảo hiểm" chỉ được tạo cho "Nhà đầu tư"')
                            
                        journal_ids = self.pool.get('account.journal').search(cr, uid, [('code','=','TG')])
                        if not journal_ids:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy journal trung gian'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy journal trung gian')
                        
                        bsx = data['bien_so_xe']
                        sql = ''' select id from bien_so_xe where upper(name)='%s' '''%(bsx.upper())
                        cr.execute(sql)
                        bien_so_xe_ids = cr.fetchone()
                        if bsx and not bien_so_xe_ids:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy biển số xe'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy biển số xe')
                        
                        lbh = data['loai_bao_hiem']
                        if not lbh:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chưa nhập thông tin loại bảo hiểm'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Chưa nhập thông tin loại bảo hiểm')
                        sql = ''' select id from loai_bao_hiem where upper(code)='%s' '''%(lbh.upper())
                        cr.execute(sql)
                        loai_bao_hiem_ids = cr.fetchone()
                        if lbh and not loai_bao_hiem_ids:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy loại bảo hiểm'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy loại bảo hiểm')
                        
                        if not data['ngay_giao_dich']:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy ngày giao dịch'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy ngày giao dịch')
                        vals.update({
                            'mlg_type': 'phai_thu_bao_hiem',
                            'type': 'out_invoice',
                            'chinhanh_id': chinhanh_ids and chinhanh_ids[0] or False,
                            'account_id': account_id,
                            'loai_doituong': loai_doituong,
                            'partner_id': partner_id,
                            'date_invoice': datetime.strptime(data['ngay_giao_dich'],'%d/%m/%Y').strftime('%Y-%m-%d'),
                            'so_hoa_don': data['so_hoa_don'],
                            'bien_so_xe_id': bien_so_xe_ids and bien_so_xe_ids[0] or False,
                            'so_tien': float(data['so_tien']),
                            'dien_giai': data['dien_giai'],
                            'journal_id': journal_ids and journal_ids[0] or False,
                            'loai_giaodich': 'Giao dịch nhập từ file',
                            'loai_baohiem_id': loai_bao_hiem_ids and loai_bao_hiem_ids[0] or False,
                        })
                        invoice_vals = invoice_obj.onchange_dien_giai_st(cr, uid, [], data['dien_giai'], data['so_tien'], journal_ids and journal_ids[0] or False, context)['value']
                        vals.update(invoice_vals)
                        invoice_id = invoice_obj.create(cr, uid, vals)
#                         wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
                    csvUti._moveFiles([file_path],done_path)
                    lichsu_obj.create(cr, uid, {
                        'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'ten_file': done_path+f_name,
                        'loai_giaodich': 'Phải thu bảo hiểm',
                        'thu_tra': 'Thu',
                        'nhap_xuat': 'Nhập',
                        'tudong_bangtay': 'Bằng tay',
                        'trang_thai': 'Thành công',
                        'noidung_loi': '',
                    })
                except Exception, e:
                    cr.rollback()
                    if not noidungloi:
                        noidungloi = str(e).replace("'","''")
                        if seq:
                            noidungloi = 'Dòng "%s": '%(seq+2) + noidungloi
                    error_path = dir_path+ERROR
                    csvUti._moveFiles([file_path],error_path)
                    sql = '''
                        insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                        values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                        commit;
                    '''%(
                         1,time.strftime('%Y-%m-%d %H:%M:%S'),1,time.strftime('%Y-%m-%d %H:%M:%S'),time.strftime('%Y-%m-%d %H:%M:%S'),
                         error_path+f_name.split('/')[-1],'Phải thu bảo hiểm','Thu','Nhập','Bằng tay','Lỗi',noidungloi
                    )
                    cr.execute(sql)
                    cr.commit()
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e))
        return self.write(cr, uid, ids, {'state':'done'})

    def bt_import_phaithu_noxuong(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        import_obj = self.pool.get('cauhinh.thumuc.import')
        invoice_obj = self.pool.get('account.invoice')
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        user = self.pool.get('res.users').browse(cr, uid, uid)
        noidungloi = ''
        wf_service = netsvc.LocalService("workflow")
        if context.get('import_loai_congno',False):
            try:
                import_ids = import_obj.search(cr, uid, [('mlg_type','=',context['import_loai_congno'])])
                if not import_ids:
                    noidungloi = 'Chưa cấu hình thư mục để nhập vào'
                    raise osv.except_osv(_('Cảnh báo!'), 'Chưa cấu hình thư mục để nhập vào')
                dir_path = import_obj.browse(cr, uid, import_ids[0]).name
                path = dir_path+IMPORTING
                done_path = dir_path+DONE
                bin_value = (this.datas).decode('base64')
                f_name = this.datas_fname and (this.datas_fname[:-4]+'_'+time.strftime('%Y%m%d%H%M%S')+this.datas_fname[-4:]) or ''
                file_path = path+f_name
                open(file_path,'wb').write(bin_value)
                
                csvUti = lib_csv.csv_ultilities()
                seq = False
                try:
                    file_data = csvUti._read_file(file_path)
                
                    for seq,data in enumerate(file_data):
                        try:
                            st = float(data['so_tien'])
                        except Exception, e:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không đúng định dạng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không đúng định dạng')
                        if float(data['so_tien']) <= 0:
                            noidungloi='Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền không được phép nhỏ hơn hoặc bằng 0'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Số tiền không được phép nhỏ hơn hoặc bằng 0')
                        account_id = False
                        vals = {}
                        sql = '''
                            select id from account_account where upper(code)='%s' limit 1
                        '''%(data['ma_chi_nhanh'].upper())
                        cr.execute(sql)
                        chinhanh_ids = cr.fetchone()
                        if not chinhanh_ids:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy chi nhánh'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy chi nhánh')
                        
                        if user.chinhanh_id.id != chinhanh_ids[0]:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của user đang đăng nhập'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của user đang đăng nhập')
                        
                        sql = '''
                            select id,bai_giaoca_id,account_ht_id,cmnd,giayphep_kinhdoanh,taixe,nhadautu,nhanvienvanphong,chinhanh_id
                                from res_partner where upper(ma_doi_tuong)='%s' limit 1
                        '''%(data['ma_doi_tuong'].upper())
                        cr.execute(sql)
                        partner = cr.dictfetchone()
                        if not partner:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy đối tượng')
                        partner_id = partner and partner['id'] or False
                        bai_giaoca_id = partner and partner['bai_giaoca_id'] or False
                        
                        loai_doituong=''
                        if partner['taixe']==True:
                            if chinhanh_ids[0]!=partner['chinhanh_id']:
                                noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của đối tượng')
                            loai_doituong='taixe'
                            account_id = partner and partner['account_ht_id'] or False
                        if partner['nhanvienvanphong']==True:
                            if chinhanh_ids[0]!=partner['chinhanh_id']:
                                noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
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
                            if not account_ids:
                                noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                                raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của đối tượng')
                            account_id = account_ids and account_ids[0] or False
                            vals.update({'cmnd': partner['cmnd'],'giayphep_kinhdoanh': partner['giayphep_kinhdoanh'],'chinhanh_ndt_id':chinhanh_ids[0]})
                            
                        journal_ids = self.pool.get('account.journal').search(cr, uid, [('code','=','TG')])
                        if not journal_ids:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy journal trung gian'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy journal trung gian')
                         
                        bsx = data['bien_so_xe']
                        sql = ''' select id from bien_so_xe where upper(name)='%s' '''%(bsx.upper())
                        cr.execute(sql)
                        bien_so_xe_ids = cr.fetchone()
                        if bsx and not bien_so_xe_ids:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy biển số xe'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy biển số xe')
                        
                        mx = data['ma_xuong']
                        sql = ''' select id from ma_xuong where upper(code)='%s' '''%(mx.upper())
                        cr.execute(sql)
                        ma_xuong_ids = cr.fetchone()
                        if mx and not ma_xuong_ids:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy mã xưởng'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy mã xưởng')
                        
                        if not data['ngay_giao_dich']:
                            noidungloi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy ngày giao dịch'%(seq+2,data['ma_doi_tuong'],data['ma_chi_nhanh'])
                            raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy ngày giao dịch')
                        vals.update({
                            'mlg_type': 'thu_no_xuong',
                            'type': 'out_invoice',
                            'account_id': account_id,
                            'chinhanh_id': chinhanh_ids and chinhanh_ids[0] or False,
                            'loai_doituong': loai_doituong,
                            'partner_id': partner_id,
                            'date_invoice': datetime.strptime(data['ngay_giao_dich'],'%d/%m/%Y').strftime('%Y-%m-%d'),
                            'so_hop_dong': data['so_hop_dong'],
                            'ma_bang_chiettinh_chiphi_sua': data['ma_chiet_tinh'],
                            'so_tien': data['so_tien'],
                            'dien_giai': data['dien_giai'],
                            'journal_id': journal_ids and journal_ids[0] or False,
                            'bai_giaoca_id': bai_giaoca_id,
                            'bien_so_xe_id': bien_so_xe_ids and bien_so_xe_ids[0] or False,
                            'ma_xuong_id': ma_xuong_ids and ma_xuong_ids[0] or False,
                            'loai_giaodich': 'Giao dịch nhập từ file',
                        })
                        
                        invoice_vals = invoice_obj.onchange_dien_giai_st(cr, uid, [], data['dien_giai'], data['so_tien'], journal_ids and journal_ids[0] or False, context)['value']
                        vals.update(invoice_vals)
                        invoice_id = invoice_obj.create(cr, uid, vals)
#                         wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
                    csvUti._moveFiles([file_path],done_path)
                    lichsu_obj.create(cr, uid, {
                        'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'ten_file': done_path+f_name,
                        'loai_giaodich': 'Thu nợ xưởng',
                        'thu_tra': 'Thu',
                        'nhap_xuat': 'Nhập',
                        'tudong_bangtay': 'Bằng tay',
                        'trang_thai': 'Thành công',
                        'noidung_loi': '',
                    })
                except Exception, e:
                    cr.rollback()
                    if not noidungloi:
                        noidungloi = str(e).replace("'","''")
                        if seq:
                            noidungloi = 'Dòng "%s": '%(seq+2) + noidungloi
                    error_path = dir_path+ERROR
                    csvUti._moveFiles([file_path],error_path)
                    sql = '''
                        insert into lichsu_giaodich(id,create_uid,create_date,write_uid,write_date,name,ten_file,loai_giaodich,thu_tra,nhap_xuat,tudong_bangtay,trang_thai,noidung_loi)
                        values (nextval('lichsu_giaodich_id_seq'),%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s');
                        commit;
                    '''%(
                         1,time.strftime('%Y-%m-%d %H:%M:%S'),1,time.strftime('%Y-%m-%d %H:%M:%S'),time.strftime('%Y-%m-%d %H:%M:%S'),
                         error_path+f_name.split('/')[-1],'Thu nợ xưởng','Thu','Nhập','Bằng tay','Lỗi',noidungloi
                    )
                    cr.execute(sql)
                    cr.commit()
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e))
        return self.write(cr, uid, ids, {'state':'done'})
    
import_congno_manually()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
