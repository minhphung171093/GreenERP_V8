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

from openerp import addons
import logging
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import tools

_logger = logging.getLogger(__name__)

class vanban_di(osv.osv):
    _name = "vanban.di"
    _description = "Van ban di"
    _columns = {
        'nguoi_tao_id': fields.many2one('hr.employee','Người tạo', readonly=True),
        'loai_vanban_id': fields.many2one('loai.vanban','Loại văn bản', required=True),
        'nguoi_ky_vb_id': fields.many2one('hr.employee','Người ký văn bản', required=True),
        'chuc_vu_id': fields.many2one('hr.employee.category','Chức vụ'),
        'ma_hoso': fields.char('Mã hồ sơ', size=64),
        'trich_yeu_noidung': fields.text('Trích yếu nội dung', required=True),
        'thuoc_phongban_id': fields.many2one('hr.department','Thuộc phòng ban'),
        'do_mat_id': fields.many2one('do.mat','Độ mật', required=True),
        'do_khan_id': fields.many2one('do.khan','Độ khẩn', required=True),
        'can_phuc_dap': fields.boolean('Cần phúc đáp'),
        'so_to': fields.integer('Số tờ'),
        'hoso_lines': fields.one2many('ir.attachment','vanban_di_id','Tập tin đính kèm'),
        'state': fields.selection([('moitao','Mới Tạo'),('dangxuly','Đang xử lý'),('daxuly','Đã xử lý')], 'Tình trạng'),
    }
    
    def _get_nguoi_tao_id(self, cr, uid, context=None):
        employee_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)], context=context)
        if not employee_ids:
            raise osv.except_osv(_('Cảnh báo!'),
                        _('Vui lòng tạo thông tin người dùng!'))
        return employee_ids and employee_ids[0] or False
    
    _defaults = {
        'state': 'moitao',
        'nguoi_tao_id': _get_nguoi_tao_id,
    }
    
vanban_di()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
