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
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.tongcongno = 0
        self.tongnodauky = 0
        self.tongno = 0
        self.tongco = 0
        self.tongcong_congno = 0
        self.tongcong_nodauky = 0
        self.tongcong_no = 0
        self.tongcong_co = 0
        
        self.loaidoituong = []
        self.loai_congno_tuongung = []
        self.partner_dict = {}
        self.congno_dict = {}
        
        self.localcontext.update({
            'get_doituong': self.get_doituong,
            'convert_date': self.convert_date,
            'get_title_doituong': self.get_title_doituong,
            'get_nodauky': self.get_nodauky,
            'convert_amount': self.convert_amount,
            'get_chitiet_congno': self.get_chitiet_congno,
            'get_nocuoiky': self.get_nocuoiky,
            'get_tongcongno': self.get_tongcongno,
            'get_from_thang': self.get_from_thang,
            'get_to_thang': self.get_to_thang,
            'get_chinhanh': self.get_chinhanh,
            'get_title': self.get_title,
            'get_loaidoituong': self.get_loaidoituong,
            'get_name_loaidoituong': self.get_name_loaidoituong,
            'get_tongnodauky': self.get_tongnodauky,
            'get_tongno': self.get_tongno,
            'get_tongco': self.get_tongco,
            'get_loai_congno_tuongung': self.get_loai_congno_tuongung,
            'get_title_lcntu': self.get_title_lcntu,
            'get_madoituong': self.get_madoituong,
            'get_tendoituong': self.get_tendoituong,
            'get_no': self.get_no,
            'get_co': self.get_co,
            'get_tongcong_congno': self.get_tongcong_congno,
            'get_tongcong_nodauky': self.get_tongcong_nodauky,
            'get_tongcong_no': self.get_tongcong_no,
            'get_tongcong_co': self.get_tongcong_co,
            
            'get_khoitao': self.get_khoitao,
        })
    
    def get_khoitao(self):
        self.get_loaidoituong_data()
        self.get_loai_congno_tuongung_data()
        self.get_doituong_data()
        self.get_congno_data()
        return True
    
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        return ''
    
    def get_chinhanh(self):
        wizard_data = self.localcontext['data']['form']
        chinhanh_id = wizard_data['chinhanh_id']
        if not chinhanh_id:
            return {'name':'','code':''}
        account = self.pool.get('account.account').browse(self.cr, self.uid, chinhanh_id[0])
        return {'name':account.name,'code':account.code}
    
    def get_from_thang(self):
        wizard_data = self.localcontext['data']['form']
        period_id = wizard_data['period_from_id']
        return period_id and period_id[1] or ''
    
    def get_to_thang(self):
        wizard_data = self.localcontext['data']['form']
        period_id = wizard_data['period_to_id']
        return period_id and period_id[1] or ''
    
    def convert_amount(self, amount):
        a = format(int(amount),',')
        return a
    
    def get_title(self):
        wizard_data = self.localcontext['data']['form']
        mlg_type = wizard_data['mlg_type']
        tt = ''
        if mlg_type=='no_doanh_thu':
            tt='Nợ DT-BH-AL'
        if mlg_type=='chi_ho_dien_thoai':
            tt='CHI HỘ ĐIỆN THOẠI'
        if mlg_type=='phai_thu_bao_hiem':
            tt='BẢO HIỂM'
        if mlg_type=='phat_vi_pham':
            tt='PHẠT VI PHẠM'
        if mlg_type=='thu_no_xuong':
            tt='NỢ XƯỞNG'
        if mlg_type=='thu_phi_thuong_hieu':
            tt='PHÍ THƯƠNG HIỆU'
        if mlg_type=='tra_gop_xe':
            tt='TRẢ GÓP XE'
        if mlg_type=='hoan_tam_ung':
            tt='TẠM ỨNG'
        if mlg_type=='phai_tra_ky_quy':
            tt='TRẢ KÝ QUỸ'
        if mlg_type=='chi_ho':
            tt='CHI HỘ'
        return tt

    def get_doituong(self, ldt, lcntu):
        if self.partner_dict.get(ldt, False):
            if self.partner_dict[ldt].get(lcntu['loai'], False):
                if lcntu['loai']=='loai_conlai':
                    return self.partner_dict[ldt][lcntu['loai']]
                else:
                    if self.partner_dict[ldt][lcntu['loai']].get(lcntu['id'], False):
                        return self.partner_dict[ldt][lcntu['loai']][lcntu['id']]
        return []
    
    def get_doituong_data(self):
        wizard_data = self.localcontext['data']['form']
        partner_ids = wizard_data['partner_ids']
        
        ldt = self.loaidoituong
        ldt = str(ldt).replace('[', '(')
        ldt = str(ldt).replace(']', ')')
        
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        mlg_type = wizard_data['mlg_type']
        sql = '''
            select partner_id, loai_doituong, loai_nodoanhthu_id, loai_baohiem_id, ma_xuong_id, loai_vipham_id, loai_tamung_id
                from account_invoice where date_invoice between '%s' and '%s' and chinhanh_id=%s
                and state in ('open','paid') and mlg_type='%s' and loai_doituong in %s 
        '''%(period_from.date_start,period_to.date_stop,chinhanh_id[0],mlg_type,ldt)
        doi_xe_ids = wizard_data['doi_xe_ids']
        if doi_xe_ids:
            doi_xe_ids = str(doi_xe_ids).replace('[', '(')
            doi_xe_ids = str(doi_xe_ids).replace(']', ')')
            sql+='''
                and account_id in %s 
            '''%(doi_xe_ids)
        bai_giaoca_ids = wizard_data['bai_giaoca_ids']
        if bai_giaoca_ids:
            bai_giaoca_ids = str(bai_giaoca_ids).replace('[', '(')
            bai_giaoca_ids = str(bai_giaoca_ids).replace(']', ')')
            sql+='''
                and bai_giaoca_id in %s 
            '''%(bai_giaoca_ids)
        if partner_ids:
            partner_ids = str(partner_ids).replace('[', '(')
            partner_ids = str(partner_ids).replace(']', ')')
            sql+='''
                and partner_id in %s 
            '''%(partner_ids)
        sql += ''' group by partner_id,loai_doituong, loai_nodoanhthu_id, loai_baohiem_id, ma_xuong_id, loai_vipham_id, loai_tamung_id '''
        self.cr.execute(sql)
        for dt in self.cr.dictfetchall():
            if self.partner_dict.get(dt['loai_doituong'], False):
                if mlg_type=='no_doanh_thu':
                    if self.partner_dict[dt['loai_doituong']].get('loai_nodoanhthu', False):
                        if self.partner_dict[dt['loai_doituong']]['loai_nodoanhthu'].get(dt['loai_nodoanhthu_id'], False):
                            if dt['partner_id'] not in self.partner_dict[dt['loai_doituong']]['loai_nodoanhthu'][dt['loai_nodoanhthu_id']]:
                                self.partner_dict[dt['loai_doituong']]['loai_nodoanhthu'][dt['loai_nodoanhthu_id']].append(dt['partner_id'])
                        else:
                            self.partner_dict[dt['loai_doituong']]['loai_nodoanhthu'][dt['loai_nodoanhthu_id']] = [dt['partner_id']]
                    else:
                        self.partner_dict[dt['loai_doituong']]['loai_nodoanhthu'] = {dt['loai_nodoanhthu_id']: [dt['partner_id']]}
                if mlg_type=='phai_thu_bao_hiem':
                    if self.partner_dict[dt['loai_doituong']].get('loai_baohiem', False):
                        if self.partner_dict[dt['loai_doituong']]['loai_baohiem'].get(dt['loai_baohiem_id'], False):
                            if dt['partner_id'] not in self.partner_dict[dt['loai_doituong']]['loai_baohiem'][dt['loai_baohiem_id']]:
                                self.partner_dict[dt['loai_doituong']]['loai_baohiem'][dt['loai_baohiem_id']].append(dt['partner_id'])
                        else:
                            self.partner_dict[dt['loai_doituong']]['loai_baohiem'][dt['loai_baohiem_id']] = [dt['partner_id']]
                    else:
                        self.partner_dict[dt['loai_doituong']]['loai_baohiem'] = {dt['loai_baohiem_id']: [dt['partner_id']]}
                if mlg_type=='phat_vi_pham':
                    if self.partner_dict[dt['loai_doituong']].get('loai_vipham', False):
                        if self.partner_dict[dt['loai_doituong']]['loai_vipham'].get(dt['loai_vipham_id'], False):
                            if dt['partner_id'] not in self.partner_dict[dt['loai_doituong']]['loai_vipham'][dt['loai_vipham_id']]:
                                self.partner_dict[dt['loai_doituong']]['loai_vipham'][dt['loai_vipham_id']].append(dt['partner_id'])
                        else:
                            self.partner_dict[dt['loai_doituong']]['loai_vipham'][dt['loai_vipham_id']] = [dt['partner_id']]
                    else:
                        self.partner_dict[dt['loai_doituong']]['loai_vipham'] = {dt['loai_vipham_id']: [dt['partner_id']]}
                if mlg_type=='thu_no_xuong':
                    if self.partner_dict[dt['loai_doituong']].get('maxuong', False):
                        if self.partner_dict[dt['loai_doituong']]['maxuong'].get(dt['ma_xuong_id'], False):
                            if dt['partner_id'] not in self.partner_dict[dt['loai_doituong']]['maxuong'][dt['ma_xuong_id']]:
                                self.partner_dict[dt['loai_doituong']]['maxuong'][dt['ma_xuong_id']].append(dt['partner_id'])
                        else:
                            self.partner_dict[dt['loai_doituong']]['maxuong'][dt['ma_xuong_id']] = [dt['partner_id']]
                    else:
                        self.partner_dict[dt['loai_doituong']]['maxuong'] = {dt['ma_xuong_id']: [dt['partner_id']]}
                if mlg_type=='hoan_tam_ung':
                    if self.partner_dict[dt['loai_doituong']].get('loai_tamung', False):
                        if self.partner_dict[dt['loai_doituong']]['loai_tamung'].get(dt['loai_tamung_id'], False):
                            if dt['partner_id'] not in self.partner_dict[dt['loai_doituong']]['loai_tamung'][dt['loai_tamung_id']]:
                                self.partner_dict[dt['loai_doituong']]['loai_tamung'][dt['loai_tamung_id']].append(dt['partner_id'])
                        else:
                            self.partner_dict[dt['loai_doituong']]['loai_tamung'][dt['loai_tamung_id']] = [dt['partner_id']]
                    else:
                        self.partner_dict[dt['loai_doituong']]['loai_tamung'] = {dt['loai_tamung_id']: [dt['partner_id']]}
                if mlg_type not in ['no_doanh_thu','phai_thu_bao_hiem','phat_vi_pham','thu_no_xuong','hoan_tam_ung']:
                    if self.partner_dict[dt['loai_doituong']].get('loai_conlai', False):
                        if dt['partner_id'] not in self.partner_dict[dt['loai_doituong']]['loai_conlai']:
                            self.partner_dict[dt['loai_doituong']]['loai_conlai'].append(dt['partner_id'])
                    else:
                        self.partner_dict[dt['loai_doituong']]['loai_conlai'] = [dt['partner_id']]
            else:
                if mlg_type=='no_doanh_thu' and dt['loai_nodoanhthu_id']:
                    self.partner_dict[dt['loai_doituong']] = {'loai_nodoanhthu': {dt['loai_nodoanhthu_id']: [dt['partner_id']]}}
                if mlg_type=='phai_thu_bao_hiem' and dt['loai_baohiem_id']:
                    self.partner_dict[dt['loai_doituong']] = {'loai_baohiem': {dt['loai_baohiem_id']: [dt['partner_id']]}}
                if mlg_type=='phat_vi_pham' and dt['loai_vipham_id']:
                    self.partner_dict[dt['loai_doituong']] = {'loai_vipham': {dt['loai_vipham_id']: [dt['partner_id']]}}
                if mlg_type=='thu_no_xuong' and dt['ma_xuong_id']:
                    self.partner_dict[dt['loai_doituong']] = {'maxuong': {dt['ma_xuong_id']: [dt['partner_id']]}}
                if mlg_type=='hoan_tam_ung' and dt['loai_tamung_id']:
                    self.partner_dict[dt['loai_doituong']] = {'loai_tamung': {dt['loai_tamung_id']: [dt['partner_id']]}}
                if mlg_type not in ['no_doanh_thu','phai_thu_bao_hiem','phat_vi_pham','thu_no_xuong','hoan_tam_ung']:
                    self.partner_dict[dt['loai_doituong']] = {'loai_conlai': [dt['partner_id']]}
                
        sql = '''
            select cndk.partner_id as partner_id, rp.taixe as taixe, rp.nhanvienvanphong as nhanvienvanphong, rp.nhadautu as nhadautu, ctcndkl.loai_id as loai_id
            
                from congno_dauky cndk
                left join congno_dauky_line cndkl on cndk.id = cndkl.congno_dauky_id
                left join chitiet_congno_dauky_line ctcndkl on ctcndkl.congno_dauky_line_id = cndkl.id
                left join res_partner rp on rp.id = cndk.partner_id
                
                where cndk.period_id=%s and cndkl.chinhanh_id=%s and cndkl.mlg_type='%s'
        '''%(period_from_id[0],chinhanh_id[0],mlg_type)
        self.cr.execute(sql)
        for ct in self.cr.dictfetchall():
            if ct['taixe'] and 'taixe' in self.loaidoituong:
                if self.partner_dict.get('taixe', False):
                    if mlg_type=='no_doanh_thu' and ct['loai_id']:
                        if self.partner_dict['taixe'].get('loai_nodoanhthu', False):
                            if self.partner_dict['taixe']['loai_nodoanhthu'].get(ct['loai_id'], False):
                                if ct['partner_id'] not in self.partner_dict['taixe']['loai_nodoanhthu'][ct['loai_id']]:
                                    self.partner_dict['taixe']['loai_nodoanhthu'][ct['loai_id']].append(ct['partner_id'])
                            else:
                                self.partner_dict['taixe']['loai_nodoanhthu'][ct['loai_id']] = [ct['partner_id']]
                        else:
                            self.partner_dict['taixe']['loai_nodoanhthu'] = {ct['loai_id']: [ct['partner_id']]}
                    if mlg_type=='phai_thu_bao_hiem' and ct['loai_id']:
                        if self.partner_dict['taixe'].get('loai_baohiem', False):
                            if self.partner_dict['taixe']['loai_baohiem'].get(ct['loai_id'], False):
                                if ct['partner_id'] not in self.partner_dict['taixe']['loai_baohiem'][ct['loai_id']]:
                                    self.partner_dict['taixe']['loai_baohiem'][ct['loai_id']].append(ct['partner_id'])
                            else:
                                self.partner_dict['taixe']['loai_baohiem'][ct['loai_id']] = [ct['partner_id']]
                        else:
                            self.partner_dict['taixe']['loai_baohiem'] = {ct['loai_id']: [ct['partner_id']]}
                    if mlg_type=='phat_vi_pham' and ct['loai_id']:
                        if self.partner_dict['taixe'].get('loai_vipham', False):
                            if self.partner_dict['taixe']['loai_vipham'].get(ct['loai_id'], False):
                                if ct['partner_id'] not in self.partner_dict['taixe']['loai_vipham'][ct['loai_id']]:
                                    self.partner_dict['taixe']['loai_vipham'][ct['loai_id']].append(ct['partner_id'])
                            else:
                                self.partner_dict['taixe']['loai_vipham'][ct['loai_id']] = [ct['partner_id']]
                        else:
                            self.partner_dict['taixe']['loai_vipham'] = {ct['loai_id']: [ct['partner_id']]}
                    if mlg_type=='thu_no_xuong' and ct['loai_id']:
                        if self.partner_dict['taixe'].get('maxuong', False):
                            if self.partner_dict['taixe']['maxuong'].get(ct['loai_id'], False):
                                if ct['partner_id'] not in self.partner_dict['taixe']['maxuong'][ct['loai_id']]:
                                    self.partner_dict['taixe']['maxuong'][ct['loai_id']].append(ct['partner_id'])
                            else:
                                self.partner_dict['taixe']['maxuong'][ct['loai_id']] = [ct['partner_id']]
                        else:
                            self.partner_dict['taixe']['maxuong'] = {ct['loai_id']: [ct['partner_id']]}
                    if mlg_type=='hoan_tam_ung' and ct['loai_id']:
                        if self.partner_dict['taixe'].get('loai_tamung', False):
                            if self.partner_dict['taixe']['loai_tamung'].get(ct['loai_id'], False):
                                if ct['partner_id'] not in self.partner_dict['taixe']['loai_tamung'][ct['loai_id']]:
                                    self.partner_dict['taixe']['loai_tamung'][ct['loai_id']].append(ct['partner_id'])
                            else:
                                self.partner_dict['taixe']['loai_tamung'][ct['loai_id']] = [ct['partner_id']]
                        else:
                            self.partner_dict['taixe']['loai_tamung'] = {ct['loai_id']: [ct['partner_id']]}
                    if mlg_type not in ['no_doanh_thu','phai_thu_bao_hiem','phat_vi_pham','thu_no_xuong','hoan_tam_ung']:
                        if self.partner_dict['taixe'].get('loai_conlai', False):
                            if ct['partner_id'] not in self.partner_dict['taixe']['loai_conlai']:
                                self.partner_dict['taixe']['loai_conlai'].append(ct['partner_id'])
                        else:
                            self.partner_dict['taixe']['loai_conlai'] = [ct['partner_id']]
                else:
                    if mlg_type=='no_doanh_thu' and ct['loai_id']:
                        self.partner_dict['taixe'] = {'loai_nodoanhthu': {ct['loai_id']: [ct['partner_id']]}}
                    if mlg_type=='phai_thu_bao_hiem' and ct['loai_id']:
                        self.partner_dict['taixe'] = {'loai_baohiem': {ct['loai_id']: [ct['partner_id']]}}
                    if mlg_type=='phat_vi_pham' and ct['loai_id']:
                        self.partner_dict['taixe'] = {'loai_vipham': {ct['loai_id']: [ct['partner_id']]}}
                    if mlg_type=='thu_no_xuong' and ct['loai_id']:
                        self.partner_dict['taixe'] = {'maxuong': {ct['loai_id']: [ct['partner_id']]}}
                    if mlg_type=='hoan_tam_ung' and ct['loai_id']:
                        self.partner_dict['taixe'] = {'loai_tamung': {ct['loai_id']: [ct['partner_id']]}}
                    if mlg_type not in ['no_doanh_thu','phai_thu_bao_hiem','phat_vi_pham','thu_no_xuong','hoan_tam_ung']:
                        self.partner_dict['taixe'] = {'loai_conlai': [ct['partner_id']]}
            
            if ct['nhadautu'] and 'nhadautu' in self.loaidoituong:
                if self.partner_dict.get('nhadautu', False):
                    if mlg_type=='no_doanh_thu' and ct['loai_id']:
                        if self.partner_dict['nhadautu'].get('loai_nodoanhthu', False):
                            if self.partner_dict['nhadautu']['loai_nodoanhthu'].get(ct['loai_id'], False):
                                if ct['partner_id'] not in self.partner_dict['nhadautu']['loai_nodoanhthu'][ct['loai_id']]:
                                    self.partner_dict['nhadautu']['loai_nodoanhthu'][ct['loai_id']].append(ct['partner_id'])
                            else:
                                self.partner_dict['nhadautu']['loai_nodoanhthu'][ct['loai_id']] = [ct['partner_id']]
                        else:
                            self.partner_dict['nhadautu']['loai_nodoanhthu'] = {ct['loai_id']: [ct['partner_id']]}
                    if mlg_type=='phai_thu_bao_hiem' and ct['loai_id']:
                        if self.partner_dict['nhadautu'].get('loai_baohiem', False):
                            if self.partner_dict['nhadautu']['loai_baohiem'].get(ct['loai_id'], False):
                                if ct['partner_id'] not in self.partner_dict['nhadautu']['loai_baohiem'][ct['loai_id']]:
                                    self.partner_dict['nhadautu']['loai_baohiem'][ct['loai_id']].append(ct['partner_id'])
                            else:
                                self.partner_dict['nhadautu']['loai_baohiem'][ct['loai_id']] = [ct['partner_id']]
                        else:
                            self.partner_dict['nhadautu']['loai_baohiem'] = {ct['loai_id']: [ct['partner_id']]}
                    if mlg_type=='phat_vi_pham' and ct['loai_id']:
                        if self.partner_dict['nhadautu'].get('loai_vipham', False):
                            if self.partner_dict['nhadautu']['loai_vipham'].get(ct['loai_id'], False):
                                if ct['partner_id'] not in self.partner_dict['nhadautu']['loai_vipham'][ct['loai_id']]:
                                    self.partner_dict['nhadautu']['loai_vipham'][ct['loai_id']].append(ct['partner_id'])
                            else:
                                self.partner_dict['nhadautu']['loai_vipham'][ct['loai_id']] = [ct['partner_id']]
                        else:
                            self.partner_dict['nhadautu']['loai_vipham'] = {ct['loai_id']: [ct['partner_id']]}
                    if mlg_type=='thu_no_xuong' and ct['loai_id']:
                        if self.partner_dict['nhadautu'].get('maxuong', False):
                            if self.partner_dict['nhadautu']['maxuong'].get(ct['loai_id'], False):
                                if ct['partner_id'] not in self.partner_dict['nhadautu']['maxuong'][ct['loai_id']]:
                                    self.partner_dict['nhadautu']['maxuong'][ct['loai_id']].append(ct['partner_id'])
                            else:
                                self.partner_dict['nhadautu']['maxuong'][ct['loai_id']] = [ct['partner_id']]
                        else:
                            self.partner_dict['nhadautu']['maxuong'] = {ct['loai_id']: [ct['partner_id']]}
                    if mlg_type=='hoan_tam_ung' and ct['loai_id']:
                        if self.partner_dict['nhadautu'].get('loai_tamung', False):
                            if self.partner_dict['nhadautu']['loai_tamung'].get(ct['loai_id'], False):
                                if ct['partner_id'] not in self.partner_dict['nhadautu']['loai_tamung'][ct['loai_id']]:
                                    self.partner_dict['nhadautu']['loai_tamung'][ct['loai_id']].append(ct['partner_id'])
                            else:
                                self.partner_dict['nhadautu']['loai_tamung'][ct['loai_id']] = [ct['partner_id']]
                        else:
                            self.partner_dict['nhadautu']['loai_tamung'] = {ct['loai_id']: [ct['partner_id']]}
                    if mlg_type not in ['no_doanh_thu','phai_thu_bao_hiem','phat_vi_pham','thu_no_xuong','hoan_tam_ung']:
                        if self.partner_dict['nhadautu'].get('loai_conlai', False):
                            if ct['partner_id'] not in self.partner_dict['nhadautu']['loai_conlai']:
                                self.partner_dict['nhadautu']['loai_conlai'].append(ct['partner_id'])
                        else:
                            self.partner_dict['nhadautu']['loai_conlai'] = [ct['partner_id']]
                else:
                    if mlg_type=='no_doanh_thu' and ct['loai_id']:
                        self.partner_dict['nhadautu'] = {'loai_nodoanhthu': {ct['loai_id']: [ct['partner_id']]}}
                    if mlg_type=='phai_thu_bao_hiem' and ct['loai_id']:
                        self.partner_dict['nhadautu'] = {'loai_baohiem': {ct['loai_id']: [ct['partner_id']]}}
                    if mlg_type=='phat_vi_pham' and ct['loai_id']:
                        self.partner_dict['nhadautu'] = {'loai_vipham': {ct['loai_id']: [ct['partner_id']]}}
                    if mlg_type=='thu_no_xuong' and ct['loai_id']:
                        self.partner_dict['nhadautu'] = {'maxuong': {ct['loai_id']: [ct['partner_id']]}}
                    if mlg_type=='hoan_tam_ung' and ct['loai_id']:
                        self.partner_dict['nhadautu'] = {'loai_tamung': {ct['loai_id']: [ct['partner_id']]}}
                    if mlg_type not in ['no_doanh_thu','phai_thu_bao_hiem','phat_vi_pham','thu_no_xuong','hoan_tam_ung']:
                        self.partner_dict['nhadautu'] = {'loai_conlai': [ct['partner_id']]} 
                        
            if ct['nhanvienvanphong'] and 'nhanvienvanphong' in self.loaidoituong:
                if self.partner_dict.get('nhanvienvanphong', False):
                    if mlg_type=='no_doanh_thu' and ct['loai_id']:
                        if self.partner_dict['nhanvienvanphong'].get('loai_nodoanhthu', False):
                            if self.partner_dict['nhanvienvanphong']['loai_nodoanhthu'].get(ct['loai_id'], False):
                                if ct['partner_id'] not in self.partner_dict['nhanvienvanphong']['loai_nodoanhthu'][ct['loai_id']]:
                                    self.partner_dict['nhanvienvanphong']['loai_nodoanhthu'][ct['loai_id']].append(ct['partner_id'])
                            else:
                                self.partner_dict['nhanvienvanphong']['loai_nodoanhthu'][ct['loai_id']] = [ct['partner_id']]
                        else:
                            self.partner_dict['nhanvienvanphong']['loai_nodoanhthu'] = {ct['loai_id']: [ct['partner_id']]}
                    if mlg_type=='phai_thu_bao_hiem' and ct['loai_id']:
                        if self.partner_dict['nhanvienvanphong'].get('loai_baohiem', False):
                            if self.partner_dict['nhanvienvanphong']['loai_baohiem'].get(ct['loai_id'], False):
                                if ct['partner_id'] not in self.partner_dict['nhanvienvanphong']['loai_baohiem'][ct['loai_id']]:
                                    self.partner_dict['nhanvienvanphong']['loai_baohiem'][ct['loai_id']].append(ct['partner_id'])
                            else:
                                self.partner_dict['nhanvienvanphong']['loai_baohiem'][ct['loai_id']] = [ct['partner_id']]
                        else:
                            self.partner_dict['nhanvienvanphong']['loai_baohiem'] = {ct['loai_id']: [ct['partner_id']]}
                    if mlg_type=='phat_vi_pham' and ct['loai_id']:
                        if self.partner_dict['nhanvienvanphong'].get('loai_vipham', False):
                            if self.partner_dict['nhanvienvanphong']['loai_vipham'].get(ct['loai_id'], False):
                                if ct['partner_id'] not in self.partner_dict['nhanvienvanphong']['loai_vipham'][ct['loai_id']]:
                                    self.partner_dict['nhanvienvanphong']['loai_vipham'][ct['loai_id']].append(ct['partner_id'])
                            else:
                                self.partner_dict['nhanvienvanphong']['loai_vipham'][ct['loai_id']] = [ct['partner_id']]
                        else:
                            self.partner_dict['nhanvienvanphong']['loai_vipham'] = {ct['loai_id']: [ct['partner_id']]}
                    if mlg_type=='thu_no_xuong' and ct['loai_id']:
                        if self.partner_dict['nhanvienvanphong'].get('maxuong', False):
                            if self.partner_dict['nhanvienvanphong']['maxuong'].get(ct['loai_id'], False):
                                if ct['partner_id'] not in self.partner_dict['nhanvienvanphong']['maxuong'][ct['loai_id']]:
                                    self.partner_dict['nhanvienvanphong']['maxuong'][ct['loai_id']].append(ct['partner_id'])
                            else:
                                self.partner_dict['nhanvienvanphong']['maxuong'][ct['loai_id']] = [ct['partner_id']]
                        else:
                            self.partner_dict['nhanvienvanphong']['maxuong'] = {ct['loai_id']: [ct['partner_id']]}
                    if mlg_type=='hoan_tam_ung' and ct['loai_id']:
                        if self.partner_dict['nhanvienvanphong'].get('loai_tamung', False):
                            if self.partner_dict['nhanvienvanphong']['loai_tamung'].get(ct['loai_id'], False):
                                if ct['partner_id'] not in self.partner_dict['nhanvienvanphong']['loai_tamung'][ct['loai_id']]:
                                    self.partner_dict['nhanvienvanphong']['loai_tamung'][ct['loai_id']].append(ct['partner_id'])
                            else:
                                self.partner_dict['nhanvienvanphong']['loai_tamung'][ct['loai_id']] = [ct['partner_id']]
                        else:
                            self.partner_dict['nhanvienvanphong']['loai_tamung'] = {ct['loai_id']: [ct['partner_id']]}
                    if mlg_type not in ['no_doanh_thu','phai_thu_bao_hiem','phat_vi_pham','thu_no_xuong','hoan_tam_ung']:
                        if self.partner_dict['nhanvienvanphong'].get('loai_conlai', False):
                            if ct['partner_id'] not in self.partner_dict['nhanvienvanphong']['loai_conlai']:
                                self.partner_dict['nhanvienvanphong']['loai_conlai'].append(ct['partner_id'])
                        else:
                            self.partner_dict['nhanvienvanphong']['loai_conlai'] = [ct['partner_id']]
                else:
                    if mlg_type=='no_doanh_thu' and ct['loai_id']:
                        self.partner_dict['nhanvienvanphong'] = {'loai_nodoanhthu': {ct['loai_id']: [ct['partner_id']]}}
                    if mlg_type=='phai_thu_bao_hiem' and ct['loai_id']:
                        self.partner_dict['nhanvienvanphong'] = {'loai_baohiem': {ct['loai_id']: [ct['partner_id']]}}
                    if mlg_type=='phat_vi_pham' and ct['loai_id']:
                        self.partner_dict['nhanvienvanphong'] = {'loai_vipham': {ct['loai_id']: [ct['partner_id']]}}
                    if mlg_type=='thu_no_xuong' and ct['loai_id']:
                        self.partner_dict['nhanvienvanphong'] = {'maxuong': {ct['loai_id']: [ct['partner_id']]}}
                    if mlg_type=='hoan_tam_ung' and ct['loai_id']:
                        self.partner_dict['nhanvienvanphong'] = {'loai_tamung': {ct['loai_id']: [ct['partner_id']]}}
                    if mlg_type not in ['no_doanh_thu','phai_thu_bao_hiem','phat_vi_pham','thu_no_xuong','hoan_tam_ung']:
                        self.partner_dict['nhanvienvanphong'] = {'loai_conlai': [ct['partner_id']]} 
        return True
    
    def get_madoituong(self, partner_id):
        mdt = ''
        if partner_id:
            return self.pool.get('res.partner').browse(self.cr, self.uid, partner_id).ma_doi_tuong
        return mdt
    
    def get_tendoituong(self, partner_id):
        tdt = ''
        if partner_id:
            return self.pool.get('res.partner').browse(self.cr, self.uid, partner_id).name
        return tdt
    
    def get_loaidoituong(self):
        return self.loaidoituong
        
    def get_loaidoituong_data(self):
        wizard_data = self.localcontext['data']['form']
        loai_doituong = wizard_data['loai_doituong']
        if loai_doituong:
            self.loaidoituong = [loai_doituong]
        else:
            self.loaidoituong = ['taixe','nhadautu','nhanvienvanphong']
        return True
        
    def get_name_loaidoituong(self, ldt):
        if ldt=='taixe':
            return 'Lái xe'
        if ldt=='nhadautu':
            return 'Nhà đầu tư'
        if ldt=='nhanvienvanphong':
            return 'Nhân viên văn phòng'
    
    def get_title_doituong(self, partner_id):
        if partner_id:
            partner = self.pool.get('res.partner').browse(self.cr, self.uid, partner_id)
            return (partner.ma_doi_tuong or '')+'_'+(partner.name or '')
        return ''
    
    def get_nodauky(self, partner_id,lcntu):
        wizard_data = self.localcontext['data']['form']
        if partner_id:
            period_id = wizard_data['period_from_id']
            chinhanh_id = wizard_data['chinhanh_id']
            mlg_type = wizard_data['mlg_type']
            sql = '''
                select case when sum(so_tien_no)!=0 then sum(so_tien_no) else 0 end nodauky
                    from congno_dauky_line where mlg_type='%s' and chinhanh_id=%s
                        and congno_dauky_id in (select id from congno_dauky where partner_id=%s and period_id=%s)
            '''%(mlg_type,chinhanh_id[0],partner_id,period_id[0])
            if lcntu['loai']!='loai_conlai' and lcntu['id']:
                sql = '''
                    select case when sum(so_tien_no)!=0 then sum(so_tien_no) else 0 end nodauky
                        from chitiet_congno_dauky_line where congno_dauky_line_id in (select id from congno_dauky_line where mlg_type='%s' and chinhanh_id=%s
                            and congno_dauky_id in (select id from congno_dauky where partner_id=%s and period_id=%s)) and loai_id=%s
                '''%(mlg_type,chinhanh_id[0],partner_id,period_id[0],lcntu['id'])
            self.cr.execute(sql)
            nodauky = self.cr.fetchone()[0]
            self.tongnodauky += nodauky
            return nodauky
        return 0
    
    def get_tongcongno(self):
        tongcongno = self.tongcongno
        self.tongcongno = 0
        self.tongcong_congno += tongcongno
        return tongcongno
    
    def get_tongnodauky(self):
        tongnodauky = self.tongnodauky
        self.tongnodauky = 0
        self.tongcong_nodauky += tongnodauky
        return tongnodauky
    
    def get_tongno(self):
        tongno = self.tongno
        self.tongno = 0
        self.tongcong_no += tongno
        return tongno
    
    def get_tongco(self):
        tongco = self.tongco
        self.tongco = 0
        self.tongcong_co += tongco
        return tongco
    
    def get_tongcong_congno(self):
        tongcong_congno = self.tongcong_congno
        self.tongcong_congno = 0
        return tongcong_congno
    
    def get_tongcong_nodauky(self):
        tongcong_nodauky = self.tongcong_nodauky
        self.tongcong_nodauky = 0
        return tongcong_nodauky
    
    def get_tongcong_no(self):
        tongcong_no = self.tongcong_no
        self.tongcong_no = 0
        return tongcong_no
    
    def get_tongcong_co(self):
        tongcong_co = self.tongcong_co
        self.tongcong_co = 0
        return tongcong_co
    
    def get_loai_congno_tuongung(self, ldt):
        return self.loai_congno_tuongung
    
    def get_loai_congno_tuongung_data(self):
        wizard_data = self.localcontext['data']['form']
        mlg_type = wizard_data['mlg_type']
        chinhanh_id = wizard_data['chinhanh_id']
        lcntu_ids = []
        if mlg_type=='no_doanh_thu':
            loai = 'loai_nodoanhthu'
            loai_nodoanhthu_id = wizard_data['loai_nodoanhthu_id']
            if loai_nodoanhthu_id:
                lcntu_ids.append({
                    'id':loai_nodoanhthu_id[0],
                    'name':loai_nodoanhthu_id[1],
                    'loai':loai
                })
            else:
                sql = '''
                    select id,name from loai_no_doanh_thu
                '''
                self.cr.execute(sql)
                for lndt in self.cr.fetchall():
                    lcntu_ids.append({
                        'id':lndt[0],
                        'name':lndt[1],
                        'loai':loai
                    })
        elif mlg_type=='phai_thu_bao_hiem':
            loai = 'loai_baohiem'
            loai_baohiem_id = wizard_data['loai_baohiem_id']
            if loai_baohiem_id:
                lcntu_ids.append({
                    'id':loai_baohiem_id[0],
                    'name':loai_baohiem_id[1],
                    'loai':loai
                })
            else:
                sql = '''
                    select id,name from loai_bao_hiem
                '''
                self.cr.execute(sql)
                for lndt in self.cr.fetchall():
                    lcntu_ids.append({
                        'id':lndt[0],
                        'name':lndt[1],
                        'loai':loai
                    })
        elif mlg_type=='phat_vi_pham':
            loai = 'loai_vipham'
            loai_vipham_id = wizard_data['loai_vipham_id']
            if loai_vipham_id:
                lcntu_ids.append({
                    'id':loai_vipham_id[0],
                    'name':loai_vipham_id[1],
                    'loai':loai
                })
            else:
                sql = '''
                    select id,name from loai_vi_pham
                '''
                self.cr.execute(sql)
                for lndt in self.cr.fetchall():
                    lcntu_ids.append({
                        'id':lndt[0],
                        'name':lndt[1],
                        'loai':loai
                    })
        elif mlg_type=='thu_no_xuong':
            loai = 'maxuong'
            ma_xuong_id = wizard_data['ma_xuong_id']
            if ma_xuong_id:
                lcntu_ids.append({
                    'id':ma_xuong_id[0],
                    'name':ma_xuong_id[1],
                    'loai':loai
                })
            else:
                sql = '''
                    select id,name from ma_xuong where chinhanh_id=%s
                '''%(chinhanh_id[0])
                self.cr.execute(sql)
                for lndt in self.cr.fetchall():
                    lcntu_ids.append({
                        'id':lndt[0],
                        'name':lndt[1],
                        'loai':loai
                    })
        elif mlg_type=='hoan_tam_ung':
            loai = 'loai_tamung'
            loai_tamung_id = wizard_data['loai_tamung_id']
            if loai_tamung_id:
                lcntu_ids.append({
                    'id':loai_tamung_id[0],
                    'name':loai_tamung_id[1],
                    'loai':loai
                })
            else:
                sql = '''
                    select id,name from loai_tam_ung
                '''
                self.cr.execute(sql)
                for lndt in self.cr.fetchall():
                    lcntu_ids.append({
                        'id':lndt[0],
                        'name':lndt[1],
                        'loai':loai
                    })
        else:
            lcntu_ids.append({
                'id':False,
                'name':'',
                'loai': 'loai_conlai'
            })
        self.loai_congno_tuongung = lcntu_ids
        return True
        
    def get_title_lcntu(self, lcntu):
        tt = ''
        if lcntu['loai']=='loai_nodoanhthu':
            tt = 'Loại nợ DT-BH-AL: '+lcntu['name']
        if lcntu['loai']=='loai_baohiem':
            tt = 'Loại bảo hiểm: '+lcntu['name']
        if lcntu['loai']=='loai_vipham':
            tt = 'Loại vi phạm: '+lcntu['name']
        if lcntu['loai']=='maxuong':
            tt = 'Mã xưởng: '+lcntu['name']
        if lcntu['loai']=='loai_tamung':
            tt = 'Loại tạm ứng: '+lcntu['name']
        return tt
    
    def get_nocuoiky(self, partner_id,lcntu):
        wizard_data = self.localcontext['data']['form']
        if partner_id:
            period_id = wizard_data['period_from_id']
            chinhanh_id = wizard_data['chinhanh_id']
            mlg_type = wizard_data['mlg_type']
            sql = '''
                select case when sum(so_tien_no)!=0 then sum(so_tien_no) else 0 end nodauky
                    from congno_dauky_line where mlg_type='%s' and chinhanh_id=%s
                        and congno_dauky_id in (select id from congno_dauky where partner_id=%s and period_id=%s)
            '''%(mlg_type,chinhanh_id[0],partner_id,period_id[0])
            if lcntu['loai']!='loai_conlai' and lcntu['id']:
                sql = '''
                    select case when sum(so_tien_no)!=0 then sum(so_tien_no) else 0 end nodauky
                        from chitiet_congno_dauky_line where congno_dauky_line_id in (select id from congno_dauky_line where mlg_type='%s' and chinhanh_id=%s
                            and congno_dauky_id in (select id from congno_dauky where partner_id=%s and period_id=%s)) and loai_id=%s
                '''%(mlg_type,chinhanh_id[0],partner_id,period_id[0],lcntu['id'])
            self.cr.execute(sql)
            nodauky = self.cr.fetchone()[0]
            
            period_from_id = wizard_data['period_from_id']
            period_to_id = wizard_data['period_to_id']
            period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
            period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
            chinhanh_id = wizard_data['chinhanh_id']
            mlg_type = wizard_data['mlg_type']
            sql = '''
                select case when sum(COALESCE(ai.so_tien,0)+COALESCE(ai.sotien_lai,0))!=0 then sum(COALESCE(ai.so_tien,0)+COALESCE(ai.sotien_lai,0)) else 0 end sotienno
                
                    from account_invoice ai
                    left join res_partner rp on rp.id = ai.partner_id
                    
                    where ai.partner_id=%s and ai.state in ('open','paid') and ai.date_invoice between '%s' and '%s' and ai.chinhanh_id=%s
                        and ai.mlg_type='%s' 
            '''%(partner_id,period_from.date_start,period_to.date_stop,chinhanh_id[0],mlg_type)
            if lcntu['loai']=='loai_nodoanhthu' and lcntu['id']:
                sql+='''
                    and ai.loai_nodoanhthu_id = %s 
                '''%(lcntu['id'])
            if lcntu['loai']=='loai_baohiem' and lcntu['id']:
                sql+='''
                    and ai.loai_baohiem_id = %s 
                '''%(lcntu['id'])
            if lcntu['loai']=='loai_vipham' and lcntu['id']:
                sql+='''
                    and ai.loai_vipham_id = %s 
                '''%(lcntu['id'])
            if lcntu['loai']=='maxuong' and lcntu['id']:
                sql+='''
                    and ai.ma_xuong_id = %s 
                '''%(lcntu['id'])
            if lcntu['loai']=='loai_tamung' and lcntu['id']:
                sql+='''
                    and ai.loai_tamung_id = %s 
                '''%(lcntu['id'])
            self.cr.execute(sql)
            no = self.cr.fetchone()[0]
            
            sql = '''
                select case when sum(credit)!=0 then sum(credit) else 0 end sotien
                    from account_move_line
                    where move_id in (select move_id from account_voucher
                        where reference in (select name from account_invoice
                            where mlg_type='%s' and state in ('open','paid') and chinhanh_id=%s and partner_id=%s and date_invoice<='%s' 
            '''%(mlg_type,chinhanh_id[0],partner_id,period_to.date_stop)
            if lcntu['loai']=='loai_nodoanhthu' and lcntu['id']:
                sql+='''
                    and loai_nodoanhthu_id = %s 
                '''%(lcntu['id'])
            if lcntu['loai']=='loai_baohiem' and lcntu['id']:
                sql+='''
                    and loai_baohiem_id = %s 
                '''%(lcntu['id'])
            if lcntu['loai']=='loai_vipham' and lcntu['id']:
                sql+='''
                    and loai_vipham_id = %s 
                '''%(lcntu['id'])
            if lcntu['loai']=='maxuong' and lcntu['id']:
                sql+='''
                    and ma_xuong_id = %s 
                '''%(lcntu['id'])
            if lcntu['loai']=='loai_tamung' and lcntu['id']:
                sql+='''
                    and loai_tamung_id = %s 
                '''%(lcntu['id'])
            sql += ''' ))
                    and date between '%s' and '%s' '''%(period_from.date_start,period_to.date_stop)
            self.cr.execute(sql)
            co = self.cr.fetchone()[0]
            
            sql = '''
                select case when sum(so_tien)!=0 then sum(so_tien) else 0 end tonglaithu
                    from so_tien_lai where invoice_id in (select id from account_invoice where mlg_type='%s' and chinhanh_id=%s
                        and date_invoice<='%s' and state in ('open','paid') and partner_id = %s) and ngay between '%s' and '%s'
            '''%(mlg_type,chinhanh_id[0],period_to.date_stop,partner_id,period_from.date_start,period_to.date_stop)
            self.cr.execute(sql)
            thutienlai = self.cr.fetchone()[0]
            
            nocuoiky = nodauky+no-co-thutienlai
            self.tongcongno += nocuoiky
            return nocuoiky
        return 0
    
    def get_congno_data(self):
        if self.partner_ids:
            p_ids = self.partner_ids
            p_ids = str(p_ids).replace('[', '(')
            p_ids = str(p_ids).replace(']', ')')
            period_from_id = wizard_data['period_from_id']
            period_to_id = wizard_data['period_to_id']
            period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
            period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
            chinhanh_id = wizard_data['chinhanh_id']
            mlg_type = wizard_data['mlg_type']
            for lcntu in self.loai_congno_tuongung:
                if lcntu['loai']=='loai_conlai':
                    sql = '''
                        select cndk.partner_id as partner_id, case when sum(so_tien_no)!=0 then sum(so_tien_no) else 0 end sotien
                            from congno_dauky_line cndkl
                                left join congno_dauky cndk on cndkl.congno_dauky_id = cndk.id
                                where cndkl. mlg_type='%s' and cndkl.chinhanh_id=%s
                                    cndk.partner_id in %s and cndk.period_id=%s
                                group by cndk.partner_id
                    '''%(mlg_type,chinhanh_id[0],p_ids,period_id[0])
                    self.cr.execute(sql)
                    cndks = self.cr.dictfetchall()
                    for cndk in cndks:
                        if self.congno_dict.get('loai_conlai', False):
                            if self.congno_dict['loai_conlai'].get(cndk['partner_id'], False):
                                if self.congno_dict['loai_conlai'][cndk['partner_id']].get('ndk', False):
                                    self.congno_dict['loai_conlai'][cndk['partner_id']]['ndk'] += cndk['sotien']
                                else:
                                    self.congno_dict['loai_conlai'][cndk['partner_id']] = {'ndk': cndk['sotien']}
                            else:
                                self.congno_dict['loai_conlai'] = {cndk['partner_id']: {'ndk': cndk['sotien']}}
                        else:
                            self.congno_dict={'loai_conlai': {cndk['partner_id']: {'ndk': cndk['sotien']}}}
                if lcntu['loai']!='loai_conlai' and lcntu['id']:
                    sql = '''
                        select case when sum(so_tien_no)!=0 then sum(so_tien_no) else 0 end nodauky
                            from chitiet_congno_dauky_line where congno_dauky_line_id in (select id from congno_dauky_line where mlg_type='%s' and chinhanh_id=%s
                                and congno_dauky_id in (select id from congno_dauky where partner_id=%s and period_id=%s)) and loai_id=%s
                    '''%(mlg_type,chinhanh_id[0],self.partner_ids,period_id[0],lcntu['id'])
                
                self.cr.execute(sql)
                nodauky = self.cr.fetchone()[0]
        return True
    
    def get_no(self, partner_id,lcntu):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        mlg_type = wizard_data['mlg_type']
        sql = '''
            select case when sum(COALESCE(ai.so_tien,0)+COALESCE(ai.sotien_lai,0))!=0 then sum(COALESCE(ai.so_tien,0)+COALESCE(ai.sotien_lai,0)) else 0 end sotienno
            
                from account_invoice ai
                left join res_partner rp on rp.id = ai.partner_id
                
                where ai.partner_id=%s and ai.state in ('open','paid') and ai.date_invoice between '%s' and '%s' and ai.chinhanh_id=%s
                    and ai.mlg_type='%s' 
        '''%(partner_id,period_from.date_start,period_to.date_stop,chinhanh_id[0],mlg_type)
        if lcntu['loai']=='loai_nodoanhthu' and lcntu['id']:
            sql+='''
                and ai.loai_nodoanhthu_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_baohiem' and lcntu['id']:
            sql+='''
                and ai.loai_baohiem_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_vipham' and lcntu['id']:
            sql+='''
                and ai.loai_vipham_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='maxuong' and lcntu['id']:
            sql+='''
                and ai.ma_xuong_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_tamung' and lcntu['id']:
            sql+='''
                and ai.loai_tamung_id = %s 
            '''%(lcntu['id'])
        self.cr.execute(sql)
        no = self.cr.fetchone()[0]
        self.tongno += no
        return no
    
    def get_co(self, partner_id,lcntu):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        mlg_type = wizard_data['mlg_type']
        sql = '''
            select case when sum(credit)!=0 then sum(credit) else 0 end sotien
                from account_move_line
                where move_id in (select move_id from account_voucher
                    where reference in (select name from account_invoice
                        where mlg_type='%s' and state in ('open','paid') and chinhanh_id=%s and partner_id=%s and date_invoice<='%s' 
        '''%(mlg_type,chinhanh_id[0],partner_id,period_to.date_stop)
        if lcntu['loai']=='loai_nodoanhthu' and lcntu['id']:
            sql+='''
                and loai_nodoanhthu_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_baohiem' and lcntu['id']:
            sql+='''
                and loai_baohiem_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_vipham' and lcntu['id']:
            sql+='''
                and loai_vipham_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='maxuong' and lcntu['id']:
            sql+='''
                and ma_xuong_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_tamung' and lcntu['id']:
            sql+='''
                and loai_tamung_id = %s 
            '''%(lcntu['id'])
        sql += ''' ))
                and date between '%s' and '%s' '''%(period_from.date_start,period_to.date_stop)
        self.cr.execute(sql)
        co = self.cr.fetchone()[0]
        
        sql = '''
            select case when sum(so_tien)!=0 then sum(so_tien) else 0 end sotien
            
                from so_tien_lai where invoice_id in (
                        select id from account_invoice where mlg_type='%s' and state in ('open','paid') and chinhanh_id=%s and partner_id=%s and date_invoice<='%s' 
        '''%(mlg_type,chinhanh_id[0],partner_id,period_to.date_stop)
        if lcntu['loai']=='loai_nodoanhthu' and lcntu['id']:
            sql+='''
                and loai_nodoanhthu_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_baohiem' and lcntu['id']:
            sql+='''
                and loai_baohiem_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_vipham' and lcntu['id']:
            sql+='''
                and loai_vipham_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='maxuong' and lcntu['id']:
            sql+='''
                and ma_xuong_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_tamung' and lcntu['id']:
            sql+='''
                and loai_tamung_id = %s 
            '''%(lcntu['id'])
        sql += ''' )
                and ngay between '%s' and '%s' '''%(period_from.date_start,period_to.date_stop)
        self.cr.execute(sql)
        lai = self.cr.fetchone()[0]
        
        self.tongco += co+lai
        return co+lai
    
    def get_chitiet_congno(self, partner_id,lcntu):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        mlg_type = wizard_data['mlg_type']
        sql = '''
            select rp.ma_doi_tuong as madoituong,rp.name as tendoituong,
                sum(COALESCE(ai.so_tien,0)+COALESCE(ai.sotien_lai,0)) as no,
                sum(COALESCE(ai.so_tien,0)+COALESCE(ai.sotien_lai,0)-COALESCE(ai.residual,0)-COALESCE(ai.sotien_lai_conlai,0)) as co
            
                from account_invoice ai
                left join res_partner rp on rp.id = ai.partner_id
                
                where ai.partner_id=%s and ai.state in ('open','paid') and ai.date_invoice between '%s' and '%s' and ai.chinhanh_id=%s
                    and ai.mlg_type='%s' 
        '''%(partner_id,period_from.date_start,period_to.date_stop,chinhanh_id[0],mlg_type)
        if lcntu['loai']=='loai_nodoanhthu' and lcntu['id']:
            sql+='''
                and ai.loai_nodoanhthu_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_baohiem' and lcntu['id']:
            sql+='''
                and ai.loai_baohiem_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_vipham' and lcntu['id']:
            sql+='''
                and ai.loai_vipham_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='maxuong' and lcntu['id']:
            sql+='''
                and ai.ma_xuong_id = %s 
            '''%(lcntu['id'])
        if lcntu['loai']=='loai_tamung' and lcntu['id']:
            sql+='''
                and ai.loai_tamung_id = %s 
            '''%(lcntu['id'])
        sql += ''' group by rp.ma_doi_tuong,rp.name '''
        self.cr.execute(sql)
        lines = self.cr.dictfetchall()
        for line in lines:
            self.tongno += line['no']
            self.tongco += line['co']
        if not lines:
            period_id = wizard_data['period_from_id']
            chinhanh_id = wizard_data['chinhanh_id']
            mlg_type = wizard_data['mlg_type']
            sql = '''
                select case when sum(so_tien_no)!=0 then sum(so_tien_no) else 0 end nodauky
                    from congno_dauky_line where mlg_type='%s' and chinhanh_id=%s
                        and congno_dauky_id in (select id from congno_dauky where partner_id=%s and period_id=%s)
            '''%(mlg_type,chinhanh_id[0],partner_id,period_id[0])
            if lcntu['loai']!='loai_conlai' and lcntu['id']:
                sql = '''
                    select case when sum(so_tien_no)!=0 then sum(so_tien_no) else 0 end nodauky
                        from chitiet_congno_dauky_line where congno_dauky_line_id in (select id from congno_dauky_line where mlg_type='%s' and chinhanh_id=%s
                            and congno_dauky_id in (select id from congno_dauky where partner_id=%s and period_id=%s)) and loai_id=%s
                '''%(mlg_type,chinhanh_id[0],partner_id,period_id[0],lcntu['id'])
            self.cr.execute(sql)
            nodauky = self.cr.fetchone()[0]
            
            period_from_id = wizard_data['period_from_id']
            period_to_id = wizard_data['period_to_id']
            period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
            period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
            chinhanh_id = wizard_data['chinhanh_id']
            mlg_type = wizard_data['mlg_type']
            sql = '''
                select case when sum(COALESCE(residual,0)+COALESCE(sotien_lai_conlai,0))!=0 then sum(COALESCE(residual,0)+COALESCE(sotien_lai_conlai,0)) else 0 end notrongky
                    from account_invoice where mlg_type='%s' and chinhanh_id=%s and partner_id=%s
                        and date_invoice between '%s' and '%s' and state in ('open','paid') 
            '''%(mlg_type,chinhanh_id[0],partner_id,period_from.date_start,period_to.date_stop)
            if lcntu['loai']=='loai_nodoanhthu' and lcntu['id']:
                sql+='''
                    and loai_nodoanhthu_id = %s 
                '''%(lcntu['id'])
            if lcntu['loai']=='loai_baohiem' and lcntu['id']:
                sql+='''
                    and loai_baohiem_id = %s 
                '''%(lcntu['id'])
            if lcntu['loai']=='loai_vipham' and lcntu['id']:
                sql+='''
                    and loai_vipham_id = %s 
                '''%(lcntu['id'])
            if lcntu['loai']=='maxuong' and lcntu['id']:
                sql+='''
                    and ma_xuong_id = %s 
                '''%(lcntu['id'])
            if lcntu['loai']=='loai_tamung' and lcntu['id']:
                sql+='''
                    and loai_tamung_id = %s 
                '''%(lcntu['id'])
            self.cr.execute(sql)
            notrongky = self.cr.fetchone()[0]
            nocuoiky = nodauky+notrongky
            if nocuoiky:
                partner = self.pool.get('res.partner').browse(self.cr, self.uid, partner_id)
                lines = [{'madoituong':partner.ma_doi_tuong,'tendoituong':partner.name,'no':0,'co':0}]
        return lines
            
    
    