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

# from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class output_congno_tudong(osv.osv):
    _name = 'output.congno.tudong'

    _columns = {
        'name': fields.date('Tên', required=True),
    }
    
    def output_phaithu_thunoxuong_bdsc(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','thu_no_xuong')])
            if output_ids:
                invoice_obj = self.pool.get('account.invoice')
                
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
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def output_phaithu_thuphithuonghieu_htkd(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','thu_phi_thuong_hieu_htkd')])
            if output_ids:
                invoice_obj = self.pool.get('account.invoice')
                
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
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def output_phaithu_tragopxe_htkd(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','tra_gop_xe_htkd')])
            if output_ids:
                invoice_obj = self.pool.get('account.invoice')
                
                csvUti = lib_csv.csv_ultilities()
                headers = ['chi_nhanh','ma_chi_nhanh','loai_doi_tuong','ma_doi_tuong','ten_doi_tuong','ngay_phat_sinh','bien_so_xe','so_hop_dong','so_tien','don_vi_chi','dien_giai','ngay_thanh_toan','so_tien_da_thu']
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
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True

    def output_phaithu_thuphithuonghieu_shift(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
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
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def output_phaithu_tragopxe_shift(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
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
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def output_phaithu_phatvipham_histaff(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
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
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def output_phaithu_tamung_histaff(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
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
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def output_phaithu_kyquy_histaff(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','phai_thu_ky_quy')])
            kyquy_obj = self.pool.get('thu.ky.quy')
            if output_ids:
                csvUti = lib_csv.csv_ultilities()
                headers = ['chi_nhanh','ma_chi_nhanh','loai_doi_tuong','ma_doi_tuong','ten_doi_tuong','so_tien','dien_giai']
                contents = []
                
                sql = '''
                    select rp.id as id,rp.name as name,rp.chinhanh_id as chinhanh_id,rp.ma_doi_tuong as ma_doi_tuong,rp.taixe as taixe,
                        rp.nhadautu as nhadautu,rp.nhanvienvanphong as nhanvienvanphong,rp.sotien_conlai as sotien_conlai,
                        rp.sotien_phaithu_dinhky as sotien_phaithu_dinhky,cn.name as ten_chi_nhanh, cn.code as ma_chi_nhanh
                        from res_partner rp
                        left join account_account cn on cn.id=rp.chinhanh_id
                        where sotien_conlai>0
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
                            'loai_doi_tuong': 'loai_doituong',
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
                            'loai_doi_tuong': loai_doituong,
                            'ma_doi_tuong': partner['ma_doi_tuong'],
                            'ten_doi_tuong': partner['name'],
                            'so_tien': sotien,
                            'dien_giai': '',
                        })
                        vals = {
                            'chinhanh_id': partner['chinhanh_id'],
                            'loai_doi_tuong': 'Nhân viên văn phòng',
                            'partner_id': partner['id'],
                            'so_tien': sotien,
                            'ngay_thu': time.strftime('%Y-%m-%d'),
                        }
                        kyquy_obj.create(cr, uid, vals)
                    if partner['nhadautu']==True:
                        loai_doituong='nhadautu'
                        sql = '''
                            select cnl.chinhanh_id as chinhanh_id, cn.code as ma_chi_nhanh, cn.name as ten_chi_nhanh
                                from chi_nhanh_line cnl
                                left join account_account cn on cn.id=cnl.chinhanh_id
                                where partner_id=%s
                        '''%(partner['id'])
                        cr.execute(sql)
                        for ndt in cr.dictfetchall():
                            contents.append({
                                'chi_nhanh': ndt['ten_chi_nhanh'],
                                'ma_chi_nhanh': ndt['ma_chi_nhanh'],
                                'loai_doi_tuong': 'Nhà đầu tư',
                                'ma_doi_tuong': partner['ma_doi_tuong'],
                                'ten_doi_tuong': partner['name'],
                                'so_tien': sotien,
                                'dien_giai': '',
                            })
                            vals = {
                                'chinhanh_id': ndt['chinhanh_id'],
                                'loai_doi_tuong': loai_doituong,
                                'partner_id': partner['id'],
                                'so_tien': sotien,
                                'ngay_thu': time.strftime('%Y-%m-%d'),
                            }
                            kyquy_obj.create(cr, uid, vals)
                        
                if contents:
                    for path in output_obj.browse(cr, uid, output_ids):
                        path_file_name = path.name+'/'+'ky_quy_histaff_'+time.strftime('%Y_%m_%d_%H_%M_%S')+'.csv'
                        csvUti._write_file(contents,headers,path_file_name )
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
    def output_oracle_phaithu(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','oracle_phaithu')])
            if output_ids:
                csvUti = lib_csv.csv_ultilities()
                headers = ['chi_nhanh','ma_chi_nhanh','loai_doanh_thu','so_tien','dien_giai']
                contents = []
                sql = '''
                    select cn.name as chi_nhanh, cn.code as ma_chi_nhanh,ai.mlg_type as loai_doanh_thu,ai.so_tien as so_tien,
                        ai.dien_giai as dien_giai
                        
                        from account_invoice ai 
                        left join account_account cn on cn.id=ai.chinhanh_id
                        
                        where ai.type='out_invoice'
                '''
                cr. execute(sql)
                for line in cr.dictfetchall():
                    loai_doanh_thu=''
                    if line['loai_doanh_thu']=='no_doanh_thu':
                        loai_doanh_thu='Nợ doanh thu'
                    if line['loai_doanh_thu']=='chi_ho_dien_thoai':
                        loai_doanh_thu='Phải thu chi hộ điện thoại'
                    if line['loai_doanh_thu']=='phai_thu_bao_hiem':
                        loai_doanh_thu='Phải thu bảo hiểm'
                    if line['loai_doanh_thu']=='phai_thu_ky_quy':
                        loai_doanh_thu='Phải thu ký quỹ'
                    if line['loai_doanh_thu']=='phat_vi_pham':
                        loai_doanh_thu='Phạt vi phạm'
                    if line['loai_doanh_thu']=='thu_no_xuong':
                        loai_doanh_thu='Thu nợ xưởng'
                    if line['loai_doanh_thu']=='thu_phi_thuong_hieu':
                        loai_doanh_thu='Thu phí thương hiệu'
                    if line['loai_doanh_thu']=='tra_gop_xe':
                        loai_doanh_thu='Trả góp xe'
                    if line['loai_doanh_thu']=='hoan_tam_ung':
                        loai_doanh_thu='Phải thu tạm ứng'
                    contents.append({
                        'chi_nhanh': line['chi_nhanh'],
                        'ma_chi_nhanh': line['ma_chi_nhanh'],
                        'loai_doanh_thu': loai_doanh_thu,
                        'so_tien': line['so_tien'],
                        'dien_giai': line['dien_giai'],
                    })
                if contents:
                    for path in output_obj.browse(cr, uid, output_ids):
                        path_file_name = path.name+'/'+'oracle_'+time.strftime('%Y_%m_%d_%H_%M_%S')+'.csv'
                        csvUti._write_file(contents,headers,path_file_name )
        except Exception, e:
            pass
        return True
    
    def output_phaitra_chigopxe_htkd(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','chi_ho')])
            invoice_obj = self.pool.get('account.invoice')
            if output_ids:
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
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
output_congno_tudong()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
