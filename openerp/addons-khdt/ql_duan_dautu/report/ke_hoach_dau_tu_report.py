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
        self.danhmuc_tam = []
        self.danhmuc_arr = []
        self.tongso = 0.0
        self.tongdt = 0.0
        self.kqdt = 0.0
        self.luyke_capphat = 0.0
        self.kehoach_daduyet_gannhat = 0.0
        self.uoc_thuchien = 0.0
        self.chudautu_dexuat = 0.0
        self.kehoach_dieuhoa = 0.0
        self.sotien_capphat = 0.0
        self.khoiluong_thuchien = 0.0
        self.khoiluong_hoanthanh = 0.0
        
        self.localcontext.update({
             'get_from_date':self.get_from_date,
             'get_to_date':self.get_to_date,
             'get_giaidoan_line': self.get_giaidoan_line,
             'get_duan_line': self.get_duan_line,
             'get_vietname_date': self.get_vietname_date,
             'get_khoiluong_thuchien': self.get_khoiluong_thuchien,
             'get_danhmuc': self.get_danhmuc,
             'get_tong_so': self.get_tong_so,
             'get_khoiluong_pheduyet_tkkt_tdt':self.get_khoiluong_pheduyet_tkkt_tdt,
             'get_qd_dautu':self.get_qd_dautu,
             'get_qd_kqdt':self.get_qd_kqdt,
             'get_khoiluong':self.get_khoiluong,
             'get_kehoachvon': self.get_kehoachvon,
        })
    
    def get_vietname_date(self, date):
        if not date:
            date = time.strftime(DATE_FORMAT)
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
    
    def khoitao_danhmuc(self, danhmuc_cha=[]):
        wizard_data = self.localcontext['data']['form']
        from_date = wizard_data['date_from']
        to_date = wizard_data['date_to']
        danhmuc_obj = self.pool.get('duan.danhmuc')
        duan_obj = self.pool.get('duan.dautu')
        if not danhmuc_cha:
            danhmuc_con_ids = danhmuc_obj.search(self.cr, self.uid, [('danhmuc_cha', '=', False)])
        else:
            danhmuc_con_ids = danhmuc_obj.search(self.cr, self.uid, [('danhmuc_cha', '=', danhmuc_cha[0])], order='stt desc')
        for danhmuc_con_id in danhmuc_con_ids:
            danhmuc = danhmuc_obj.browse(self.cr, self.uid, danhmuc_con_id)
            self.khoitao_danhmuc([danhmuc_con_id, self.tongso, danhmuc.name, danhmuc.stt])
            sql = '''
                SELECT id 
                FROM duan_dautu
                WHERE giai_doan_id is not null
                   and danhmuc_id = %(danhmuc)s
                   and id in (select duan_dautu_id from duan_dautu_thuchien where nam = '%(from_date)s')
            ''' % {'danhmuc': danhmuc_con_id,
                 'from_date': from_date[:4]}
            self.cr.execute(sql)
            duan_ids = [row[0] for row in self.cr.fetchall()]
#             duan_ids = duan_obj.search(self.cr, self.uid, [('danhmuc_id','=',danhmuc_con_id),('giai_doan_id','!=',False)])
            tongdt_line = kqdt_line = luyke_capphat_line = kehoach_daduyet_gannhat_line = uoc_thuchien_line = chudautu_dexuat_line = kehoach_dieuhoa_line = sotien_capphat_line = khoiluong_thuchien_line = khoiluong_hoanthanh_line = 0
            for duan_dautu in duan_obj.browse(self.cr, self.uid, duan_ids):
                self.tongso += duan_dautu.tongmuc_dautu
                for tdt in duan_dautu.pheduyet_tdt_lines:
                    tongdt_line = tdt.pheduyet_tdt_tongdutoan
                self.tongdt += tongdt_line
                tongdt_line = 0
                for kq in duan_dautu.pheduyet_kqdt_lines:
                    kqdt_line = kq.pheduyet_giatrungthau
                self.kqdt += kqdt_line
                kqdt_line = 0
                for khv in duan_dautu.ke_hoach_von:
                    if khv.nam == from_date[:4]:
                        luyke_capphat_line = khv.luyke_capphat_namtruoc
                        kehoach_daduyet_gannhat_line = khv.kehoach_daduyet_gannhat
                        uoc_thuchien_line = khv.uoc_thuchien
                        chudautu_dexuat_line = khv.chudautu_dexuat
                        kehoach_dieuhoa_line = khv.kehoach_dieuhoa
                        for ct in khv.thuchien_chitiet:
                            if ct.ngay <= from_date:
                                sotien_capphat_line = ct.sotien
                                khoiluong_thuchien_line = ct.khoiluong_thuchien
                                khoiluong_hoanthanh_line = ct.khoiluong_hoanthanh
                self.luyke_capphat += luyke_capphat_line
                self.kehoach_daduyet_gannhat += kehoach_daduyet_gannhat_line
                self.uoc_thuchien += uoc_thuchien_line
                self.chudautu_dexuat += chudautu_dexuat_line
                self.kehoach_dieuhoa += kehoach_dieuhoa_line
                self.sotien_capphat += sotien_capphat_line
                self.khoiluong_thuchien += khoiluong_thuchien_line
                self.khoiluong_hoanthanh += khoiluong_hoanthanh_line
                luyke_capphat_line = 0
                kehoach_daduyet_gannhat_line = 0
                uoc_thuchien_line = 0
                chudautu_dexuat_line = 0
                kehoach_dieuhoa_line = 0
                sotien_capphat_line = 0
                khoiluong_thuchien_line = 0
                khoiluong_hoanthanh_line = 0
            if self.danhmuc_tam:
                danhmuc_con = []
                for line in self.danhmuc_tam:
                    danhmuc_con.append(line[0])
                for danhmucs in danhmuc_obj.browse(self.cr, self.uid, danhmuc_con):
                    if danhmucs.danhmuc_cha.id == danhmuc_con_id:
                        for line in self.danhmuc_tam:
                            if danhmucs.id == line[0]:
                                self.tongso += line[1]
                                self.tongdt += line[4]
                                self.kqdt += line[5]
                                self.luyke_capphat += line[6]
                                self.kehoach_daduyet_gannhat += line[7]
                                self.uoc_thuchien += line[8]
                                self.chudautu_dexuat += line[9]
                                self.kehoach_dieuhoa += line[10]
                                self.sotien_capphat += line[11]
                                self.khoiluong_thuchien += line[12]
                                self.khoiluong_hoanthanh += line[13]
            self.danhmuc_tam.append([danhmuc_con_id, self.tongso, danhmuc.name, danhmuc.stt, self.tongdt, self.kqdt,self.luyke_capphat,self.kehoach_daduyet_gannhat,self.uoc_thuchien,self.chudautu_dexuat,self.kehoach_dieuhoa,self.sotien_capphat,self.khoiluong_thuchien,self.khoiluong_hoanthanh])
            self.tongso = 0
            self.tongdt = 0
            self.kqdt = 0
            self.luyke_capphat = 0
            self.kehoach_daduyet_gannhat = 0
            self.uoc_thuchien = 0
            self.chudautu_dexuat = 0
            self.kehoach_dieuhoa = 0
            self.sotien_capphat = 0
            self.khoiluong_thuchien = 0
            self.khoiluong_hoanthanh = 0
            if not danhmuc_cha:
                self.danhmuc_tam.reverse()
                self.danhmuc_arr += self.danhmuc_tam
                self.danhmuc_tam = []
        return True
    
    def get_danhmuc(self):
        danhmuc_obj = self.pool.get('duan.danhmuc')
        self.khoitao_danhmuc()
#         danhmucs = danhmuc_obj.browse(self.cr, self.uid, self.danhmuc_arr)
        return self.danhmuc_arr
    
    def get_giaidoan_line(self, danhmuc_id):
        wizard_data = self.localcontext['data']['form']
        from_date = wizard_data['date_from']
        to_date = wizard_data['date_to']
        giaidoan_obj = self.pool.get('duan.giaidoan')
        giaidoan_ids = []
        for giaidoan in giaidoan_obj.search(self.cr, self.uid, []):
            sql = '''
                SELECT id 
                FROM duan_dautu
                WHERE giai_doan_id = %(giaidoan)s 
                   and danhmuc_id = %(danhmuc)s
                   and id in (select duan_dautu_id from duan_dautu_thuchien where nam = '%(from_date)s')
            ''' % {'giaidoan': giaidoan,
                 'danhmuc': danhmuc_id,
                 'from_date': from_date[:4],
                 }
            self.cr.execute(sql)
            duan_ids = [row[0] for row in self.cr.fetchall()]
            if duan_ids:
                giaidoan_ids.append(giaidoan)
        giaidoans = giaidoan_obj.browse(self.cr, self.uid, giaidoan_ids)
        return giaidoans
    
    def get_duan_line(self, danhmuc, giaidoan):
        duan_obj = self.pool.get('duan.dautu')
        wizard_data = self.localcontext['data']['form']
        from_date = wizard_data['date_from']
        to_date = wizard_data['date_to']
        sql = '''
            SELECT id 
            FROM duan_dautu
            WHERE giai_doan_id = %(giaidoan)s 
               and danhmuc_id = %(danhmuc)s
               and id in (select duan_dautu_id from duan_dautu_thuchien where nam = '%(from_date)s')
        ''' % {'giaidoan': giaidoan,
             'danhmuc': danhmuc,
             'from_date': from_date[:4],
             }
        self.cr.execute(sql)
        duan_ids = [row[0] for row in self.cr.fetchall()]
        duans = duan_obj.browse(self.cr, self.uid, duan_ids)
        return duans
    
    def get_tong_so(self):
        wizard_data = self.localcontext['data']['form']
        from_date = wizard_data['date_from']
        to_date = wizard_data['date_to']
        sql = '''
            SELECT (SELECT CASE WHEN sum(tongmuc_dautu)!= 0 THEN sum(tongmuc_dautu) ELSE 0 END
                FROM duan_dautu
                WHERE giai_doan_id is not null
                and id in (select duan_dautu_id from duan_dautu_thuchien where nam = '%(from_date)s')) as tongmuc_dautu
        ''' % {'from_date': from_date[:4],
             }
        self.cr.execute(sql)
        tongmuc_dautu = self.cr.dictfetchone()['tongmuc_dautu']
        sql = '''
            SELECT id
                FROM duan_dautu
                WHERE giai_doan_id is not null
                and id in (select duan_dautu_id from duan_dautu_thuchien where nam = '%(from_date)s')
        ''' % {'from_date': from_date[:4],
             }
        self.cr.execute(sql)
        duan_ids = [x[0] for x in self.cr.fetchall()]
        tongdt = kqdt = tongdt_line = kqdt_line = 0
        luyke_capphat_line = kehoach_daduyet_gannhat_line = uoc_thuchien_line = chudautu_dexuat_line = kehoach_dieuhoa_line = sotien_capphat_line = khoiluong_thuchien_line = khoiluong_hoanthanh_line = 0
        luyke_capphat = kehoach_daduyet_gannhat = uoc_thuchien = chudautu_dexuat = kehoach_dieuhoa = sotien_capphat = khoiluong_thuchien = khoiluong_hoanthanh = 0
        for duan in self.pool.get('duan.dautu').browse(self.cr, self.uid, duan_ids):
            for tdt in duan.pheduyet_tdt_lines:
                tongdt_line = tdt.pheduyet_tdt_tongdutoan
            tongdt += tongdt_line
            tongdt_line = 0
            for kq in duan.pheduyet_kqdt_lines:
                kqdt_line = kq.pheduyet_giatrungthau
            kqdt += kqdt_line
            kqdt_line = 0
            for khv in duan.ke_hoach_von:
                if khv.nam == from_date[:4]:
                    luyke_capphat_line = khv.luyke_capphat_namtruoc
                    kehoach_daduyet_gannhat_line = khv.kehoach_daduyet_gannhat
                    uoc_thuchien_line = khv.uoc_thuchien
                    chudautu_dexuat_line = khv.chudautu_dexuat
                    kehoach_dieuhoa_line = khv.kehoach_dieuhoa
                    for ct in khv.thuchien_chitiet:
                        if ct.ngay <= from_date:
                            sotien_capphat_line = ct.sotien
                            khoiluong_thuchien_line = ct.khoiluong_thuchien
                            khoiluong_hoanthanh_line = ct.khoiluong_hoanthanh
            luyke_capphat += luyke_capphat_line
            kehoach_daduyet_gannhat += kehoach_daduyet_gannhat_line
            uoc_thuchien += uoc_thuchien_line
            chudautu_dexuat += chudautu_dexuat_line
            kehoach_dieuhoa += kehoach_dieuhoa_line
            sotien_capphat += sotien_capphat_line
            khoiluong_thuchien += khoiluong_thuchien_line
            khoiluong_hoanthanh += khoiluong_hoanthanh_line
            luyke_capphat_line = 0
            kehoach_daduyet_gannhat_line = 0
            uoc_thuchien_line = 0
            chudautu_dexuat_line = 0
            kehoach_dieuhoa_line = 0
            sotien_capphat_line = 0
            khoiluong_thuchien_line = 0
            khoiluong_hoanthanh_line = 0
        vals = {
            'tongmuc_dautu': tongmuc_dautu,
            'pheduyet_tdt_tongdutoan': tongdt,
            'pheduyet_giatrungthau': kqdt,
            'luyke_capphat': luyke_capphat,
            'kehoach_daduyet_gannhat': kehoach_daduyet_gannhat,
            'uoc_thuchien': uoc_thuchien,
            'chudautu_dexuat': chudautu_dexuat,
            'kehoach_dieuhoa': kehoach_dieuhoa,
            'sotien_capphat': sotien_capphat,
            'khoiluong_thuchien': khoiluong_thuchien,
            'khoiluong_hoanthanh': khoiluong_hoanthanh,
        }
        
        return vals
    
    def get_khoiluong_thuchien(self, duan_dautu_id):
        wizard_data = self.localcontext['data']['form']
        from_date = wizard_data['date_from']
        to_date = wizard_data['date_to']
        sql = '''
            SELECT CASE WHEN sum(sotien)!= 0 THEN sum(sotien) ELSE 0 END as sotien
            FROM duan_dautu_thuchien_chitiet
            WHERE duan_dautu_thuchien_id in (SELECT id FROM duan_dautu_thuchien WHERE duan_dautu_id = %(duan_dautu_id)s) 
               and (ngay between '%(from_date)s' and '%(to_date)s')
        ''' % {'duan_dautu_id': duan_dautu_id,
             'from_date': from_date,
             'to_date': to_date}
        self.cr.execute(sql)
        return self.cr.dictfetchall()[0]
    
    def get_khoiluong_pheduyet_tkkt_tdt(self, duan_object):
        values ={}
        if duan_object:
            for pheduyet in duan_object.pheduyet_tdt_lines:
                values ={
                     'tkkt_tdt_soquyetdinh':pheduyet.pheduyet_tdt_soquyetdinh_id and pheduyet.pheduyet_tdt_soquyetdinh_id.name or '',
                     'tkkt_tdt_ngaythangnam':self.get_vietname_date(pheduyet.pheduyet_tdt_ngay),
                     'tkkt_tdt_tongdutoan':pheduyet.pheduyet_tdt_tongdutoan,
                     }
            return values
        
    def get_qd_kqdt(self,duan_object):
        values ={}
        if duan_object:
            for kq in duan_object.pheduyet_kqdt_lines:
                values ={
                     'kq_pheduyet_kqdt_ngay':kq.pheduyet_kqdt_ngay and self.get_vietname_date(kq.pheduyet_kqdt_ngay) or False,
                     'kq_pheduyet_giagoithau':kq.pheduyet_giagoithau or False,
                     'kq_pheduyet_kqdt_soquyetdinh':kq.pheduyet_kqdt_soquyetdinh_id and kq.pheduyet_kqdt_soquyetdinh_id.name or False,
                     }
            return values
        
    def get_qd_dautu(self,duan_object):
        values ={}
        if duan_object:
            for qd in duan_object.quyetdinh_dautu_lines:
                values ={
                     'qd_dautu_ngay':qd.dautu_ngay and self.get_vietname_date(qd.dautu_ngay),
                     'qd_dautu_tongmuc':duan_object.tongmuc_dautu or False,
                     'qd_dautu_soquyetdinh':qd.dautu_soquyetdinh_id and qd.dautu_soquyetdinh_id.name or False,
                     }
            return values
        
    def get_khoiluong(self,duan_object):
        wizard_data = self.localcontext['data']['form']
        from_date = wizard_data['date_from']
        sotien_capphat = khoiluong_thuchien = khoiluong_hoanthanh = 0
        if duan_object:
            for khv in duan_object.ke_hoach_von:
                for ct in khv.thuchien_chitiet:
                    if ct.ngay <= from_date:
                        sotien_capphat = ct.sotien
                        khoiluong_thuchien = ct.khoiluong_thuchien
                        khoiluong_hoanthanh = ct.khoiluong_hoanthanh
        values = {
         'sotien_capphat':sotien_capphat,
         'khoiluong_thuchien':khoiluong_thuchien,
         'khoiluong_hoanthanh':khoiluong_hoanthanh,
         }
        return values
    
    def get_kehoachvon(self, duan_object):
        wizard_data = self.localcontext['data']['form']
        from_date = wizard_data['date_from']
        sql = '''
            SELECT luyke_capphat_namtruoc,kehoach_daduyet_gannhat,uoc_thuchien,chudautu_dexuat,kehoach_dieuhoa
                FROM duan_dautu_thuchien
                WHERE duan_dautu_id = %s
                AND nam = '%s' limit 1
        ''' %(duan_object.id,from_date[:4])
        self.cr.execute(sql)
        kehoachvon = self.cr.dictfetchone()
        vals = {
            'luyke_capphat_namtruoc': kehoachvon['luyke_capphat_namtruoc'],
            'kehoach_daduyet_gannhat': kehoachvon['kehoach_daduyet_gannhat'],
            'uoc_thuchien': kehoachvon['uoc_thuchien'],
            'chudautu_dexuat': kehoachvon['chudautu_dexuat'],
            'kehoach_dieuhoa': kehoachvon['kehoach_dieuhoa'],
        }
        return vals
    
    
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
