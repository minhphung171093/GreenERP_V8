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
    
    def output_thu_noxuong(self, cr, uid, context=None):
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
                        
                        where ai.mlg_type='thu_no_xuong'
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
                            contents.append({
                                'chi_nhanh': line['chi_nhanh'],
                                'ma_chi_nhanh': line['ma_chi_nhanh'],
                                'loai_doi_tuong': loai_doituong,
                                'ma_doi_tuong': line['ma_doi_tuong'],
                                'ten_doi_tuong': line['ten_doi_tuong'],
                                'ngay_giao_dich': line['ngay_giao_dich'],
                                'bien_so_xe': line['bien_so_xe'],
                                'so_hop_dong': line['so_hop_dong'],
                                'ma_chiet_tinh': line['ma_chiet_tinh'],
                                'ma_xuong': line['ma_xuong'],
                                'so_tien': line['so_tien'],
                                'dien_giai': line['dien_giai'],
                                'ngay_thanh_toan': payment.date,
                                'so_tien_da_thu': payment.credit,
                            })
                    else:
                        contents.append({
                            'chi_nhanh': line['chi_nhanh'],
                            'ma_chi_nhanh': line['ma_chi_nhanh'],
                            'loai_doi_tuong': loai_doituong,
                            'ma_doi_tuong': line['ma_doi_tuong'],
                            'ten_doi_tuong': line['ten_doi_tuong'],
                            'ngay_giao_dich': line['ngay_giao_dich'],
                            'bien_so_xe': line['bien_so_xe'],
                            'so_hop_dong': line['so_hop_dong'],
                            'ma_chiet_tinh': line['ma_chiet_tinh'],
                            'ma_xuong': line['ma_xuong'],
                            'so_tien': line['so_tien'],
                            'dien_giai': line['dien_giai'],
                            'ngay_thanh_toan': '',
                            'so_tien_da_thu': line['so_tien']-line['residual'],
                        })
                if contents:
                    for path in output_obj.browse(cr, uid, output_ids):
                        path_file_name = path.name+'/'+'thu_no_xuong_'+time.strftime('%Y_%m_%d_%H_%M_%S')+'.csv'
                        csvUti._write_file(contents,headers,path_file_name )
        except Exception, e:
            pass
        return True

    def output_ky_quy(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','phai_thu_ky_quy')])
            if output_ids:
                csvUti = lib_csv.csv_ultilities()
                headers = ['chi_nhanh','ma_chi_nhanh','loai_doi_tuong','ma_doi_tuong','ten_doi_tuong','so_tien','dien_giai']
                contents = []
                sql = '''
                    select cn.name as chi_nhanh, cn.code as ma_chi_nhanh,tkq.loai_doituong,dt.ma_doi_tuong as ma_doi_tuong, dt.name as ten_doi_tuong,
                        tkq.so_tien as so_tien, tkq.dien_giai as dien_giai
                        
                        from thu_ky_quy tkq 
                        left join account_account cn on cn.id=tkq.chinhanh_id
                        left join res_partner dt on dt.id=tkq.partner_id
                        
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
                        'dien_giai': line['dien_giai'],
                    })
                if contents:
                    for path in output_obj.browse(cr, uid, output_ids):
                        path_file_name = path.name+'/'+'ky_quy_'+time.strftime('%Y_%m_%d_%H_%M_%S')+'.csv'
                        csvUti._write_file(contents,headers,path_file_name )
        except Exception, e:
            pass
        return True
    
    def output_phat_vi_pham(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','phat_vi_pham')])
            if output_ids:
                csvUti = lib_csv.csv_ultilities()
                headers = ['chi_nhanh','ma_chi_nhanh','loai_doi_tuong','ma_doi_tuong','ten_doi_tuong','so_tien','dien_giai']
                contents = []
                sql = '''
                    select cn.name as chi_nhanh, cn.code as ma_chi_nhanh,ai.loai_doituong,dt.ma_doi_tuong as ma_doi_tuong, dt.name as ten_doi_tuong,
                        ai.so_tien as so_tien, ai.dien_giai as dien_giai
                        
                        from account_invoice ai 
                        left join account_account cn on cn.id=ai.chinhanh_id
                        left join res_partner dt on dt.id=ai.partner_id
                        
                        where ai.mlg_type='phat_vi_pham'
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
                        'dien_giai': line['dien_giai'],
                    })
                if contents:
                    for path in output_obj.browse(cr, uid, output_ids):
                        path_file_name = path.name+'/'+'phat_vi_pham_'+time.strftime('%Y_%m_%d_%H_%M_%S')+'.csv'
                        csvUti._write_file(contents,headers,path_file_name )
        except Exception, e:
            pass
        return True
    
    def output_phaithu_tamung(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','hoan_tam_ung')])
            if output_ids:
                csvUti = lib_csv.csv_ultilities()
                headers = ['chi_nhanh','ma_chi_nhanh','loai_doi_tuong','ma_doi_tuong','ten_doi_tuong','so_tien','dien_giai']
                contents = []
                sql = '''
                    select cn.name as chi_nhanh, cn.code as ma_chi_nhanh,ai.loai_doituong,dt.ma_doi_tuong as ma_doi_tuong, dt.name as ten_doi_tuong,
                        ai.so_tien as so_tien, ai.dien_giai as dien_giai
                        
                        from account_invoice ai 
                        left join account_account cn on cn.id=ai.chinhanh_id
                        left join res_partner dt on dt.id=ai.partner_id
                        
                        where ai.mlg_type='hoan_tam_ung'
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
                        'dien_giai': line['dien_giai'],
                    })
                if contents:
                    for path in output_obj.browse(cr, uid, output_ids):
                        path_file_name = path.name+'/'+'tam_ung_'+time.strftime('%Y_%m_%d_%H_%M_%S')+'.csv'
                        csvUti._write_file(contents,headers,path_file_name )
        except Exception, e:
            pass
        return True
    
    def output_thuphi_thuonghieu_htkd(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','thu_phi_thuong_hieu_htkd')])
            invoice_obj = self.pool.get('account.invoice')
            if output_ids:
                csvUti = lib_csv.csv_ultilities()
                headers = ['chi_nhanh','ma_chi_nhanh','loai_doi_tuong','ma_doi_tuong','ten_doi_tuong','ngay_giao_dich','bien_so_xe','so_tien','so_hop_dong','dien_giai','ngay_thanh_toan','so_tien_da_thu']
                contents = []
                sql = '''
                    select ai.id as invoice_id,cn.name as chi_nhanh, cn.code as ma_chi_nhanh,ai.loai_doituong,dt.ma_doi_tuong as ma_doi_tuong, dt.name as ten_doi_tuong,
                        ai.date_invoice as ngay_giao_dich,bsx.name as bien_so_xe, ai.so_hop_dong as so_hop_dong, ai.so_tien as so_tien,
                        ai.dien_giai as dien_giai, ai.residual as residual
                        
                        from account_invoice ai 
                        left join account_account cn on cn.id=ai.chinhanh_id
                        left join res_partner dt on dt.id=ai.partner_id
                        left join bien_so_xe bsx on bsx.id=ai.bien_so_xe_id
                        
                        where ai.mlg_type='thu_phi_thuong_hieu'
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
                            contents.append({
                                'chi_nhanh': line['chi_nhanh'],
                                'ma_chi_nhanh': line['ma_chi_nhanh'],
                                'loai_doi_tuong': loai_doituong,
                                'ma_doi_tuong': line['ma_doi_tuong'],
                                'ten_doi_tuong': line['ten_doi_tuong'],
                                'ngay_giao_dich': line['ngay_giao_dich'],
                                'bien_so_xe': line['bien_so_xe'],
                                'so_tien': line['so_tien'],
                                'so_hop_dong': line['so_hop_dong'],
                                'dien_giai': line['dien_giai'],
                                'ngay_thanh_toan': payment.date,
                                'so_tien_da_thu': payment.credit,
                            })
                    else:
                        contents.append({
                            'chi_nhanh': line['chi_nhanh'],
                            'ma_chi_nhanh': line['ma_chi_nhanh'],
                            'loai_doi_tuong': loai_doituong,
                            'ma_doi_tuong': line['ma_doi_tuong'],
                            'ten_doi_tuong': line['ten_doi_tuong'],
                            'ngay_giao_dich': line['ngay_giao_dich'],
                            'bien_so_xe': line['bien_so_xe'],
                            'so_tien': line['so_tien'],
                            'so_hop_dong': line['so_hop_dong'],
                            'dien_giai': line['dien_giai'],
                            'ngay_thanh_toan': '',
                            'so_tien_da_thu': line['so_tien']-line['residual'],
                        })
                if contents:
                    for path in output_obj.browse(cr, uid, output_ids):
                        path_file_name = path.name+'/'+'thu_phi_thuong_hieu_htkd_'+time.strftime('%Y_%m_%d_%H_%M_%S')+'.csv'
                        csvUti._write_file(contents,headers,path_file_name )
        except Exception, e:
            pass
        return True
    
    def output_tra_gop_xe_htkd(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','tra_gop_xe_htkd')])
            invoice_obj = self.pool.get('account.invoice')
            if output_ids:
                csvUti = lib_csv.csv_ultilities()
                headers = ['chi_nhanh','ma_chi_nhanh','loai_doi_tuong','ma_doi_tuong','ten_doi_tuong','ngay_giao_dich','bien_so_xe','so_tien','so_hop_dong','don_vi_chi','dien_giai','ngay_thanh_toan','so_tien_da_thu']
                contents = []
                sql = '''
                    select ai.id as invoice_id,cn.name as chi_nhanh, cn.code as ma_chi_nhanh,ai.loai_doituong,dt.ma_doi_tuong as ma_doi_tuong, dt.name as ten_doi_tuong,
                        ai.date_invoice as ngay_giao_dich,bsx.name as bien_so_xe, ai.so_hop_dong as so_hop_dong, ai.so_tien as so_tien,
                        ai.dien_giai as dien_giai, ai.residual as residual,dvc.ma_doi_tuong as don_vi_chi
                        
                        from account_invoice ai 
                        left join account_account cn on cn.id=ai.chinhanh_id
                        left join res_partner dt on dt.id=ai.partner_id
                        left join bien_so_xe bsx on bsx.id=ai.bien_so_xe_id
                        left join res_partner dvc on dvc.id=ai.thu_cho_doituong_id
                        where ai.mlg_type='tra_gop_xe'
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
                            contents.append({
                                'chi_nhanh': line['chi_nhanh'],
                                'ma_chi_nhanh': line['ma_chi_nhanh'],
                                'loai_doi_tuong': loai_doituong,
                                'ma_doi_tuong': line['ma_doi_tuong'],
                                'ten_doi_tuong': line['ten_doi_tuong'],
                                'ngay_giao_dich': line['ngay_giao_dich'],
                                'bien_so_xe': line['bien_so_xe'],
                                'so_tien': line['so_tien'],
                                'so_hop_dong': line['so_hop_dong'],
                                'don_vi_chi': line['don_vi_chi'],
                                'dien_giai': line['dien_giai'],
                                'ngay_thanh_toan': payment.date,
                                'so_tien_da_thu': payment.credit,
                            })
                    else:
                        contents.append({
                            'chi_nhanh': line['chi_nhanh'],
                            'ma_chi_nhanh': line['ma_chi_nhanh'],
                            'loai_doi_tuong': loai_doituong,
                            'ma_doi_tuong': line['ma_doi_tuong'],
                            'ten_doi_tuong': line['ten_doi_tuong'],
                            'ngay_giao_dich': line['ngay_giao_dich'],
                            'bien_so_xe': line['bien_so_xe'],
                            'so_tien': line['so_tien'],
                            'so_hop_dong': line['so_hop_dong'],
                            'don_vi_chi': line['don_vi_chi'],
                            'dien_giai': line['dien_giai'],
                            'ngay_thanh_toan': '',#line['chi_nhanh'],
                            'so_tien_da_thu': line['so_tien']-line['residual'],
                        })
                if contents:
                    for path in output_obj.browse(cr, uid, output_ids):
                        path_file_name = path.name+'/'+'tra_gop_xe_htkd_'+time.strftime('%Y_%m_%d_%H_%M_%S')+'.csv'
                        csvUti._write_file(contents,headers,path_file_name )
        except Exception, e:
            pass
        return True
    
    def output_thuphi_thuonghieu_shift(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','thu_phi_thuong_hieu_shift')])
            if output_ids:
                csvUti = lib_csv.csv_ultilities()
                headers = ['chi_nhanh','ma_chi_nhanh','loai_doi_tuong','ma_doi_tuong','ten_doi_tuong','ngay_giao_dich','bien_so_xe','so_tien','so_hop_dong','dien_giai']
                contents = []
                sql = '''
                    select cn.name as chi_nhanh, cn.code as ma_chi_nhanh,ai.loai_doituong,dt.ma_doi_tuong as ma_doi_tuong, dt.name as ten_doi_tuong,
                        ai.date_invoice as ngay_giao_dich,bsx.name as bien_so_xe,ai.so_tien as so_tien, ai.so_hop_dong as so_hop_dong, ai.dien_giai as dien_giai
                        
                        from account_invoice ai 
                        left join account_account cn on cn.id=ai.chinhanh_id
                        left join res_partner dt on dt.id=ai.partner_id
                        left join bien_so_xe bsx on bsx.id=ai.bien_so_xe_id
                        
                        where ai.mlg_type='thu_phi_thuong_hieu'
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
                        'ngay_giao_dich': line['ngay_giao_dich'],
                        'bien_so_xe': line['bien_so_xe'],
                        'so_tien': line['so_tien'],
                        'so_hop_dong': line['so_hop_dong'],
                        'dien_giai': line['dien_giai'],
                    })
                if contents:
                    for path in output_obj.browse(cr, uid, output_ids):
                        path_file_name = path.name+'/'+'thuphi_thuonghieu_shift_'+time.strftime('%Y_%m_%d_%H_%M_%S')+'.csv'
                        csvUti._write_file(contents,headers,path_file_name )
        except Exception, e:
            pass
        return True
    
    def output_tra_gop_xe_shift(self, cr, uid, context=None):
        output_obj = self.pool.get('cauhinh.thumuc.output.tudong')
        try:
            output_ids = output_obj.search(cr, uid, [('mlg_type','=','tra_gop_xe_shift')])
            if output_ids:
                csvUti = lib_csv.csv_ultilities()
                headers = ['chi_nhanh','ma_chi_nhanh','loai_doi_tuong','ma_doi_tuong','ten_doi_tuong','ngay_phat_sinh','so_tien','bien_so_xe','so_hop_dong','dien_giai']
                contents = []
                sql = '''
                    select cn.name as chi_nhanh, cn.code as ma_chi_nhanh,ai.loai_doituong,dt.ma_doi_tuong as ma_doi_tuong, dt.name as ten_doi_tuong,
                        ai.date_invoice as ngay_giao_dich,bsx.name as bien_so_xe, ai.so_hop_dong as so_hop_dong, ai.so_tien as so_tien,
                        ai.dien_giai as dien_giai, ai.residual as residual,dvc.ma_doi_tuong as don_vi_chi
                        
                        from account_invoice ai 
                        left join account_account cn on cn.id=ai.chinhanh_id
                        left join res_partner dt on dt.id=ai.partner_id
                        left join bien_so_xe bsx on bsx.id=ai.bien_so_xe_id
                        left join res_partner dvc on dvc.id=ai.thu_cho_doituong_id
                        where ai.mlg_type='tra_gop_xe'
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
                        'ngay_phat_sinh': line['ngay_giao_dich'],
                        'so_tien': line['so_tien'],
                        'bien_so_xe': line['bien_so_xe'],
                        'so_hop_dong': line['so_hop_dong'],
                        'dien_giai': line['dien_giai'],
                    })
                if contents:
                    for path in output_obj.browse(cr, uid, output_ids):
                        path_file_name = path.name+'/'+'tra_gop_xe_shift_'+time.strftime('%Y_%m_%d_%H_%M_%S')+'.csv'
                        csvUti._write_file(contents,headers,path_file_name )
        except Exception, e:
            pass
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
    
    def output_chi_gop_xe(self, cr, uid, context=None):
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
                        where ai.mlg_type='chi_ho'
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
                                'ngay_thanh_toan': payment.date,
                                'so_tien_da_chi': payment.debit,
                            })
                    else:
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
                            'ngay_thanh_toan': '',#line['chi_nhanh'],
                            'so_tien_da_chi': line['so_tien']-line['residual'],
                        })
                if contents:
                    for path in output_obj.browse(cr, uid, output_ids):
                        path_file_name = path.name+'/'+'chi_gop_xe_'+time.strftime('%Y_%m_%d_%H_%M_%S')+'.csv'
                        csvUti._write_file(contents,headers,path_file_name )
        except Exception, e:
            pass
        return True
    
output_congno_tudong()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
