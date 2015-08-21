# -*- coding: utf-8 -*-
##############################################################################
#
#    HLVSolution, Open Source Management Solution
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
import random
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        
        self.localcontext.update({
             'get_from_date':self.get_from_date,
             'get_to_date':self.get_to_date,
             'get_vietname_date': self.get_vietname_date,
             'get_loai_hoso': self.get_loai_hoso,
             'get_hoso_line': self.get_hoso_line,
             'get_nhadautu_nn_line': self.get_nhadautu_nn_line,
             'get_date_now': self.get_date_now,
        })
    
    def get_date_now(self):
        return time.strftime('%Y-%m-%d')
    
    def get_vietname_date(self, date):
        if not date:
            return ''
#             date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_from_date(self):
        wizard_data = self.localcontext['data']['form']
        from_date = wizard_data['date_from']
        return from_date
    
    def get_to_date(self):
        wizard_data = self.localcontext['data']['form']
        to_date = wizard_data['date_to']
        return to_date
    
    def get_loai_hoso(self):
        wizard_data = self.localcontext['data']['form']
        to_date = wizard_data['date_to']
        sql = '''
            SELECT id ,name 
            FROM loai_ho_so
        '''
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_hoso_line(self, loai_hoso_id, report):
        hoso_obj = self.pool.get('giay.chung.nhan.dau.tu')
        nhadautu_obj = self.pool.get('res.partner')
        temp = 0
        wizard_data = self.localcontext['data']['form']
        from_date = wizard_data['date_from']
        to_date = wizard_data['date_to']
        res = []
        if report=='cap':
            hoso_ids = hoso_obj.search(self.cr, self.uid, [('state','=','done'),('loai_ho_so','=',loai_hoso_id),('chung_nhan_lan_dau','>=',from_date),('chung_nhan_lan_dau','<=',to_date)])
        if report=='thuhoi':
            hoso_ids = hoso_obj.search(self.cr, self.uid, [('state','=','refuse'),('loai_ho_so','=',loai_hoso_id),('chung_nhan_lan_dau','>=',from_date),('chung_nhan_lan_dau','<=',to_date)])
        for hoso in hoso_obj.browse(self.cr, self.uid, hoso_ids):
            nha_dau_tu_ids = [x.id for x in hoso.nha_dau_tu]
            nhadautu_nn_ids = nhadautu_obj.search(self.cr, self.uid, [('id','in',nha_dau_tu_ids),('country_id.code','!=','VN')])
            nhadautu_vn_ids = nhadautu_obj.search(self.cr, self.uid, [('id','in',nha_dau_tu_ids),('country_id.code','=','VN')])
            
            res.append({})
            res[temp]['ma_so'] = hoso.ma_so
            res[temp]['chung_nhan_lan_dau'] = hoso.chung_nhan_lan_dau
            res[temp]['ten_du_an'] = hoso.ten_du_an
            res[temp]['hinh_thuc_dau_tu'] = hoso.hinh_thuc_dau_tu_id and hoso.hinh_thuc_dau_tu_id.name or False
            res[temp]['ten_tieng_viet'] = hoso.ten_tieng_viet
            res[temp]['doanh_nghiep'] = hoso.loai_hinh_doanh_nghiep and hoso.loai_hinh_doanh_nghiep.name or False
            res[temp]['von_dau_tu_us'] = hoso.von_dau_tu_us
            res[temp]['von_dieu_le_us'] = hoso.von_dieu_le_us
            res[temp]['muc_tieu_du_an'] = hoso.muc_tieu_du_an
            res[temp]['nganh_nghe_khac'] = hoso.nganh_nghe_khac
            res[temp]['thoi_han_hoat_dong'] = hoso.thoi_han_hoat_dong
            res[temp]['dia_chi_tru_so'] = ''
            res[temp]['dia_chi_du_an'] = hoso.dia_chi_du_an
            res[temp]['ten_ndt_nn'] = ''
            res[temp]['diachi_ndt_nn'] = ''
            res[temp]['nuoc_ndt_nn'] = ''
            res[temp]['ten_ndt_vn'] = ''
            res[temp]['diachi_ndt_vn'] = ''
                        
            dem = 0
            if max(len(nhadautu_nn_ids),len(nhadautu_vn_ids))!=0:
                while (dem < max(len(nhadautu_nn_ids),len(nhadautu_vn_ids))):
                    if dem > 0:
                        res.append({})
                        res[temp]['ma_so'] = ''
                        res[temp]['ten_du_an'] = ''
                        res[temp]['chung_nhan_lan_dau'] = ''
                        res[temp]['hinh_thuc_dau_tu'] = ''
                        res[temp]['ten_tieng_viet'] = ''
                        res[temp]['doanh_nghiep'] = ''
                        res[temp]['von_dau_tu_us'] = ''
                        res[temp]['von_dieu_le_us'] = ''
                        res[temp]['muc_tieu_du_an'] = ''
                        res[temp]['nganh_nghe_khac'] = ''
                        res[temp]['thoi_han_hoat_dong'] = ''
                        res[temp]['dia_chi_tru_so'] = ''
                        res[temp]['dia_chi_du_an'] = ''
                    if dem < len(nhadautu_nn_ids) and len(nhadautu_nn_ids)!=0:
                        nhadautu_nn = nhadautu_obj.browse(self.cr, self.uid, nhadautu_nn_ids[dem])
                        res[temp]['ten_ndt_nn'] = nhadautu_nn.name
                        res[temp]['diachi_ndt_nn'] = str(nhadautu_nn.street or '') + ', ' + str(nhadautu_nn.state_id and nhadautu_nn.state_id.name or '') + ', ' + str(nhadautu_nn.country_id and nhadautu_nn.country_id.name or '')
                        res[temp]['nuoc_ndt_nn'] = nhadautu_nn.noi_cap_phep_thanh_lap or nhadautu_nn.noi_cap_cmnd_hc
                    else:
                        res[temp]['ten_ndt_nn'] = ''
                        res[temp]['diachi_ndt_nn'] = ''
                        res[temp]['nuoc_ndt_nn'] = ''
                    if dem < len(nhadautu_vn_ids) and len(nhadautu_vn_ids)!=0:
                        nhadautu_vn = nhadautu_obj.browse(self.cr, self.uid, nhadautu_vn_ids[dem])
                        res[temp]['ten_ndt_vn'] = nhadautu_vn.name
                        res[temp]['diachi_ndt_vn'] = str(nhadautu_vn.street or '') + ', ' + str(nhadautu_vn.state_id and nhadautu_vn.state_id.name or '') + ', ' + str(nhadautu_vn.country_id and nhadautu_vn.country_id.name or '')
                    else:
                        res[temp]['ten_ndt_vn'] = ''
                        res[temp]['diachi_ndt_vn'] = ''
                    dem += 1
                    temp += 1
            else:
                temp += 1
        return res
    
    def get_nhadautu_nn_line(self, hoso_id):
        nhadautu_obj = self.pool.get('res.partner')
        sql = '''
            SELECT id 
            FROM res_partner
            WHERE id in (SELECT partner_id FROM nha_dau_tu_rel WHERE ho_so_id in (SELECT id FROM giay_chung_nhan_dau_tu WHERE id=%(hoso_id)s))
                and country_id in (SELECT id FROM res_country WHERE code != 'VN')
        '''%{'hoso_id': hoso_id,
             }
        self.cr.execute(sql)
        nhadautu_ids = [row[0] for row in self.cr.fetchall()]
        nhadautus = nhadautu_obj.browse(self.cr, self.uid, nhadautu_ids)
        return nhadautus
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
