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
             'get_vietname_date': self.get_vietname_date,
             'get_can_cu_phap_ly': self.get_can_cu_phap_ly,
             'get_nganh_nghe': self.get_nganh_nghe,
             'get_nghia_vu': self.get_nghia_vu,
             'get_so_lan_thay_doi': self.get_so_lan_thay_doi,
             'get_nha_dau_tu': self.get_nha_dau_tu,
        })
        
    def get_vietname_date(self, date):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_can_cu_phap_ly(self, gcndt_id):
        sql=''' select canculuat_id
                from hosodautu_canculuat_ref
                where hosodautu_id = %s'''%(gcndt_id)
        self.cr.execute(sql)
        phaply_ids = [row[0] for row in self.cr.fetchall()]
        phaplys = self.pool.get('can.cu.luat').browse(self.cr,self.uid,phaply_ids)
        return phaplys
    
    def get_nganh_nghe(self, gcndt_id):
        sql=''' select nganh_nghe_id
                from nganh_nghe_ho_so_rel
                where ho_so_id = %s'''%(gcndt_id)
        self.cr.execute(sql)
        nganhnghe_ids = [row[0] for row in self.cr.fetchall()]
        nganhnghes = self.pool.get('nganh.nghe').browse(self.cr,self.uid,nganhnghe_ids)
        return nganhnghes
        
    def get_nghia_vu(self, gcndt_id):
        sql=''' select nghiavunhadautu_id
                from hosodautu_nghiavunhadautu_ref
                where hosodautu_id = %s'''%(gcndt_id)
        self.cr.execute(sql)
        nghiavu_ids = [row[0] for row in self.cr.fetchall()]
        nghiavus = self.pool.get('nghiavu.nhadautu').browse(self.cr,self.uid,nghiavu_ids)
        return nghiavus
    
    def get_so_lan_thay_doi(self, gcndt_id):
        gcndt = self.pool.get('giay.chung.nhan.dau.tu').browse(self.cr, self.uid, gcndt_id)
        if gcndt.so_lan_thay_doi == 0:
            kq = ''
        else:
            kq = 'Chứng nhận thay đổi lần thứ ' + str(gcndt.so_lan_thay_doi) +' : ngày '+str(gcndt.write_date[8:10])+' tháng '+str(gcndt.write_date[5:7])+' năm '+str(gcndt.write_date[:4])
        return kq
    
    def get_nha_dau_tu(self, gcndt_id):
        res = []
        temp = 1
        sql=''' select partner_id
                from nha_dau_tu_rel
                where ho_so_id = %s'''%(gcndt_id)
        self.cr.execute(sql)
        nhadautu_ids = [row[0] for row in self.cr.fetchall()]
        res.append('')
        for nhadautu in self.pool.get('res.partner').browse(self.cr, self.uid, nhadautu_ids):
            if nhadautu.is_company == True:
                ndt = str(temp)+'. '+str(nhadautu.name or '')+'; Giấy phép thành lập số '+str(nhadautu.giay_thanh_lap_so or '')+'; cấp ngày '+str(nhadautu.ngay_cap_phep_thanh_lap or '')+'; nơi cấp '+str(nhadautu.noi_cap_phep_thanh_lap or '')+'; địa chỉ trụ sở chính '+str(nhadautu.street or '')+', '+str(nhadautu.state_id.name or '')+', '+str(nhadautu.country_id.name or '')
                res.append(ndt)
                temp += 1
                if nhadautu.child_ids:
                    for child in nhadautu.child_ids:
                        ndd = 'Đại diện bởi: '+str(child.name or '')+'; quốc tịch '+str(child.country_id.name or '')
                        res.append(ndd)
                res.append('')
            else:
                ndt = str(temp)+'. '+str(nhadautu.name or '')+'; quốc tịch '+str(nhadautu.country_id.name or '')
                res.append(ndt)
                temp += 1
                res.append('')
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
