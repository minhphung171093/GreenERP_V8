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

from openerp import tools
from openerp.osv import fields, osv
from openerp import pooler

class theo_dia_ban_report(osv.osv):
    _name = "theo.dia.ban.report"
    _description = "Theo dia ban"
    _auto = False
#     _rec_name = 'date'

    _columns = {
        'khu_vuc_id': fields.many2one('khu.vuc','Khu vực', readonly=True),
        'tinh_tp_id': fields.many2one('res.country.state','Tỉnh/TP', readonly=True),
        'tong_so_du_an': fields.integer('TỔNG SỐ', readonly=True),
        'pt_du_an': fields.float('%', readonly=True),
        'tong_so_von_dau_tu': fields.float('TỔNG VĐT', readonly=True),
        'pt_von_dau_tu': fields.float('%', readonly=True),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT 
                min(id) as id,
                khu_vuc_id as khu_vuc_id,
                tinh_tp_id as tinh_tp_id, 
                count(id) as tong_so_du_an, 
                count(id)::double precision/(select CASE WHEN count(id)::double precision=0 THEN 1 ELSE count(id)::double precision END from giay_chung_nhan_dau_tu)*100 as pt_du_an,
                sum(von_dau_tu_vn) as tong_so_von_dau_tu, 
                (sum(von_dau_tu_vn)/(select CASE WHEN sum(von_dau_tu_vn)=0 THEN 1 ELSE sum(von_dau_tu_vn) END from giay_chung_nhan_dau_tu))*100 as pt_von_dau_tu
            FROM giay_chung_nhan_dau_tu
            GROUP BY khu_vuc_id,tinh_tp_id
            )""" %(self._table))
theo_dia_ban_report()

class theo_quoc_gia_report(osv.osv):
    _name = "theo.quoc.gia.report"
    _description = "Theo quoc gia"
    _auto = False
#     _rec_name = 'date'

    _columns = {
        'quoc_gia_id': fields.many2one('res.country','Quốc gia', readonly=True),
        'tinh_tp_id': fields.many2one('res.country.state','Tỉnh/TP', readonly=True),
        'tong_so_du_an': fields.integer('TỔNG SỐ', readonly=True),
        'pt_du_an': fields.float('%', readonly=True),
        'tong_so_von_dau_tu': fields.float('TỔNG VĐT', readonly=True),
        'pt_von_dau_tu': fields.float('%', readonly=True),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT 
                min(id) as id,
                quoc_gia as quoc_gia_id,
                tinh_tp_id as tinh_tp_id, 
                count(id) as tong_so_du_an, 
                count(id)::double precision/(select CASE WHEN count(id)::double precision=0 THEN 1 ELSE count(id)::double precision END from giay_chung_nhan_dau_tu)*100 as pt_du_an,
                sum(von_dau_tu_vn) as tong_so_von_dau_tu, 
                (sum(von_dau_tu_vn)/(select CASE WHEN sum(von_dau_tu_vn)=0 THEN 1 ELSE sum(von_dau_tu_vn) END from giay_chung_nhan_dau_tu))*100 as pt_von_dau_tu
            FROM giay_chung_nhan_dau_tu
            GROUP BY quoc_gia_id,tinh_tp_id
            )""" %(self._table))
theo_quoc_gia_report()

class theo_nganh_nghe_report(osv.osv):
    _name = "theo.nganh.nghe.report"
    _description = "Theo nganh nghe"
    _auto = False
#     _rec_name = 'date'

    _columns = {
        'nganh_nghe_id': fields.many2one('nganh.nghe','Ngành nghề', readonly=True),
        'tinh_tp_id': fields.many2one('res.country.state','Tỉnh/TP', readonly=True),
        'tong_so_du_an': fields.integer('TỔNG SỐ', readonly=True),
        'pt_du_an': fields.float('%', readonly=True),
        'tong_so_von_dau_tu': fields.float('TỔNG VĐT', readonly=True),
        'pt_von_dau_tu': fields.float('%', readonly=True),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT 
                min(id) as id,
                nganh_nghe_khac as nganh_nghe_id,
                tinh_tp_id as tinh_tp_id,
                count(id) as tong_so_du_an, 
                count(id)::double precision/(select CASE WHEN count(id)::double precision=0 THEN 1 ELSE count(id)::double precision END from giay_chung_nhan_dau_tu)*100 as pt_du_an,
                sum(von_dau_tu_vn) as tong_so_von_dau_tu, 
                (sum(von_dau_tu_vn)/(select CASE WHEN sum(von_dau_tu_vn)=0 THEN 1 ELSE sum(von_dau_tu_vn) END from giay_chung_nhan_dau_tu))*100 as pt_von_dau_tu
            FROM giay_chung_nhan_dau_tu
            GROUP BY nganh_nghe_khac,tinh_tp_id
            )""" %(self._table))
theo_nganh_nghe_report()

class theo_loai_hinh_doanh_nghiep_report(osv.osv):
    _name = "theo.loai.hinh.doanh.nghiep.report"
    _description = "Theo loai hinh doanh nghiep"
    _auto = False
#     _rec_name = 'date'

    _columns = {
        'loai_hinh_doanh_nghiep_id': fields.many2one('res.partner.category','Loại hình doanh nghiệp', readonly=True),
        'tinh_tp_id': fields.many2one('res.country.state','Tỉnh/TP', readonly=True),
        'tong_so_du_an': fields.integer('TỔNG SỐ', readonly=True),
        'pt_du_an': fields.float('%', readonly=True),
        'tong_so_von_dau_tu': fields.float('TỔNG VĐT', readonly=True),
        'pt_von_dau_tu': fields.float('%', readonly=True),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT 
                min(id) as id,
                loai_hinh_doanh_nghiep as loai_hinh_doanh_nghiep_id,
                tinh_tp_id as tinh_tp_id,
                count(id) as tong_so_du_an, 
                count(id)::double precision/(select CASE WHEN count(id)::double precision=0 THEN 1 ELSE count(id)::double precision END from giay_chung_nhan_dau_tu)*100 as pt_du_an,
                sum(von_dau_tu_vn) as tong_so_von_dau_tu, 
                (sum(von_dau_tu_vn)/(select CASE WHEN sum(von_dau_tu_vn)=0 THEN 1 ELSE sum(von_dau_tu_vn) END from giay_chung_nhan_dau_tu))*100 as pt_von_dau_tu
            FROM giay_chung_nhan_dau_tu
            GROUP BY loai_hinh_doanh_nghiep,tinh_tp_id
            )""" %(self._table))
theo_loai_hinh_doanh_nghiep_report()

class theo_hinh_thuc_dau_tu_report(osv.osv):
    _name = "theo.hinh.thuc.dau.tu.report"
    _description = "Theo hinh thuc dau tu"
    _auto = False
#     _rec_name = 'date'

    _columns = {
        'hinh_thuc_dau_tu_id': fields.many2one('hinh.thuc.dau.tu','Hình thức đầu tư', readonly=True),
        'tinh_tp_id': fields.many2one('res.country.state','Tỉnh/TP', readonly=True),
        'tong_so_du_an': fields.integer('TỔNG SỐ', readonly=True),
        'pt_du_an': fields.float('%', readonly=True),
        'tong_so_von_dau_tu': fields.float('TỔNG VĐT', readonly=True),
        'pt_von_dau_tu': fields.float('%', readonly=True),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT 
                min(id) as id,
                hinh_thuc_dau_tu_id as hinh_thuc_dau_tu_id,
                tinh_tp_id as tinh_tp_id,
                count(id) as tong_so_du_an, 
                count(id)::double precision/(select CASE WHEN count(id)::double precision=0 THEN 1 ELSE count(id)::double precision END from giay_chung_nhan_dau_tu)*100 as pt_du_an,
                sum(von_dau_tu_vn) as tong_so_von_dau_tu, 
                (sum(von_dau_tu_vn)/(select CASE WHEN sum(von_dau_tu_vn)=0 THEN 1 ELSE sum(von_dau_tu_vn) END from giay_chung_nhan_dau_tu))*100 as pt_von_dau_tu
            FROM giay_chung_nhan_dau_tu
            GROUP BY hinh_thuc_dau_tu_id,tinh_tp_id
            )""" %(self._table))
theo_hinh_thuc_dau_tu_report()

class theo_thoi_gian_report(osv.osv):
    _name = "theo.thoi.gian.report"
    _description = "Theo thoi gian"
    _auto = False
#     _rec_name = 'date'

    _columns = {
        'nam': fields.char('Thời gian', size=64, readonly=True),
        'tinh_tp_id': fields.many2one('res.country.state','Tỉnh/TP', readonly=True),
        'tong_so_du_an': fields.integer('TỔNG SỐ', readonly=True),
        'pt_du_an': fields.float('%', readonly=True),
        'tong_so_von_dau_tu': fields.float('TỔNG VĐT', readonly=True),
        'pt_von_dau_tu': fields.float('%', readonly=True),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT 
                min(id) as id,
                EXTRACT(YEAR FROM chung_nhan_lan_dau) as nam,
                tinh_tp_id as tinh_tp_id,
                count(id) as tong_so_du_an, 
                count(id)::double precision/(select CASE WHEN count(id)::double precision=0 THEN 1 ELSE count(id)::double precision END from giay_chung_nhan_dau_tu)*100 as pt_du_an,
                sum(von_dau_tu_vn) as tong_so_von_dau_tu, 
                (sum(von_dau_tu_vn)/(select CASE WHEN sum(von_dau_tu_vn)=0 THEN 1 ELSE sum(von_dau_tu_vn) END from giay_chung_nhan_dau_tu))*100 as pt_von_dau_tu
            FROM giay_chung_nhan_dau_tu
            GROUP BY EXTRACT(YEAR FROM chung_nhan_lan_dau),tinh_tp_id
            )""" %(self._table))
theo_thoi_gian_report()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
