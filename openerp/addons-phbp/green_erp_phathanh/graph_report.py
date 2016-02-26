# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields

class doanhthu_graph_report(osv.osv):
    _name = "doanhthu.graph.report"
    _description = "Báo cáo doanh thu"
    _auto = False
    _columns = {
        'daily_id': fields.many2one('dai.ly','Đại lý'),
        'ky_ve_id': fields.many2one('ky.ve','Kỳ vé'),
        'doanh_thu': fields.integer('Doanh Thu'),
    }
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'doanhthu_graph_report')
        cr.execute("""
            create or replace view doanhthu_graph_report as (

                select id, daily_id, ky_ve_id, sum(doanh_thu) as doanh_thu
                from
                (
                select ppttl.id as id, ppttl.daily_id as daily_id, pptt.ky_ve_id as ky_ve_id,
                    case when (select sove_sau_dc from dieuchinh_line where phanphoi_line_id=ppttl.id order by id desc limit 1) is not null
                        then (select sove_sau_dc*lv.gia_tri from dieuchinh_line where phanphoi_line_id=ppttl.id order by id desc limit 1) else ppttl.sove_kynay*lv.gia_tri end doanh_thu
                    from phanphoi_tt_line ppttl 
                    left join phanphoi_truyenthong pptt on ppttl.phanphoi_tt_id=pptt.id
                    left join loai_ve lv on pptt.loai_ve_id = lv.id
                
                union
                
                select vel.phanphoi_line_id as id, vel.daily_id as daily_id, ve.ky_ve_id as ky_ve_id,-1*vel.thuc_kiem*lv.gia_tri as doanh_thu
                
                    from nhap_ve_e_line vel
                    left join nhap_ve_e ve on vel.nhap_ve_e_id=ve.id
                    left join loai_ve lv on ve.loai_ve_id = lv.id
                )foo
                group by id,daily_id,ky_ve_id
            )
        """)
doanhthu_graph_report()
class dthu_phanh_graph_report(osv.osv):
    _name = "dthu.phanh.graph.report"
    _description = "Báo cáo doanh thu và phát hành cho đại lý"
    _auto = False
    _columns = {
        'daily_id': fields.many2one('dai.ly','Đại lý'),
        'ky_ve_id': fields.many2one('ky.ve','Kỳ vé'),
        'doanh_thu': fields.integer('Doanh Thu'),
        'phathanh': fields.integer('Phat Hanh'),
    }
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'dthu_phanh_graph_report')
        cr.execute("""
            create or replace view dthu_phanh_graph_report as (

                select id, daily_id, ky_ve_id, sum(doanh_thu) as doanh_thu, sum(phathanh) as phathanh
                from
                (
                select ppttl.id as id, ppttl.daily_id as daily_id, pptt.ky_ve_id as ky_ve_id,
                    case when (select sove_sau_dc from dieuchinh_line where phanphoi_line_id=ppttl.id order by id desc limit 1) is not null
                        then (select sove_sau_dc*lv.gia_tri from dieuchinh_line where phanphoi_line_id=ppttl.id order by id desc limit 1) else ppttl.sove_kynay*lv.gia_tri end doanh_thu,
                    case when (select sove_sau_dc from dieuchinh_line where phanphoi_line_id=ppttl.id order by id desc limit 1) is not null
                        then (select sove_sau_dc*lv.gia_tri from dieuchinh_line where phanphoi_line_id=ppttl.id order by id desc limit 1) else ppttl.sove_kynay*lv.gia_tri end phathanh
                    from phanphoi_tt_line ppttl 
                    left join phanphoi_truyenthong pptt on ppttl.phanphoi_tt_id=pptt.id
                    left join loai_ve lv on pptt.loai_ve_id = lv.id
                
                union
                
                select vel.phanphoi_line_id as id, vel.daily_id as daily_id, ve.ky_ve_id as ky_ve_id,-1*vel.thuc_kiem*lv.gia_tri as doanh_thu,0 as phathanh
                
                    from nhap_ve_e_line vel
                    left join nhap_ve_e ve on vel.nhap_ve_e_id=ve.id
                    left join loai_ve lv on ve.loai_ve_id = lv.id
                )foo
                group by id,daily_id,ky_ve_id
            )
        """)
dthu_phanh_graph_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
