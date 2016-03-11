# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import datetime
import base64
from openerp.addons.mlg_arap_account import lib_csv
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class arap_import_kyquy_congviec(osv.osv):
    _name = 'arap.import.kyquy.congviec'
    
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
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'hr_identities_attachment.location')
        file_size = len(value.decode('base64'))
        if location:
            attach = self.browse(cr, uid, id, context=context)
            if attach.store_fname:
                self._file_delete(cr, uid, location, attach.store_fname)
            fname = self._file_write(cr, uid, location, value)
            # SUPERUSER_ID as probably don't have write access, trigger during create
            super(arap_import_kyquy_congviec, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(arap_import_kyquy_congviec, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True

    _columns = {
        'name': fields.datetime('Date Import', required=True,states={'done': [('readonly', True)]}),
        'ngay_thu': fields.date('Ngày thu', required=True,states={'done': [('readonly', True)]}),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='GL Account', type="binary", nodrop=True,states={'done': [('readonly', True)]}),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True)
    }
    
    _defaults = {
        'state':'draft',
        'name': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'ngay_thu': lambda *a: time.strftime('%Y-%m-%d'),
        
    }
    
    def import_account(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            f_name = this.datas_fname and (this.datas_fname[:-4]+'_'+time.strftime('%Y%m%d%H%M%S')+this.datas_fname[-4:]) or ''
            file_path = '/media/temp/'+f_name
            open(file_path,'wb').write(recordlist)
            csvUti = lib_csv.csv_ultilities()
            file_data = csvUti._read_file(file_path)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        kyquy_obj = self.pool.get('thu.ky.quy')
        partner_obj = self.pool.get('res.partner')
        try:
            seq = 0
            noidung_loi = ''
            for seq,row in enumerate(file_data):
                 
                ma_doi_tuong = str(row['ma_doi_tuong']).strip()
                 
                chinhanh = str(row['ma_chi_nhanh']).strip()
                 
                try:
                    sotien_dathu = int(row['ky_quy_da_thu'])
                except Exception, e:
                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền đã thu không đúng định dạng'%(seq+2,ma_doi_tuong,chinhanh)
                    raise osv.except_osv(_('Cảnh báo!'), 'Số tiền đã thu không đúng định dạng')
                 
#                 if sotien_phaithu<sotien_dathu:
#                     noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền phải thu không được bé hơn số tiền đã thu'%(seq+2,ma_doi_tuong,chinhanh)
#                     raise osv.except_osv(_('Cảnh báo!'), 'Số tiền phải thu không được bé hơn số tiền đã thu')
                 
                sql = '''
                    select id from account_account where upper(code)='%s' limit 1
                '''%(chinhanh.upper())
                cr.execute(sql)
                chinhanh_ids = cr.fetchone()
                if not chinhanh_ids:
                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy chi nhánh'%(seq+2,ma_doi_tuong,chinhanh)
                    raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy chi nhánh')
                 
                sql = '''
                    select id,COALESCE(sotien_phaithu,0) as sotien_phaithu,COALESCE(sotien_dathu,0) as sotien_dathu,chinhanh_id,nhanvienvanphong,taixe,nhadautu from res_partner where upper(ma_doi_tuong)='%s'
                '''%(ma_doi_tuong.upper())
                cr.execute(sql)
                partner = cr.dictfetchone()
                if not partner:
                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy đối tượng'%(seq+2,ma_doi_tuong,chinhanh)
                    raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy đối tượng')
                loai_doituong = ''
                if partner['nhadautu']:
                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Ký quỹ công việc không dành cho đối tượng nhà đầu tư'%(seq+2,ma_doi_tuong,chinhanh)
                    raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy chi nhánh')
                if partner['taixe']==True:
                    loai_doituong = 'taixe'
                if partner['nhanvienvanphong']==True:
                    loai_doituong = 'nhanvienvanphong'
                if chinhanh_ids[0]!=partner['chinhanh_id']:
                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,ma_doi_tuong,chinhanh)
                    raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của đối tượng')
                if partner['sotien_phaithu']<00:
                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền phải thu phải lớn hơn 0'%(seq+2,ma_doi_tuong,chinhanh)
                    raise osv.except_osv(_('Cảnh báo!'), 'Đã có số tiền phải thu')
#                 if partner['sotien_dathu']>0:
#                     noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Đã có số tiền đã thu'%(seq+2,ma_doi_tuong,chinhanh)
#                     raise osv.except_osv(_('Cảnh báo!'), 'Đã có số tiền đã thu')
                 
#                 partner_obj.write(cr, uid, [partner['id']], {'sotien_phaithu':sotien_phaithu})
                sql = '''
                    select id from loai_ky_quy where upper(code)='KY_QUY_CONG_VIEC' limit 1
                '''
                cr.execute(sql)
                loai_kq_ids = [r[0] for r in cr.fetchall()]
                if not loai_kq_ids:
                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy loại ký quỹ "Ký quỹ công việc"'%(seq+2,ma_doi_tuong,chinhanh)
                    raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy loại ký quỹ "Ký quỹ công việc"')
                kyquy_vals = {
                    'chinhanh_id': partner['chinhanh_id'],
                    'loai_doituong': loai_doituong,
                    'partner_id': partner['id'],
                    'so_tien': sotien_dathu,
                    'ngay_thu': this.ngay_thu,
                    'loai_kyquy_id': loai_kq_ids[0],
                }
                kyquy_id = kyquy_obj.create(cr, uid, kyquy_vals)
                kyquy_obj.bt_thu(cr, uid, [kyquy_id])
                 
        except Exception, e:
            cr.rollback()
            if not noidung_loi:
                noidung_loi = str(e).replace("'","''")
                if seq:
                    noidung_loi = 'Dòng "%s": '%(seq+2) + noidung_loi
            raise osv.except_osv(_('Warning!'), noidung_loi)
        return self.write(cr, uid, ids, {'state':'done'})
    
arap_import_kyquy_congviec()

class arap_import_kyquy_dhbd(osv.osv):
    _name = 'arap.import.kyquy.dhbd'
    
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
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'hr_identities_attachment.location')
        file_size = len(value.decode('base64'))
        if location:
            attach = self.browse(cr, uid, id, context=context)
            if attach.store_fname:
                self._file_delete(cr, uid, location, attach.store_fname)
            fname = self._file_write(cr, uid, location, value)
            # SUPERUSER_ID as probably don't have write access, trigger during create
            super(arap_import_kyquy_dhbd, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(arap_import_kyquy_dhbd, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True

    _columns = {
        'name': fields.datetime('Date Import', required=True,states={'done': [('readonly', True)]}),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='GL Account', type="binary", nodrop=True,states={'done': [('readonly', True)]}),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True)
    }
    
    _defaults = {
        'state':'draft',
        'name': time.strftime('%Y-%m-%d %H:%M:%S'),
        
    }
    
    def import_account(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            f_name = this.datas_fname and (this.datas_fname[:-4]+'_'+time.strftime('%Y%m%d%H%M%S')+this.datas_fname[-4:]) or ''
            file_path = '/media/temp/'+f_name
            open(file_path,'wb').write(recordlist)
            csvUti = lib_csv.csv_ultilities()
            file_data = csvUti._read_file(file_path)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        kyquy_obj = self.pool.get('thu.ky.quy')
        partner_obj = self.pool.get('res.partner')
        chi_nhanh_line_obj = self.pool.get('chi.nhanh.line')
        try:
            seq = 0
            noidung_loi = ''
            for seq,row in enumerate(file_data):
                
                ma_doi_tuong = str(row['ma_doi_tuong']).strip()
                
                chinhanh = str(row['ma_chi_nhanh']).strip()
                
                try:
                    sotien_phaithu = int(row['ky_quy_phai_thu'])
                except Exception, e:
                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền phải thu không đúng định dạng'%(seq+2,ma_doi_tuong,chinhanh)
                    raise osv.except_osv(_('Cảnh báo!'), 'Số tiền phải thu không đúng định dạng')
                
                try:
                    sotien_dathu = int(row['ky_quy_da_thu'])
                except Exception, e:
                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền đã thu không đúng định dạng'%(seq+2,ma_doi_tuong,chinhanh)
                    raise osv.except_osv(_('Cảnh báo!'), 'Số tiền đã thu không đúng định dạng')
                
                if sotien_phaithu<sotien_dathu:
                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Số tiền phải thu không được bé hơn số tiền đã thu'%(seq+2,ma_doi_tuong,chinhanh)
                    raise osv.except_osv(_('Cảnh báo!'), 'Số tiền phải thu không được bé hơn số tiền đã thu')
                
                sql = '''
                    select id from account_account where upper(code)='%s' limit 1
                '''%(chinhanh.upper())
                cr.execute(sql)
                chinhanh_ids = cr.fetchone()
                if not chinhanh_ids:
                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy chi nhánh'%(seq+2,ma_doi_tuong,chinhanh)
                    raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy chi nhánh')
                
                bsx = str(row['bien_so_xe']).strip()
                sql = ''' select id from bien_so_xe where upper(name)='%s' '''%(bsx.upper())
                cr.execute(sql)
                bien_so_xe_ids = cr.fetchone()
                if not bien_so_xe_ids:
                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy biển số xe'%(seq+2,ma_doi_tuong,chinhanh)
                    raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy biển số xe')
                
                sql = '''
                    select id,COALESCE(sotien_phaithu,0) as sotien_phaithu,COALESCE(sotien_dathu,0) as sotien_dathu,chinhanh_id,nhanvienvanphong,taixe,nhadautu from res_partner where upper(ma_doi_tuong)='%s'
                '''%(ma_doi_tuong.upper())
                cr.execute(sql)
                partner = cr.dictfetchone()
                if not partner:
                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy đối tượng'%(seq+2,ma_doi_tuong,chinhanh)
                    raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy đối tượng')
                loai_doituong = ''
                if partner['taixe'] or partner['nhanvienvanphong']:
                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Ký quỹ ĐH-BĐ không dành cho đối tượng lái xe hoặc nhân viên văn phòng'%(seq+2,ma_doi_tuong,chinhanh)
                    raise osv.except_osv(_('Cảnh báo!'), 'Ký quỹ ĐH-BĐ không dành cho đối tượng lái xe hoặc nhân viên văn phòng')
                if partner['nhadautu']==True:
                    loai_doituong = 'nhadautu'
                    sql = '''
                        select id,COALESCE(sotien_phaithu,0) as sotien_phaithu,COALESCE(sotien_dathu,0) as sotien_dathu from chi_nhanh_line where chinhanh_id=%s and partner_id=%s
                    '''%(chinhanh_ids[0],partner['id'])
                    cr.execute(sql)
                    chinhanhline = cr.dictfetchone()
                    if not chinhanhline:
                        noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Chi nhánh không trùng với chi nhánh của đối tượng'%(seq+2,ma_doi_tuong,chinhanh)
                        raise osv.except_osv(_('Cảnh báo!'), 'Chi nhánh không trùng với chi nhánh của đối tượng')
                    sql = '''
                        select id from thu_ky_quy where partner_id=%s and bien_so_xe_id=%s and state='paid'
                    '''%(partner['id'],bien_so_xe_ids[0])
                    cr.execute(sql)
                    kyquy_ids = [r[0] for r in cr.fetchall()]
                    if kyquy_ids:
                        noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Đã thu ký quỹ cho biển số xe "%s"'%(seq+2,ma_doi_tuong,chinhanh,bsx)
                        raise osv.except_osv(_('Cảnh báo!'), 'Đã thu ký quỹ cho biển số xe')
#                     if chinhanhline['sotien_phaithu']>0:
#                         noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Đã có số tiền phải thu'%(seq+2,ma_doi_tuong,chinhanh)
#                         raise osv.except_osv(_('Cảnh báo!'), 'Đã có số tiền phải thu')
#                     if chinhanhline['sotien_dathu']>0:
#                         noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Đã có số tiền đã thu'%(seq+2,ma_doi_tuong,chinhanh)
#                         raise osv.except_osv(_('Cảnh báo!'), 'Đã có số tiền đã thu')
                    chi_nhanh_line_obj.write(cr, uid, [chinhanhline['id']], {'sotien_phaithu':chinhanhline['sotien_phaithu']+sotien_phaithu})
                
                sql = '''
                    select id from loai_ky_quy where upper(code)='KY_QUY_DH_BD' limit 1
                '''
                cr.execute(sql)
                loai_kq_ids = [r[0] for r in cr.fetchall()]
                if not loai_kq_ids:
                    noidung_loi = 'Dòng "%s"; mã đối tượng "%s"; chi nhánh "%s": Không tìm thấy loại ký quỹ "Ký quỹ ĐH-BĐ"'%(seq+2,ma_doi_tuong,chinhanh)
                    raise osv.except_osv(_('Cảnh báo!'), 'Không tìm thấy loại ký quỹ "Ký quỹ ĐH-BĐ"')
                kyquy_vals = {
                    'chinhanh_id': chinhanh_ids[0],
                    'loai_doituong': loai_doituong,
                    'partner_id': partner['id'],
                    'so_tien': sotien_dathu,
                    'ngay_thu': '2015-12-31',
                    'loai_kyquy_id': loai_kq_ids[0],
                    'bien_so_xe_id': bien_so_xe_ids and bien_so_xe_ids[0] or False,
                }
                kyquy_id = kyquy_obj.create(cr, uid, kyquy_vals)
                kyquy_obj.bt_thu(cr, uid, [kyquy_id])
                
        except Exception, e:
            cr.rollback()
            if not noidung_loi:
                noidung_loi = str(e).replace("'","''")
                if seq:
                    noidung_loi = 'Dòng "%s": '%(seq+2) + noidung_loi
            raise osv.except_osv(_('Warning!'), noidung_loi)
        return self.write(cr, uid, ids, {'state':'done'})
    
arap_import_kyquy_dhbd()

