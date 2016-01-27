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
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class congno_dauky(osv.osv):
    _name = "congno.dauky"
    
    _columns = {
        'period_id': fields.many2one('account.period','Tháng', readonly=False),
        'partner_id': fields.many2one('res.partner','Đối tượng', readonly=False),
        'congno_dauky_line': fields.one2many('congno.dauky.line', 'congno_dauky_id','Chi tiết công nợ'),
    }
    
    def get_congno_dauky(self, cr, uid, context=None):
        try:
            date_now = datetime.now() + timedelta(hours=7)
            end_of_month = str(date_now + relativedelta(months=+1, day=1, days=-1))[:10]
            date_now_str = date_now.strftime('%Y-%m-%d')
            day = int(end_of_month[8:10])-int(date_now_str[8:10])+3
            next_month = date_now + timedelta(days=day)
            next_month_str = next_month.strftime('%Y-%m-%d')
            sql = '''
                select id,date_start,date_stop from account_period
                    where '%s' between date_start and date_stop and special != 't' limit 1 
            '''%(next_month_str)
            cr.execute(sql)
            period = cr.dictfetchone()
            sql = '''
                select partner_id
                    
                    from account_invoice
                    
                    where state='open'
                    
                    group by partner_id
            '''
            cr.execute(sql)
            for partner in cr.dictfetchall():
                sql = '''
                    select sum(COALESCE(residual,0) + COALESCE(sotien_lai_conlai,0)) as so_tien_no,mlg_type,chinhanh_id
                        
                        from account_invoice
                        
                        where state='open' and partner_id=%s 
                        
                        group by chinhanh_id,mlg_type
                '''%(partner['partner_id'])
                cr.execute(sql)
                congno_dauky_line = []
                for invoice in cr.dictfetchall():
                    chitiet_loai_line = []
                    if invoice['mlg_type']=='no_doanh_thu':
                        sql = '''
                            select sum(COALESCE(residual,0) + COALESCE(sotien_lai_conlai,0)) as so_tien_no,loai_nodoanhthu_id
                                from account_invoice
                                where state='open' and partner_id=%s and mlg_type='%s' and chinhanh_id=%s
                                group by loai_nodoanhthu_id
                        '''%(partner['partner_id'],invoice['mlg_type'],invoice['chinhanh_id'])
                        cr.execute(sql)
                        for line in cr.dictfetchall():
                            chitiet_loai_line.append((0,0,{
                                'loai_id': line['loai_nodoanhthu_id'],
                                'so_tien_no': line['so_tien_no'],
                            }))
                    if invoice['mlg_type']=='phai_thu_bao_hiem':
                        sql = '''
                            select sum(COALESCE(residual,0) + COALESCE(sotien_lai_conlai,0)) as so_tien_no,loai_baohiem_id
                                from account_invoice
                                where state='open' and partner_id=%s and mlg_type='%s' and chinhanh_id=%s
                                group by loai_baohiem_id
                        '''%(partner['partner_id'],invoice['mlg_type'],invoice['chinhanh_id'])
                        cr.execute(sql)
                        for line in cr.dictfetchall():
                            chitiet_loai_line.append((0,0,{
                                'loai_id': line['loai_baohiem_id'],
                                'so_tien_no': line['so_tien_no'],
                            }))
                    if invoice['mlg_type']=='phat_vi_pham':
                        sql = '''
                            select sum(COALESCE(residual,0) + COALESCE(sotien_lai_conlai,0)) as so_tien_no,loai_vipham_id
                                from account_invoice
                                where state='open' and partner_id=%s and mlg_type='%s' and chinhanh_id=%s
                                group by loai_vipham_id
                        '''%(partner['partner_id'],invoice['mlg_type'],invoice['chinhanh_id'])
                        cr.execute(sql)
                        for line in cr.dictfetchall():
                            chitiet_loai_line.append((0,0,{
                                'loai_id': line['loai_vipham_id'],
                                'so_tien_no': line['so_tien_no'],
                            }))
                    if invoice['mlg_type']=='hoan_tam_ung':
                        sql = '''
                            select sum(COALESCE(residual,0) + COALESCE(sotien_lai_conlai,0)) as so_tien_no,loai_tamung_id
                                from account_invoice
                                where state='open' and partner_id=%s and mlg_type='%s' and chinhanh_id=%s
                                group by loai_tamung_id
                        '''%(partner['partner_id'],invoice['mlg_type'],invoice['chinhanh_id'])
                        cr.execute(sql)
                        for line in cr.dictfetchall():
                            chitiet_loai_line.append((0,0,{
                                'loai_id': line['loai_tamung_id'],
                                'so_tien_no': line['so_tien_no'],
                            }))
                    congno_dauky_line.append((0,0,{
                        'chinhanh_id': invoice['chinhanh_id'],
                        'mlg_type': invoice['mlg_type'],
#                         'bien_so_xe_id': invoice['bien_so_xe_id'],
#                         'so_hop_dong': invoice['so_hop_dong'],
#                         'so_hoa_don': invoice['so_hoa_don'],
#                         'ma_bang_chiettinh_chiphi_sua': invoice['ma_bang_chiettinh_chiphi_sua'],
                        'so_tien_no': invoice['so_tien_no'],
                        'chitiet_loai_line': chitiet_loai_line,
                    }))
                self.create(cr, uid, {
                    'period_id': period['id'],
                    'partner_id': partner['partner_id'],
                    'congno_dauky_line': congno_dauky_line,               
                })
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        return True
    
congno_dauky()
    
class congno_dauky_line(osv.osv):
    _name = "congno.dauky.line"
    
    _columns = {
        'congno_dauky_id': fields.many2one('congno.dauky','Công nợ đầu kỳ', ondelete='cascade'),
        'chinhanh_id': fields.many2one('account.account', 'Chi nhánh'),
#         'so_hop_dong': fields.char('Số hợp đồng', size=1024),
#         'so_hoa_don': fields.char('Số hóa đơn', size=1024),
#         'ma_bang_chiettinh_chiphi_sua': fields.char('Mã chiết tính', size=1024),
#         'bien_so_xe_id': fields.many2one('bien.so.xe','Biển số xe'),
        'mlg_type': fields.selection([
                                      ('no_doanh_thu','Nợ DT-BH-AL'),
                                      ('chi_ho_dien_thoai','Phải thu chi hộ điện thoại'),
                                      ('phai_thu_bao_hiem','Phải thu bảo hiểm'),
                                      ('phai_thu_ky_quy','Phải thu ký quỹ'),
                                      ('phat_vi_pham','Phạt vi phạm'),
                                      ('thu_no_xuong','Thu nợ xưởng'),
                                      ('thu_phi_thuong_hieu','Thu phí thương hiệu'),
                                      ('tra_gop_xe','Trả góp xe'),
                                      ('hoan_tam_ung','Phải thu tạm ứng'),
                                      ('chi_no_doanh_thu','Chi nợ doanh thu'),
                                      ('chi_dien_thoai','Chi điện thoại'),
                                      ('chi_bao_hiem','Chi bảo hiểm'),
                                      ('phai_tra_ky_quy','Phải trả ký quỹ'),
                                      ('tam_ung','Tạm ứng'),
                                      ('chi_ho','Chi hộ')
                                      ],'Loại công nợ'),
        'so_tien_no': fields.float('Số tiền nợ',digits=(16,0)),
        'chitiet_loai_line': fields.one2many('chitiet.congno.dauky.line', 'congno_dauky_line_id', 'Chi tiết')
    }
congno_dauky_line()

class chitiet_congno_dauky_line(osv.osv):
    _name = "chitiet.congno.dauky.line"
    
    def _get_tenloai(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = ''
            if line.congno_dauky_line_id.mlg_type=='no_doanh_thu' and line.loai_id:
                obj = self.pool.get('loai.no.doanh.thu')
                loai = obj.browse(cr, uid, line.loai_id)
                res[line.id] = loai.name
            if line.congno_dauky_line_id.mlg_type=='phai_thu_bao_hiem' and line.loai_id:
                obj = self.pool.get('loai.bao.hiem')
                loai = obj.browse(cr, uid, line.loai_id)
                res[line.id] = loai.name
            if line.congno_dauky_line_id.mlg_type=='phat_vi_pham' and line.loai_id:
                obj = self.pool.get('loai.vi.pham')
                loai = obj.browse(cr, uid, line.loai_id)
                res[line.id] = loai.name
            if line.congno_dauky_line_id.mlg_type=='hoan_tam_ung' and line.loai_id:
                obj = self.pool.get('loai.tam.ung')
                loai = obj.browse(cr, uid, line.loai_id)
                res[line.id] = loai.name
        return res
    
    _columns = {
        'congno_dauky_line_id': fields.many2one('congno.dauky.line','Công nợ đầu kỳ line', ondelete='cascade'),
        'so_tien_no': fields.float('Số tiền nợ',digits=(16,0)),
        'loai_id': fields.integer('Loại id'),
        'loai': fields.function(_get_tenloai, string='Loại', type='char'),
    }
chitiet_congno_dauky_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
