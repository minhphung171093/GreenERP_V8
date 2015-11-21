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
from dateutil.relativedelta import relativedelta
# from datetime import datetime, timedelta
from openerp.tools import config
_logger = logging.getLogger(__name__)


class output_congno_tudong(osv.osv):
    _name = 'output.congno.tudong'

    _columns = {
        'name': fields.date('Tên', required=True),
    }
    
    def init(self, cr):
        self.fin_output_theodoanhsothu_oracle_data(cr)
        self.fin_output_theodoanhsotra_oracle_data(cr)
        self.fin_output_theodoanhsothu_oracle(cr)
        self.fin_output_theodoanhsotra_oracle(cr)
        cr.commit()
        return True
    
    def fin_output_theodoanhsothu_oracle_data(self, cr):
        cr.execute("select exists (select 1 from pg_type where typname = 'fin_output_theodoanhsothu_oracle_data')")
        res = cr.fetchone()
        if res and res[0]:
            cr.execute('''delete from pg_type where typname = 'fin_output_theodoanhsothu_oracle_data';
                            delete from pg_class where relname='fin_output_theodoanhsothu_oracle_data';
                            commit;''')
        sql = '''
        CREATE TYPE fin_output_theodoanhsothu_oracle_data AS
           (chinhanh character varying(1024),
            machinhanh character varying(250),
            loaicongno character varying(250),
            taikhoan character varying(250),
            sotien numeric,
            ghichu character varying(250)
            );
        ALTER TYPE fin_output_theodoanhsothu_oracle_data
          OWNER TO '''+config['db_user']+''';
        '''
        cr.execute(sql)
        return True
    
    def fin_output_theodoanhsothu_oracle(self, cr):
        sql = '''
        DROP FUNCTION IF EXISTS fin_output_theodoanhsothu_oracle(date, date) CASCADE;
        commit;
        
        CREATE OR REPLACE FUNCTION fin_output_theodoanhsothu_oracle(date, date)
          RETURNS SETOF fin_output_theodoanhsothu_oracle_data AS
        $BODY$
        DECLARE
            rec_cn        record;
            rec_aml       record;
            bal_data      fin_output_theodoanhsothu_oracle_data%ROWTYPE;
            loaicongno    numeric;
            sotien        numeric;
        BEGIN
            for rec_cn in execute '
                    select id,code,name from account_account where parent_id in (select id from account_account where code=''1'')
                        and id in (select parent_id from account_account where id in (select account_id from account_move_line where date between $1 and $2))
                ' using $1, $2
            loop
                for loaicongno in 1..9
                loop
                    if loaicongno=1 then
                        sotien = 0;
                        for rec_aml in execute '
                            select sum(credit) as sotien
                                from account_move_line
                                where move_id in (select move_id from account_voucher
                                    where reference in (select name from account_invoice
                                        where mlg_type=''no_doanh_thu'' and state in (''open'',''paid'')))
                                and date between $1 and $2
                        ' using $1, $2
                        loop
                            sotien = sotien + coalesce(rec_aml.sotien, 0);
                        end loop;
                        if sotien <> 0 then
                            bal_data.chinhanh=rec_cn.name;
                            bal_data.machinhanh=rec_cn.code;
                            bal_data.loaicongno='AR_Nợ doanh thu';
                            bal_data.taikhoan='1411011';
                            bal_data.sotien=sotien;
                            bal_data.ghichu='';
                            return next bal_data;
                        end if;
                    end if;
                    
                    if loaicongno=2 then
                        sotien = 0;
                        for rec_aml in execute '
                            select sum(credit) as sotien
                                from account_move_line
                                where move_id in (select move_id from account_voucher
                                    where reference in (select name from account_invoice
                                        where mlg_type=''hoan_tam_ung'' and loai_tamung_id in (select id from loai_tam_ung
                                            where name=''Tạm ứng công tác'')
                                            and state in (''open'',''paid'') and loai_doituong=''nhanvienvanphong''))
                                and date between $1 and $2
                        ' using $1, $2
                        loop
                            sotien = sotien + coalesce(rec_aml.sotien, 0);
                        end loop;
                        if sotien <> 0 then
                            bal_data.chinhanh=rec_cn.name;
                            bal_data.machinhanh=rec_cn.code;
                            bal_data.loaicongno='AR_Tạm ứng_Công tác_Nhân viên';
                            bal_data.taikhoan='1411012';
                            bal_data.sotien=sotien;
                            bal_data.ghichu='';
                            return next bal_data;
                        end if;
                    end if;
                    
                    if loaicongno=3 then
                        sotien = 0;
                        for rec_aml in execute '
                            select sum(credit) as sotien
                                from account_move_line
                                where move_id in (select move_id from account_voucher
                                    where reference in (select name from account_invoice
                                        where mlg_type=''hoan_tam_ung'' and loai_tamung_id in (select id from loai_tam_ung
                                            where name=''Tạm ứng công tác'')
                                            and state in (''open'',''paid'') and loai_doituong=''taixe''))
                                and date between $1 and $2
                        ' using $1, $2
                        loop
                            sotien = sotien + coalesce(rec_aml.sotien, 0);
                        end loop;
                        if sotien <> 0 then
                            bal_data.chinhanh=rec_cn.name;
                            bal_data.machinhanh=rec_cn.code;
                            bal_data.loaicongno='AR_Tạm ứng_Công tác_Lái xe';
                            bal_data.taikhoan='1411011';
                            bal_data.sotien=sotien;
                            bal_data.ghichu='';
                            return next bal_data;
                        end if;
                    end if;
                    
                    if loaicongno=4 then
                        sotien = 0;
                        for rec_aml in execute '
                            select sum(credit) as sotien
                                from account_move_line
                                where move_id in (select move_id from account_voucher
                                    where reference in (select name from account_invoice
                                        where mlg_type=''hoan_tam_ung'' and loai_tamung_id in (select id from loai_tam_ung
                                            where name=''Tạm ứng khó khăn'')
                                            and state in (''open'',''paid'') and loai_doituong=''nhanvienvanphong''))
                                and date between $1 and $2
                        ' using $1, $2
                        loop
                            sotien = sotien + coalesce(rec_aml.sotien, 0);
                        end loop;
                        if sotien <> 0 then
                            bal_data.chinhanh=rec_cn.name;
                            bal_data.machinhanh=rec_cn.code;
                            bal_data.loaicongno='AR_Tạm ứng_Hoàn cảnh_Nhân viên';
                            bal_data.taikhoan='1411012';
                            bal_data.sotien=sotien;
                            bal_data.ghichu='';
                            return next bal_data;
                        end if;
                    end if;
                    
                    if loaicongno=5 then
                        sotien = 0;
                        for rec_aml in execute '
                            select sum(credit) as sotien
                                from account_move_line
                                where move_id in (select move_id from account_voucher
                                    where reference in (select name from account_invoice
                                        where mlg_type=''hoan_tam_ung'' and loai_tamung_id in (select id from loai_tam_ung
                                            where name=''Tạm ứng khó khăn'')
                                            and state in (''open'',''paid'') and loai_doituong=''taixe''))
                                and date between $1 and $2
                        ' using $1, $2
                        loop
                            sotien = sotien + coalesce(rec_aml.sotien, 0);
                        end loop;
                        if sotien <> 0 then
                            bal_data.chinhanh=rec_cn.name;
                            bal_data.machinhanh=rec_cn.code;
                            bal_data.loaicongno='AR_Tạm ứng_Hoàn cảnh_Lái xe';
                            bal_data.taikhoan='1411011';
                            bal_data.sotien=sotien;
                            bal_data.ghichu='';
                            return next bal_data;
                        end if;
                    end if;
                    
                    if loaicongno=6 then
                        sotien = 0;
                        for rec_aml in execute '
                            select sum(credit) as sotien
                                from account_move_line
                                where move_id in (select move_id from account_voucher
                                    where reference in (select name from account_invoice
                                        where mlg_type=''phat_vi_pham'' and state in (''open'',''paid'') ))
                                and date between $1 and $2
                        ' using $1, $2
                        loop
                            sotien = sotien + coalesce(rec_aml.sotien, 0);
                        end loop;
                        if sotien <> 0 then
                            bal_data.chinhanh=rec_cn.name;
                            bal_data.machinhanh=rec_cn.code;
                            bal_data.loaicongno='AR_Phạt vi phạm';
                            bal_data.taikhoan='7111018';
                            bal_data.sotien=sotien;
                            bal_data.ghichu='';
                            return next bal_data;
                        end if;
                    end if;
                    
                    if loaicongno=7 then
                        sotien = 0;
                        for rec_aml in execute '
                            select sum(credit) as sotien
                                from account_move_line
                                where move_id in (select move_id from account_voucher
                                    where reference in (select name from account_invoice
                                        where mlg_type=''tra_gop_xe'' and state in (''open'',''paid'') ))
                                and date between $1 and $2
                        ' using $1, $2
                        loop
                            sotien = sotien + coalesce(rec_aml.sotien, 0);
                        end loop;
                        if sotien <> 0 then
                            bal_data.chinhanh=rec_cn.name;
                            bal_data.machinhanh=rec_cn.code;
                            bal_data.loaicongno='AR_Trả góp mua xe';
                            bal_data.taikhoan='3387018';
                            bal_data.sotien=sotien;
                            bal_data.ghichu='';
                            return next bal_data;
                        end if;
                    end if;
                    
                    if loaicongno=8 then
                        sotien = 0;
                        for rec_aml in execute '
                            select sum(credit) as sotien
                                from account_move_line
                                where move_id in (select move_id from account_voucher
                                    where reference in (select name from account_invoice
                                        where mlg_type=''thu_phi_thuong_hieu'' and state in (''open'',''paid'') ))
                                and date between $1 and $2
                        ' using $1, $2
                        loop
                            sotien = sotien + coalesce(rec_aml.sotien, 0);
                        end loop;
                        if sotien <> 0 then
                            bal_data.chinhanh=rec_cn.name;
                            bal_data.machinhanh=rec_cn.code;
                            bal_data.loaicongno='AR_Phí thương hiệu';
                            bal_data.taikhoan='3387012';
                            bal_data.sotien=sotien;
                            bal_data.ghichu='';
                            return next bal_data;
                        end if;
                    end if;
                    
                    if loaicongno=9 then
                        sotien = 0;
                        for rec_aml in execute '
                            select sum(credit) as sotien
                                from account_move_line
                                where move_id in (select move_id from account_voucher
                                    where reference in (select name from account_invoice
                                        where mlg_type=''thu_no_xuong'' and state in (''open'',''paid'') ))
                                and date between $1 and $2
                        ' using $1, $2
                        loop
                            sotien = sotien + coalesce(rec_aml.sotien, 0);
                        end loop;
                        if sotien <> 0 then
                            bal_data.chinhanh=rec_cn.name;
                            bal_data.machinhanh=rec_cn.code;
                            bal_data.loaicongno='AR_Nợ xưởng sửa chữa';
                            bal_data.taikhoan='5113021';
                            bal_data.sotien=sotien;
                            bal_data.ghichu='';
                            return next bal_data;
                        end if;
                    end if;
                    
                end loop;
            end loop;

            return;
        END; $BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100
          ROWS 1000000;
        ALTER FUNCTION fin_output_theodoanhsothu_oracle(date, date)
          OWNER TO '''+config['db_user']+''';
        '''
        cr.execute(sql)
        return True
    
    def fin_output_theodoanhsotra_oracle_data(self, cr):
        cr.execute("select exists (select 1 from pg_type where typname = 'fin_output_theodoanhsotra_oracle_data')")
        res = cr.fetchone()
        if res and res[0]:
            cr.execute('''delete from pg_type where typname = 'fin_output_theodoanhsotra_oracle_data';
                            delete from pg_class where relname='fin_output_theodoanhsotra_oracle_data';
                            commit;''')
        sql = '''
        CREATE TYPE fin_output_theodoanhsotra_oracle_data AS
           (chinhanh character varying(1024),
            machinhanh character varying(250),
            loaicongno character varying(250),
            taikhoan character varying(250),
            sotien numeric,
            ghichu character varying(250)
            );
        ALTER TYPE fin_output_theodoanhsotra_oracle_data
          OWNER TO '''+config['db_user']+''';
        '''
        cr.execute(sql)
        return True
    
    def fin_output_theodoanhsotra_oracle(self, cr):
        sql = '''
        DROP FUNCTION IF EXISTS fin_output_theodoanhsotra_oracle(date, date) CASCADE;
        commit;
        
        CREATE OR REPLACE FUNCTION fin_output_theodoanhsotra_oracle(date, date)
          RETURNS SETOF fin_output_theodoanhsotra_oracle_data AS
        $BODY$
        DECLARE
            rec_cn        record;
            rec_aml       record;
            bal_data      fin_output_theodoanhsotra_oracle_data%ROWTYPE;
            loaicongno    numeric;
            sotien        numeric;
        BEGIN
            for rec_cn in execute '
                    select id,code,name from account_account where parent_id in (select id from account_account where code=''1'')
                        and id in (select parent_id from account_account where id in (select account_id from account_move_line where date between $1 and $2))
                ' using $1, $2
            loop
                for loaicongno in 1..2
                loop
                    if loaicongno=1 then
                        sotien = 0;
                        for rec_aml in execute '
                            select sum(credit) as sotien
                                from account_move_line
                                where move_id in (select move_id from account_voucher
                                    where reference in (select name from account_invoice
                                        where mlg_type=''phai_tra_ky_quy'' and state in (''open'',''paid'')))
                                and date between $1 and $2
                        ' using $1, $2
                        loop
                            sotien = sotien + coalesce(rec_aml.sotien, 0);
                        end loop;
                        if sotien <> 0 then
                            bal_data.chinhanh=rec_cn.name;
                            bal_data.machinhanh=rec_cn.code;
                            bal_data.loaicongno='AR_Phải trả ký quỹ';
                            bal_data.taikhoan='1411011';
                            bal_data.sotien=sotien;
                            bal_data.ghichu='';
                            return next bal_data;
                        end if;
                    end if;
                    
                    if loaicongno=2 then
                        sotien = 0;
                        for rec_aml in execute '
                            select sum(credit) as sotien
                                from account_move_line
                                where move_id in (select move_id from account_voucher
                                    where reference in (select name from account_invoice
                                        where mlg_type=''chi_ho'' and state in (''open'',''paid'')))
                                and date between $1 and $2
                        ' using $1, $2
                        loop
                            sotien = sotien + coalesce(rec_aml.sotien, 0);
                        end loop;
                        if sotien <> 0 then
                            bal_data.chinhanh=rec_cn.name;
                            bal_data.machinhanh=rec_cn.code;
                            bal_data.loaicongno='AR_Phải trả chi hộ';
                            bal_data.taikhoan='1411011';
                            bal_data.sotien=sotien;
                            bal_data.ghichu='';
                            return next bal_data;
                        end if;
                    end if;
                    
                end loop;
            end loop;

            return;
        END; $BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100
          ROWS 1000000;
        ALTER FUNCTION fin_output_theodoanhsotra_oracle(date, date)
          OWNER TO '''+config['db_user']+''';
        '''
        cr.execute(sql)
        return True
    
    def output_phaithu_thunoxuong_bdsc(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','thu_no_xuong')])
            if output_ids:
                invoice_obj = self.pool.get('account.invoice')
                date_start = time.strftime('%Y-%m-01')
                date_end = str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10]
                csvUti = lib_csv.csv_ultilities()
                headers = ['chi_nhanh','ma_chi_nhanh','loai_doi_tuong','ma_doi_tuong','ten_doi_tuong','ngay_giao_dich','bien_so_xe','so_hop_dong','ma_chiet_tinh','ma_xuong','so_tien','dien_giai','ngay_thanh_toan','so_tien_da_thu']
                contents = []
                sql = '''
                    select ai.id as invoice_id,cn.name as chi_nhanh, cn.code as ma_chi_nhanh,ai.loai_doituong,dt.ma_doi_tuong as ma_doi_tuong, dt.name as ten_doi_tuong,
                        ai.date_invoice as ngay_giao_dich,bsx.name as bien_so_xe, ai.so_hop_dong as so_hop_dong, ai.ma_bang_chiettinh_chiphi_sua as ma_chiet_tinh,
                        mx.code as ma_xuong, ai.so_tien as so_tien, ai.dien_giai as dien_giai, ai.residual as residual, ai.state as state
                        
                        from account_invoice ai 
                        left join account_account cn on cn.id=ai.chinhanh_id
                        left join res_partner dt on dt.id=ai.partner_id
                        left join bien_so_xe bsx on bsx.id=ai.bien_so_xe_id
                        left join ma_xuong mx on mx.id=ai.ma_xuong_id
                        
                        where ai.mlg_type='thu_no_xuong' and state in ('open','paid')
                '''
                cr. execute(sql)
                for line in cr.dictfetchall():
                    loai_doituong=''
                    if line['loai_doituong']=='taixe':
                        loai_doituong = 'Lái xe'
                    if line['loai_doituong']=='nhadautu':
                        loai_doituong = 'Nhà đầu tư'
                    if line['loai_doituong']=='nhanvienvanphong':
                        loai_doituong = 'Nhân viên văn phòng'
                        
                    ngay_giao_dich_arr = line['ngay_giao_dich'].split('-')
                    ngay_giao_dich = ngay_giao_dich_arr[2]+'/'+ngay_giao_dich_arr[1]+'/'+ngay_giao_dich_arr[0]
                        
                    invoice = invoice_obj.browse(cr, uid, line['invoice_id'])
                    if invoice.payment_ids:
                        for payment in invoice.payment_ids:
                            if payment.date>=date_start and payment.date<=date_end:
                                ngay_thanh_toan_arr = payment.date.split('-')
                                ngay_thanh_toan = ngay_thanh_toan_arr[2]+'/'+ngay_thanh_toan_arr[1]+'/'+ngay_thanh_toan_arr[0]
                                contents.append({
                                    'chi_nhanh': line['chi_nhanh'],
                                    'ma_chi_nhanh': line['ma_chi_nhanh'],
                                    'loai_doi_tuong': loai_doituong,
                                    'ma_doi_tuong': line['ma_doi_tuong'],
                                    'ten_doi_tuong': line['ten_doi_tuong'],
                                    'ngay_giao_dich': ngay_giao_dich,
                                    'bien_so_xe': line['bien_so_xe'],
                                    'so_hop_dong': line['so_hop_dong'],
                                    'ma_chiet_tinh': line['ma_chiet_tinh'],
                                    'ma_xuong': line['ma_xuong'],
                                    'so_tien': line['so_tien'],
                                    'dien_giai': line['dien_giai'],
                                    'ngay_thanh_toan': ngay_thanh_toan,
                                    'so_tien_da_thu': payment.credit,
                                })
                if contents:
                    for path in output_obj.browse(cr, uid, output_ids):
                        path_file_name = path.name+'/'+'thu_no_xuong_bdsc_'+time.strftime('%Y_%m_%d_%H_%M_%S')+'.csv'
                        csvUti._write_file(contents,headers,path_file_name )
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': path_file_name,
                            'loai_giaodich': 'Thu nợ xưởng (BDSC)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Xuất',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
        except Exception, e:
            lichsu_obj.create(cr, uid, {
                'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                'ten_file': '',
                'loai_giaodich': 'Thu nợ xưởng (BDSC)',
                'thu_tra': 'Thu',
                'nhap_xuat': 'Xuất',
                'tudong_bangtay': 'Tự động',
                'trang_thai': 'Lỗi',
                'noidung_loi': e,
            })
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def output_phaithu_thuphithuonghieu_htkd(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','thu_phi_thuong_hieu_htkd')])
            if output_ids:
                invoice_obj = self.pool.get('account.invoice')
                date_start = time.strftime('%Y-%m-01')
                date_end = str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10]
                csvUti = lib_csv.csv_ultilities()
                headers = ['chi_nhanh','ma_chi_nhanh','loai_doi_tuong','ma_doi_tuong','ten_doi_tuong','ngay_giao_dich','bien_so_xe','so_hop_dong','so_tien','dien_giai','ngay_thanh_toan','so_tien_da_thu']
                contents = []
                sql = '''
                    select ai.id as invoice_id,cn.name as chi_nhanh, cn.code as ma_chi_nhanh,ai.loai_doituong,dt.ma_doi_tuong as ma_doi_tuong, dt.name as ten_doi_tuong,
                        ai.date_invoice as ngay_giao_dich,bsx.name as bien_so_xe, ai.so_hop_dong as so_hop_dong, ai.ma_bang_chiettinh_chiphi_sua as ma_chiet_tinh,
                        mx.code as ma_xuong, ai.so_tien as so_tien, ai.dien_giai as dien_giai, ai.residual as residual, ai.state as state
                        
                        from account_invoice ai 
                        left join account_account cn on cn.id=ai.chinhanh_id
                        left join res_partner dt on dt.id=ai.partner_id
                        left join bien_so_xe bsx on bsx.id=ai.bien_so_xe_id
                        left join ma_xuong mx on mx.id=ai.ma_xuong_id
                        
                        where ai.mlg_type='thu_phi_thuong_hieu' and state in ('open','paid')
                '''
                cr. execute(sql)
                for line in cr.dictfetchall():
                    loai_doituong=''
                    if line['loai_doituong']=='taixe':
                        loai_doituong = 'Lái xe'
                    if line['loai_doituong']=='nhadautu':
                        loai_doituong = 'Nhà đầu tư'
                    if line['loai_doituong']=='nhanvienvanphong':
                        loai_doituong = 'Nhân viên văn phòng'
                        
                    ngay_giao_dich_arr = line['ngay_giao_dich'].split('-')
                    ngay_giao_dich = ngay_giao_dich_arr[2]+'/'+ngay_giao_dich_arr[1]+'/'+ngay_giao_dich_arr[0]
                        
                    invoice = invoice_obj.browse(cr, uid, line['invoice_id'])
                    if invoice.payment_ids:
                        for payment in invoice.payment_ids:
                            if payment.date>=date_start and payment.date<=date_end:
                                ngay_thanh_toan_arr = payment.date.split('-')
                                ngay_thanh_toan = ngay_thanh_toan_arr[2]+'/'+ngay_thanh_toan_arr[1]+'/'+ngay_thanh_toan_arr[0]
                                contents.append({
                                    'chi_nhanh': line['chi_nhanh'],
                                    'ma_chi_nhanh': line['ma_chi_nhanh'],
                                    'loai_doi_tuong': loai_doituong,
                                    'ma_doi_tuong': line['ma_doi_tuong'],
                                    'ten_doi_tuong': line['ten_doi_tuong'],
                                    'ngay_giao_dich': ngay_giao_dich,
                                    'bien_so_xe': line['bien_so_xe'],
                                    'so_hop_dong': line['so_hop_dong'],
                                    'so_tien': line['so_tien'],
                                    'dien_giai': line['dien_giai'],
                                    'ngay_thanh_toan': ngay_thanh_toan,
                                    'so_tien_da_thu': payment.credit,
                                })
                if contents:
                    for path in output_obj.browse(cr, uid, output_ids):
                        path_file_name = path.name+'/'+'thu_phi_thuong_hieu_htkd_'+time.strftime('%Y_%m_%d_%H_%M_%S')+'.csv'
                        csvUti._write_file(contents,headers,path_file_name )
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': path_file_name,
                            'loai_giaodich': 'Thu phí thương hiệu (HTKD)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Xuất',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
        except Exception, e:
            lichsu_obj.create(cr, uid, {
                'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                'ten_file': '',
                'loai_giaodich': 'Thu phí thương hiệu (HTKD)',
                'thu_tra': 'Thu',
                'nhap_xuat': 'Xuất',
                'tudong_bangtay': 'Tự động',
                'trang_thai': 'Lỗi',
                'noidung_loi': e,
            })
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def output_phaithu_tragopxe_htkd(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','tra_gop_xe_htkd')])
            if output_ids:
                invoice_obj = self.pool.get('account.invoice')
                date_start = time.strftime('%Y-%m-01')
                date_end = str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10]
                csvUti = lib_csv.csv_ultilities()
                headers = ['chi_nhanh','ma_chi_nhanh','loai_doi_tuong','ma_doi_tuong','ten_doi_tuong','ngay_phat_sinh','bien_so_xe','so_hop_dong','so_tien','don_vi_chi','dien_giai','ngay_thanh_toan','so_tien_da_thu']
                contents = []
                sql = '''
                    select ai.id as invoice_id,cn.name as chi_nhanh, cn.code as ma_chi_nhanh,ai.loai_doituong,dt.ma_doi_tuong as ma_doi_tuong, dt.name as ten_doi_tuong,
                        ai.date_invoice as ngay_giao_dich,bsx.name as bien_so_xe, ai.so_hop_dong as so_hop_dong, ai.ma_bang_chiettinh_chiphi_sua as ma_chiet_tinh,
                        mx.code as ma_xuong, ai.so_tien as so_tien, ai.dien_giai as dien_giai, ai.residual as residual, ai.state as state,dvc.ma_doi_tuong as don_vi_chi
                        
                        from account_invoice ai 
                        left join account_account cn on cn.id=ai.chinhanh_id
                        left join res_partner dt on dt.id=ai.partner_id
                        left join bien_so_xe bsx on bsx.id=ai.bien_so_xe_id
                        left join ma_xuong mx on mx.id=ai.ma_xuong_id
                        left join res_partner dvc on dvc.id=ai.thu_cho_doituong_id
                        
                        where ai.mlg_type='tra_gop_xe' and state in ('open','paid')
                '''
                cr. execute(sql)
                for line in cr.dictfetchall():
                    loai_doituong=''
                    if line['loai_doituong']=='taixe':
                        loai_doituong = 'Lái xe'
                    if line['loai_doituong']=='nhadautu':
                        loai_doituong = 'Nhà đầu tư'
                    if line['loai_doituong']=='nhanvienvanphong':
                        loai_doituong = 'Nhân viên văn phòng'
                        
                    ngay_giao_dich_arr = line['ngay_giao_dich'].split('-')
                    ngay_giao_dich = ngay_giao_dich_arr[2]+'/'+ngay_giao_dich_arr[1]+'/'+ngay_giao_dich_arr[0]
                        
                    invoice = invoice_obj.browse(cr, uid, line['invoice_id'])
                    if invoice.payment_ids:
                        for payment in invoice.payment_ids:
                            if payment.date>=date_start and payment.date<=date_end:
                                ngay_thanh_toan_arr = payment.date.split('-')
                                ngay_thanh_toan = ngay_thanh_toan_arr[2]+'/'+ngay_thanh_toan_arr[1]+'/'+ngay_thanh_toan_arr[0]
                                contents.append({
                                    'chi_nhanh': line['chi_nhanh'],
                                    'ma_chi_nhanh': line['ma_chi_nhanh'],
                                    'loai_doi_tuong': loai_doituong,
                                    'ma_doi_tuong': line['ma_doi_tuong'],
                                    'ten_doi_tuong': line['ten_doi_tuong'],
                                    'ngay_phat_sinh': ngay_giao_dich,
                                    'bien_so_xe': line['bien_so_xe'],
                                    'so_hop_dong': line['so_hop_dong'],
                                    'so_tien': line['so_tien'],
                                    'don_vi_chi': line['don_vi_chi'],
                                    'dien_giai': line['dien_giai'],
                                    'ngay_thanh_toan': ngay_thanh_toan,
                                    'so_tien_da_thu': payment.credit,
                                })
                if contents:
                    for path in output_obj.browse(cr, uid, output_ids):
                        path_file_name = path.name+'/'+'tra_gop_xe_htkd_'+time.strftime('%Y_%m_%d_%H_%M_%S')+'.csv'
                        csvUti._write_file(contents,headers,path_file_name )
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': path_file_name,
                            'loai_giaodich': 'Trả góp xe (HTKD)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Xuất',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
        except Exception, e:
            lichsu_obj.create(cr, uid, {
                'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                'ten_file': '',
                'loai_giaodich': 'Trả góp xe (HTKD)',
                'thu_tra': 'Thu',
                'nhap_xuat': 'Xuất',
                'tudong_bangtay': 'Tự động',
                'trang_thai': 'Lỗi',
                'noidung_loi': e,
            })
            raise osv.except_osv(_('Warning!'), str(e))
        return True

    def output_phaithu_thuphithuonghieu_shift(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','thu_phi_thuong_hieu_shift')])
            if output_ids:
                csvUti = lib_csv.csv_ultilities()
                headers = ['chi_nhanh','ma_chi_nhanh','loai_doi_tuong','ma_doi_tuong','ten_doi_tuong','ngay_giao_dich','bien_so_xe','so_tien','so_hop_dong','dien_giai']
                contents = []
                sql = '''
                    select cn.name as chi_nhanh, cn.code as ma_chi_nhanh,ai.loai_doituong,dt.ma_doi_tuong as ma_doi_tuong, dt.name as ten_doi_tuong,
                        bsx.name as bien_so_xe,sum(ai.residual) as so_tien, ai.so_hop_dong as so_hop_dong
                        
                        from account_invoice ai 
                        left join account_account cn on cn.id=ai.chinhanh_id
                        left join res_partner dt on dt.id=ai.partner_id
                        left join bien_so_xe bsx on bsx.id=ai.bien_so_xe_id
                        
                        where ai.mlg_type='thu_phi_thuong_hieu' and state='open'
                        
                        group by cn.name, cn.code,ai.loai_doituong,dt.ma_doi_tuong, dt.name,bsx.name, ai.so_hop_dong
                '''
                cr. execute(sql)
                for line in cr.dictfetchall():
                    loai_doituong=''
                    if line['loai_doituong']=='taixe':
                        loai_doituong = 'Lái xe'
                    if line['loai_doituong']=='nhadautu':
                        loai_doituong = 'Nhà đầu tư'
                    if line['loai_doituong']=='nhanvienvanphong':
                        loai_doituong = 'Nhân viên văn phòng'
                    contents.append({
                        'chi_nhanh': line['chi_nhanh'],
                        'ma_chi_nhanh': line['ma_chi_nhanh'],
                        'loai_doi_tuong': loai_doituong,
                        'ma_doi_tuong': line['ma_doi_tuong'],
                        'ten_doi_tuong': line['ten_doi_tuong'],
                        'ngay_giao_dich': '',
                        'bien_so_xe': line['bien_so_xe'],
                        'so_tien': line['so_tien'],
                        'so_hop_dong': line['so_hop_dong'],
                        'dien_giai': '',
                    })
                if contents:
                    for path in output_obj.browse(cr, uid, output_ids):
                        path_file_name = path.name+'/'+'thu_phi_thuong_hieu_shift_'+time.strftime('%Y_%m_%d_%H_%M_%S')+'.csv'
                        csvUti._write_file(contents,headers,path_file_name )
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': path_file_name,
                            'loai_giaodich': 'Thu phí thương hiệu (SHIFT)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Xuất',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
        except Exception, e:
            lichsu_obj.create(cr, uid, {
                'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                'ten_file': '',
                'loai_giaodich': 'Thu phí thương hiệu (SHIFT)',
                'thu_tra': 'Thu',
                'nhap_xuat': 'Xuất',
                'tudong_bangtay': 'Tự động',
                'trang_thai': 'Lỗi',
                'noidung_loi': e,
            })
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def output_phaithu_tragopxe_shift(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','tra_gop_xe_shift')])
            if output_ids:
                csvUti = lib_csv.csv_ultilities()
                headers = ['chi_nhanh','ma_chi_nhanh','loai_doi_tuong','ma_doi_tuong','ten_doi_tuong','ngay_giao_dich','bien_so_xe','so_tien','so_hop_dong','dien_giai']
                contents = []
                sql = '''
                    select cn.name as chi_nhanh, cn.code as ma_chi_nhanh,ai.loai_doituong,dt.ma_doi_tuong as ma_doi_tuong, dt.name as ten_doi_tuong,
                        bsx.name as bien_so_xe,sum(ai.residual) as so_tien, ai.so_hop_dong as so_hop_dong
                        
                        from account_invoice ai 
                        left join account_account cn on cn.id=ai.chinhanh_id
                        left join res_partner dt on dt.id=ai.partner_id
                        left join bien_so_xe bsx on bsx.id=ai.bien_so_xe_id
                        
                        where ai.mlg_type='tra_gop_xe' and state='open'
                        
                        group by cn.name, cn.code,ai.loai_doituong,dt.ma_doi_tuong, dt.name,bsx.name, ai.so_hop_dong
                '''
                cr. execute(sql)
                for line in cr.dictfetchall():
                    loai_doituong=''
                    if line['loai_doituong']=='taixe':
                        loai_doituong = 'Lái xe'
                    if line['loai_doituong']=='nhadautu':
                        loai_doituong = 'Nhà đầu tư'
                    if line['loai_doituong']=='nhanvienvanphong':
                        loai_doituong = 'Nhân viên văn phòng'
                    contents.append({
                        'chi_nhanh': line['chi_nhanh'],
                        'ma_chi_nhanh': line['ma_chi_nhanh'],
                        'loai_doi_tuong': loai_doituong,
                        'ma_doi_tuong': line['ma_doi_tuong'],
                        'ten_doi_tuong': line['ten_doi_tuong'],
                        'ngay_giao_dich': '',
                        'bien_so_xe': line['bien_so_xe'],
                        'so_tien': line['so_tien'],
                        'so_hop_dong': line['so_hop_dong'],
                        'dien_giai': '',
                    })
                if contents:
                    for path in output_obj.browse(cr, uid, output_ids):
                        path_file_name = path.name+'/'+'tra_gop_xe_shift_'+time.strftime('%Y_%m_%d_%H_%M_%S')+'.csv'
                        csvUti._write_file(contents,headers,path_file_name )
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': path_file_name,
                            'loai_giaodich': 'Trả góp xe (SHIFT)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Xuất',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
        except Exception, e:
            lichsu_obj.create(cr, uid, {
                'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                'ten_file': '',
                'loai_giaodich': 'Trả góp xe (SHIFT)',
                'thu_tra': 'Thu',
                'nhap_xuat': 'Xuất',
                'tudong_bangtay': 'Tự động',
                'trang_thai': 'Lỗi',
                'noidung_loi': e,
            })
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def output_phaithu_phatvipham_histaff(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','phat_vi_pham')])
            if output_ids:
                csvUti = lib_csv.csv_ultilities()
                headers = ['chi_nhanh','ma_chi_nhanh','loai_doi_tuong','ma_doi_tuong','ten_doi_tuong','so_tien','dien_giai']
                contents = []
                sql = '''
                    select cn.name as chi_nhanh, cn.code as ma_chi_nhanh,ai.loai_doituong,dt.ma_doi_tuong as ma_doi_tuong, dt.name as ten_doi_tuong,
                        sum(ai.residual) as so_tien
                        
                        from account_invoice ai 
                        left join account_account cn on cn.id=ai.chinhanh_id
                        left join res_partner dt on dt.id=ai.partner_id
                        
                        where ai.mlg_type='phat_vi_pham' and state='open'
                        
                        group by cn.name, cn.code,ai.loai_doituong,dt.ma_doi_tuong, dt.name
                '''
                cr. execute(sql)
                for line in cr.dictfetchall():
                    loai_doituong=''
                    if line['loai_doituong']=='taixe':
                        loai_doituong = 'Lái xe'
                    if line['loai_doituong']=='nhadautu':
                        loai_doituong = 'Nhà đầu tư'
                    if line['loai_doituong']=='nhanvienvanphong':
                        loai_doituong = 'Nhân viên văn phòng'
                    contents.append({
                        'chi_nhanh': line['chi_nhanh'],
                        'ma_chi_nhanh': line['ma_chi_nhanh'],
                        'loai_doi_tuong': loai_doituong,
                        'ma_doi_tuong': line['ma_doi_tuong'],
                        'ten_doi_tuong': line['ten_doi_tuong'],
                        'so_tien': line['so_tien'],
                        'dien_giai': '',
                    })
                if contents:
                    for path in output_obj.browse(cr, uid, output_ids):
                        path_file_name = path.name+'/'+'phat_vi_pham_histaff_'+time.strftime('%Y_%m_%d_%H_%M_%S')+'.csv'
                        csvUti._write_file(contents,headers,path_file_name )
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': path_file_name,
                            'loai_giaodich': 'Phạt vi phạm (HISTAFF)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Xuất',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
        except Exception, e:
            lichsu_obj.create(cr, uid, {
                'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                'ten_file': '',
                'loai_giaodich': 'Phạt vi phạm (HISTAFF)',
                'thu_tra': 'Thu',
                'nhap_xuat': 'Xuất',
                'tudong_bangtay': 'Tự động',
                'trang_thai': 'Lỗi',
                'noidung_loi': e,
            })
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def output_phaithu_tamung_histaff(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','hoan_tam_ung')])
            if output_ids:
                csvUti = lib_csv.csv_ultilities()
                headers = ['chi_nhanh','ma_chi_nhanh','loai_doi_tuong','ma_doi_tuong','ten_doi_tuong','so_tien','dien_giai']
                contents = []
                sql = '''
                    select cn.name as chi_nhanh, cn.code as ma_chi_nhanh,ai.loai_doituong,dt.ma_doi_tuong as ma_doi_tuong, dt.name as ten_doi_tuong,
                        sum(ai.residual) as so_tien
                        
                        from account_invoice ai 
                        left join account_account cn on cn.id=ai.chinhanh_id
                        left join res_partner dt on dt.id=ai.partner_id
                        
                        where ai.mlg_type='hoan_tam_ung' and state='open'
                        
                        group by cn.name, cn.code,ai.loai_doituong,dt.ma_doi_tuong, dt.name
                '''
                cr. execute(sql)
                for line in cr.dictfetchall():
                    loai_doituong=''
                    if line['loai_doituong']=='taixe':
                        loai_doituong = 'Lái xe'
                    if line['loai_doituong']=='nhadautu':
                        loai_doituong = 'Nhà đầu tư'
                    if line['loai_doituong']=='nhanvienvanphong':
                        loai_doituong = 'Nhân viên văn phòng'
                    contents.append({
                        'chi_nhanh': line['chi_nhanh'],
                        'ma_chi_nhanh': line['ma_chi_nhanh'],
                        'loai_doi_tuong': loai_doituong,
                        'ma_doi_tuong': line['ma_doi_tuong'],
                        'ten_doi_tuong': line['ten_doi_tuong'],
                        'so_tien': line['so_tien'],
                        'dien_giai': '',
                    })
                if contents:
                    for path in output_obj.browse(cr, uid, output_ids):
                        path_file_name = path.name+'/'+'phai_thu_tam_ung_histaff_'+time.strftime('%Y_%m_%d_%H_%M_%S')+'.csv'
                        csvUti._write_file(contents,headers,path_file_name )
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': path_file_name,
                            'loai_giaodich': 'Phải thi tạm ứng (HISTAFF)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Xuất',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
        except Exception, e:
            lichsu_obj.create(cr, uid, {
                'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                'ten_file': '',
                'loai_giaodich': 'Phải thi tạm ứng (HISTAFF)',
                'thu_tra': 'Thu',
                'nhap_xuat': 'Xuất',
                'tudong_bangtay': 'Tự động',
                'trang_thai': 'Lỗi',
                'noidung_loi': e,
            })
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def output_phaithu_kyquy_histaff(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','phai_thu_ky_quy')])
            kyquy_obj = self.pool.get('thu.ky.quy')
            if output_ids:
                csvUti = lib_csv.csv_ultilities()
                headers = ['chi_nhanh','ma_chi_nhanh','loai_doi_tuong','ma_doi_tuong','ten_doi_tuong','so_tien','dien_giai']
                contents = []
                
                sql = '''
                    select rp.id as id,rp.name as name,rp.chinhanh_id as chinhanh_id,rp.ma_doi_tuong as ma_doi_tuong,rp.taixe as taixe,
                        rp.nhanvienvanphong as nhanvienvanphong,rp.sotien_conlai as sotien_conlai,
                        rp.sotien_phaithu_dinhky as sotien_phaithu_dinhky,cn.name as ten_chi_nhanh, cn.code as ma_chi_nhanh
                        from res_partner rp
                        left join account_account cn on cn.id=rp.chinhanh_id
                        where rp.sotien_conlai>0
                '''
                cr.execute(sql)
                for partner in cr.dictfetchall():
                    if partner['sotien_phaithu_dinhky']<=partner['sotien_conlai']:
                        sotien=partner['sotien_phaithu_dinhky']
                    else:
                        sotien=partner['sotien_conlai']
                    loai_doituong=''
                    if partner['taixe']==True:
                        loai_doituong='taixe'
                        contents.append({
                            'chi_nhanh': partner['ten_chi_nhanh'],
                            'ma_chi_nhanh': partner['ma_chi_nhanh'],
                            'loai_doi_tuong': 'Lái xe',
                            'ma_doi_tuong': partner['ma_doi_tuong'],
                            'ten_doi_tuong': partner['name'],
                            'so_tien': sotien,
                            'dien_giai': '',
                        })
                        vals = {
                            'chinhanh_id': partner['chinhanh_id'],
                            'loai_doituong': loai_doituong,
                            'partner_id': partner['id'],
                            'so_tien': sotien,
                            'ngay_thu': time.strftime('%Y-%m-%d'),
                        }
                        kyquy_obj.create(cr, uid, vals)
                    if partner['nhanvienvanphong']==True:
                        loai_doituong='nhanvienvanphong'
                        contents.append({
                            'chi_nhanh': partner['ten_chi_nhanh'],
                            'ma_chi_nhanh': partner['ma_chi_nhanh'],
                            'loai_doi_tuong': 'Nhân viên văn phòng',
                            'ma_doi_tuong': partner['ma_doi_tuong'],
                            'ten_doi_tuong': partner['name'],
                            'so_tien': sotien,
                            'dien_giai': '',
                        })
                        vals = {
                            'chinhanh_id': partner['chinhanh_id'],
                            'loai_doituong': loai_doituong,
                            'partner_id': partner['id'],
                            'so_tien': sotien,
                            'ngay_thu': time.strftime('%Y-%m-%d'),
                        }
                        kyquy_obj.create(cr, uid, vals)
                sql = '''
                    select rp.id as id,rp.ma_doi_tuong as ma_doi_tuong,rp.name as name,cnl.chinhanh_id as chinhanh_id, cn.code as ma_chi_nhanh,
                        cn.name as ten_chi_nhanh,cnl.sotien_phaithu_dinhky as sotien_phaithu_dinhky,cnl.sotien_conlai as sotien_conlai
                        
                        from chi_nhanh_line cnl
                        left join res_partner rp on rp.id=cnl.partner_id
                        left join account_account cn on cn.id=cnl.chinhanh_id
                        
                        where cnl.sotien_conlai>0
                '''
                cr.execute(sql)
                for ndt in cr.dictfetchall():
                    if ndt['sotien_phaithu_dinhky']<=ndt['sotien_conlai']:
                        sotien=ndt['sotien_phaithu_dinhky']
                    else:
                        sotien=ndt['sotien_conlai']
                    loai_doituong='nhadautu'
                    contents.append({
                        'chi_nhanh': ndt['ten_chi_nhanh'],
                        'ma_chi_nhanh': ndt['ma_chi_nhanh'],
                        'loai_doi_tuong': 'Nhà đầu tư',
                        'ma_doi_tuong': ndt['ma_doi_tuong'],
                        'ten_doi_tuong': ndt['name'],
                        'so_tien': sotien,
                        'dien_giai': '',
                    })
                    vals = {
                        'chinhanh_id': ndt['chinhanh_id'],
                        'loai_doituong': loai_doituong,
                        'partner_id': ndt['id'],
                        'so_tien': sotien,
                        'ngay_thu': time.strftime('%Y-%m-%d'),
                    }
                    kyquy_obj.create(cr, uid, vals)
                        
                if contents:
                    for path in output_obj.browse(cr, uid, output_ids):
                        path_file_name = path.name+'/'+'ky_quy_histaff_'+time.strftime('%Y_%m_%d_%H_%M_%S')+'.csv'
                        csvUti._write_file(contents,headers,path_file_name )
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': path_file_name,
                            'loai_giaodich': 'Phải thu ký quỹ (HISTAFF)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Xuất',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
        except Exception, e:
            lichsu_obj.create(cr, uid, {
                'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                'ten_file': '',
                'loai_giaodich': 'Phải thu ký quỹ (HISTAFF)',
                'thu_tra': 'Thu',
                'nhap_xuat': 'Xuất',
                'tudong_bangtay': 'Tự động',
                'trang_thai': 'Lỗi',
                'noidung_loi': e,
            })
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def output_phaithu_doanhsothu_oracle(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','oracle_phaithu')])
            if output_ids:
                csvUti = lib_csv.csv_ultilities()
                headers = ['chi_nhanh','ma_chi_nhanh','loai_cong_no','tai_khoan','so_tien','ghi_chu']
                contents = []
                date_start = time.strftime('%Y-%m-01')
                date_end = str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10]
                sql = '''
                    select * from fin_output_theodoanhsothu_oracle('%s','%s')
                '''%(date_start,date_end)
                cr. execute(sql)
                for line in cr.dictfetchall():
                    contents.append({
                        'chi_nhanh': line['chinhanh'],
                        'ma_chi_nhanh': line['machinhanh'],
                        'loai_cong_no': line['loaicongno'],
                        'tai_khoan': line['taikhoan'],
                        'so_tien': line['sotien'],
                        'ghi_chu': line['ghichu'],
                    })
                if contents:
                    for path in output_obj.browse(cr, uid, output_ids):
                        path_file_name = path.name+'/'+'doanh_so_thu_oracle_'+time.strftime('%Y_%m_%d_%H_%M_%S')+'.csv'
                        csvUti._write_file(contents,headers,path_file_name )
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': path_file_name,
                            'loai_giaodich': 'Doanh số thu (ORACLE)',
                            'thu_tra': 'Thu',
                            'nhap_xuat': 'Xuất',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
        except Exception, e:
            lichsu_obj.create(cr, uid, {
                'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                'ten_file': '',
                'loai_giaodich': 'Doanh số thu (ORACLE)',
                'thu_tra': 'Thu',
                'nhap_xuat': 'Xuất',
                'tudong_bangtay': 'Tự động',
                'trang_thai': 'Lỗi',
                'noidung_loi': e,
            })
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def output_phaithu_doanhsotra_oracle(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','oracle_phaitra')])
            if output_ids:
                csvUti = lib_csv.csv_ultilities()
                headers = ['chi_nhanh','ma_chi_nhanh','loai_cong_no','tai_khoan','so_tien','ghi_chu']
                contents = []
                date_start = time.strftime('%Y-%m-01')
                date_end = str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10]
                sql = '''
                    select * from fin_output_theodoanhsotra_oracle('%s','%s')
                '''%(date_start,date_end)
                cr. execute(sql)
                for line in cr.dictfetchall():
                    contents.append({
                        'chi_nhanh': line['chinhanh'],
                        'ma_chi_nhanh': line['machinhanh'],
                        'loai_cong_no': line['loaicongno'],
                        'tai_khoan': line['taikhoan'],
                        'so_tien': line['sotien'],
                        'ghi_chu': line['ghichu'],
                    })
                if contents:
                    for path in output_obj.browse(cr, uid, output_ids):
                        path_file_name = path.name+'/'+'doanh_so_tra_oracle_'+time.strftime('%Y_%m_%d_%H_%M_%S')+'.csv'
                        csvUti._write_file(contents,headers,path_file_name )
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': path_file_name,
                            'loai_giaodich': 'Doanh số trả (ORACLE)',
                            'thu_tra': 'Trả',
                            'nhap_xuat': 'Xuất',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
        except Exception, e:
            lichsu_obj.create(cr, uid, {
                'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                'ten_file': '',
                'loai_giaodich': 'Doanh số trả (ORACLE)',
                'thu_tra': 'Trả',
                'nhap_xuat': 'Xuất',
                'tudong_bangtay': 'Tự động',
                'trang_thai': 'Lỗi',
                'noidung_loi': e,
            })
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def output_phaitra_chigopxe_htkd(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        lichsu_obj = self.pool.get('lichsu.giaodich')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','chi_ho')])
            invoice_obj = self.pool.get('account.invoice')
            if output_ids:
                date_start = time.strftime('%Y-%m-01')
                date_end = str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10]
                csvUti = lib_csv.csv_ultilities()
                headers = ['chi_nhanh','ma_chi_nhanh','loai_doi_tuong','ma_doi_tuong','ten_doi_tuong','ngay_phat_sinh','bien_so_xe','so_tien','so_hop_dong','dien_giai','ngay_thanh_toan','so_tien_da_chi']
                contents = []
                sql = '''
                    select ai.id as invoice_id,cn.name as chi_nhanh, cn.code as ma_chi_nhanh,ai.loai_doituong,dt.ma_doi_tuong as ma_doi_tuong, dt.name as ten_doi_tuong,
                        ai.date_invoice as ngay_giao_dich,bsx.name as bien_so_xe, ai.so_hop_dong as so_hop_dong, ai.so_tien as so_tien,
                        ai.dien_giai as dien_giai, ai.residual as residual
                        
                        from account_invoice ai 
                        left join account_account cn on cn.id=ai.chinhanh_id
                        left join res_partner dt on dt.id=ai.partner_id
                        left join bien_so_xe bsx on bsx.id=ai.bien_so_xe_id
                        where ai.mlg_type='chi_ho' and state in ('open','paid')
                '''
                cr. execute(sql)
                for line in cr.dictfetchall():
                    loai_doituong=''
                    if line['loai_doituong']=='taixe':
                        loai_doituong = 'Lái xe'
                    if line['loai_doituong']=='nhadautu':
                        loai_doituong = 'Nhà đầu tư'
                    if line['loai_doituong']=='nhanvienvanphong':
                        loai_doituong = 'Nhân viên văn phòng'
                        
                    invoice = invoice_obj.browse(cr, uid, line['invoice_id'])
                    if invoice.payment_ids:
                        for payment in invoice.payment_ids:
                            if payment.date>=date_start and payment.date<=date_end:
                                ngay_thanh_toan_arr = payment.date.split('-')
                                ngay_thanh_toan = ngay_thanh_toan_arr[2]+'/'+ngay_thanh_toan_arr[1]+'/'+ngay_thanh_toan_arr[0]
                                contents.append({
                                    'chi_nhanh': line['chi_nhanh'],
                                    'ma_chi_nhanh': line['ma_chi_nhanh'],
                                    'loai_doi_tuong': loai_doituong,
                                    'ma_doi_tuong': line['ma_doi_tuong'],
                                    'ten_doi_tuong': line['ten_doi_tuong'],
                                    'ngay_phat_sinh': line['ngay_giao_dich'],
                                    'bien_so_xe': line['bien_so_xe'],
                                    'so_tien': line['so_tien'],
                                    'so_hop_dong': line['so_hop_dong'],
                                    'dien_giai': line['dien_giai'],
                                    'ngay_thanh_toan': ngay_thanh_toan,
                                    'so_tien_da_chi': payment.debit,
                                })
                if contents:
                    for path in output_obj.browse(cr, uid, output_ids):
                        path_file_name = path.name+'/'+'chi_gop_xe_htkd_'+time.strftime('%Y_%m_%d_%H_%M_%S')+'.csv'
                        csvUti._write_file(contents,headers,path_file_name )
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'ten_file': path_file_name,
                            'loai_giaodich': 'Chi góp xe (HTKD)',
                            'thu_tra': 'Trả',
                            'nhap_xuat': 'Xuất',
                            'tudong_bangtay': 'Tự động',
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
        except Exception, e:
            lichsu_obj.create(cr, uid, {
                'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                'ten_file': '',
                'loai_giaodich': 'Chi góp xe (HTKD)',
                'thu_tra': 'Trả',
                'nhap_xuat': 'Xuất',
                'tudong_bangtay': 'Tự động',
                'trang_thai': 'Lỗi',
                'noidung_loi': e,
            })
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
output_congno_tudong()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
