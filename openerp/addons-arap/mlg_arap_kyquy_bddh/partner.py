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

from operator import itemgetter
import time

from openerp.osv import fields, osv
from openerp import api
from openerp.tools.translate import _
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class chi_nhanh_line(osv.osv):
    _inherit = 'chi.nhanh.line'

    _columns = {
        'kyquybddh_line': fields.one2many('chinhanhline.biensoxe.kyquybddh', 'chinhanhline_id','Danh sách biển số xe'),
    }
    
chi_nhanh_line()

class chinhanhline_biensoxe_kyquybddh(osv.osv):
    _name = 'chinhanhline.biensoxe.kyquybddh'
    
    def _get_sotien(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for kq in self.browse(cr, uid, ids, context=context):
            res[kq.id] = {
                'sotien_dathu': 0,
            }
            sql = '''
                select case when sum(sotien_conlai)!=0 then sum(sotien_conlai) else 0 end sotien
                    from thu_ky_quy
                    where partner_id=%s and chinhanh_id=%s and state='paid' and bien_so_xe_id=%s
            '''%(kq.chinhanhline_id.partner_id.id,kq.chinhanhline_id.chinhanh_id.id,kq.bien_so_xe_id.id)
            cr.execute(sql)
            res[kq.id]['sotien_dathu'] = cr.fetchone()[0]
        return res
    
    def _get_chi_nhanh_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('chi.nhanh.line').browse(cr, uid, ids, context=context):
            for kq in line.kyquybddh_line:
                result[kq.id] = True
        return result.keys()
    
    def _get_thu_kyquy(self, cr, uid, ids, context=None):
        result = {}
        chinhanhline_obj = self.pool.get('chi.nhanh.line')
        for line in self.pool.get('thu.ky.quy').browse(cr, uid, ids, context=context):
            chinhanhline_ids = chinhanhline_obj.search(cr, uid, [('chinhanh_id','=',line.chinhanh_id.id),('partner_id','=',line.partner_id.id)])
            for chinhanhline in chinhanhline_obj.browse(cr, uid, chinhanhline_ids):
                for kq in chinhanhline.kyquybddh_line:
                    result[kq.id] = True
        return result.keys()
    
    _columns = {
        'chinhanhline_id': fields.many2one('chi.nhanh.line', 'Chi nhánh line', ondelete='cascade'),
        'bien_so_xe_id': fields.many2one('bien.so.xe', 'Biển số xe'),
        'ngaychay_cuoi': fields.date('Ngày chạy cuối'),
        'kich_hoat': fields.boolean('Kích hoạt'),
        'sotien_dathu': fields.function(_get_sotien, string='Số tiền đã thu', multi='sotien',
            store={
                'chinhanhline.biensoxe.kyquybddh': (lambda self, cr, uid, ids, c={}: ids, ['bien_so_xe_id','ngaychay_cuoi','kich_hoat'], 10),
                'chi.nhanh.line': (_get_chi_nhanh_line, ['sotien_phaithu','sotien_phaithu_dinhky'], 10),
                'thu.ky.quy': (_get_thu_kyquy, ['state', 'so_tien', 'partner_id','chinhanh_id','sotien_conlai'], 10),
            },type='float',digits=(16,0)),
    }
    
    _defaults = {
        'kich_hoat': True,
    }
    
chinhanhline_biensoxe_kyquybddh()

class lichsu_kyquy_bddh(osv.osv):
    _name = "lichsu.kyquy.bddh"
    _order = 'name desc'
    _columns = {
        'name': fields.datetime('Ngày'),
        'partner_id': fields.many2one('res.partner', 'Nhà đầu tư'),
        'chinhanh_id': fields.many2one('account.account', 'Chi nhánh'),
        'bien_so_xe_id': fields.many2one('bien.so.xe', 'Biển số xe'),
        'trang_thai': fields.text('Trạng thái'),
        'noidung_loi': fields.text('Ghi chú'),
    }
lichsu_kyquy_bddh()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
