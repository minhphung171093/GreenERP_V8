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
        'giatri': fields.float('Doanh thu', digits=(16,0)),
        'ngay_mo_thuong': fields.date('Ngày mở thưởng'),
    }
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'doanhthu_graph_report')
        cr.execute("""
            create or replace view doanhthu_graph_report as (
 
                select id, daily_id, ky_ve_id, sum(giatri) as giatri, ngay_mo_thuong
                from
                (
                select ppttl.id as id, ppttl.daily_id as daily_id, pptt.ky_ve_id as ky_ve_id,
                    case when (select sove_sau_dc from dieuchinh_line where phanphoi_line_id=ppttl.id order by id desc limit 1) is not null
                        then (select sove_sau_dc*lv.gia_tri from dieuchinh_line where phanphoi_line_id=ppttl.id order by id desc limit 1) else ppttl.sove_kynay*lv.gia_tri end giatri,
                    kv.ngay_mo_thuong as ngay_mo_thuong
                    from phanphoi_tt_line ppttl 
                    left join phanphoi_truyenthong pptt on ppttl.phanphoi_tt_id=pptt.id
                    left join loai_ve lv on pptt.loai_ve_id = lv.id
                    left join ky_ve kv on pptt.ky_ve_id = kv.id
                 
                union
                 
                select vel.phanphoi_line_id as id, vel.daily_id as daily_id, ve.ky_ve_id as ky_ve_id,-1*vel.thuc_kiem*lv.gia_tri as giatri, kv.ngay_mo_thuong as ngay_mo_thuong
                 
                    from nhap_ve_e_line vel
                    left join nhap_ve_e ve on vel.nhap_ve_e_id=ve.id
                    left join loai_ve lv on ve.loai_ve_id = lv.id
                    left join ky_ve kv on ve.ky_ve_id = kv.id
                )foo
                group by id,daily_id,ky_ve_id,ngay_mo_thuong
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
        'giatri': fields.float('Giá Trị', digits=(16,0)),
        'loai_giatri': fields.char('Loại'),
    }
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'dthu_phanh_graph_report')
        cr.execute("""
            create or replace view dthu_phanh_graph_report as (

                select id, daily_id, ky_ve_id, sum(giatri) as giatri, loai_giatri
                from
                (
                select ppttl.id as id, ppttl.daily_id as daily_id, pptt.ky_ve_id as ky_ve_id,
                    case when (select sove_sau_dc from dieuchinh_line where phanphoi_line_id=ppttl.id order by id desc limit 1) is not null
                        then (select sove_sau_dc*lv.gia_tri from dieuchinh_line where phanphoi_line_id=ppttl.id order by id desc limit 1) else ppttl.sove_kynay*lv.gia_tri end giatri,
                    
                    'Doanh Thu' as loai_giatri
                    from phanphoi_tt_line ppttl 
                    left join phanphoi_truyenthong pptt on ppttl.phanphoi_tt_id=pptt.id
                    left join loai_ve lv on pptt.loai_ve_id = lv.id
                
                union
                
                select vel.phanphoi_line_id as id, vel.daily_id as daily_id, ve.ky_ve_id as ky_ve_id,-1*vel.thuc_kiem*lv.gia_tri as giatri,'Doanh Thu' as loai_giatri
                
                    from nhap_ve_e_line vel
                    left join nhap_ve_e ve on vel.nhap_ve_e_id=ve.id
                    left join loai_ve lv on ve.loai_ve_id = lv.id

                union

                select ppttl.id as id, ppttl.daily_id as daily_id, pptt.ky_ve_id as ky_ve_id,
                    case when (select sove_sau_dc from dieuchinh_line where phanphoi_line_id=ppttl.id order by id desc limit 1) is not null
                        then (select sove_sau_dc*lv.gia_tri from dieuchinh_line where phanphoi_line_id=ppttl.id order by id desc limit 1) else ppttl.sove_kynay*lv.gia_tri end giatri,
                    'Phát Hành' as loai_giatri
                    from phanphoi_tt_line ppttl 
                    left join phanphoi_truyenthong pptt on ppttl.phanphoi_tt_id=pptt.id
                    left join loai_ve lv on pptt.loai_ve_id = lv.id
                
                )foo
                group by id,daily_id,ky_ve_id,loai_giatri
            )
        """)
dthu_phanh_graph_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
