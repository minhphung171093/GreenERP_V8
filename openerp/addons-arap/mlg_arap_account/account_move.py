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
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class account_move_line(osv.osv):
    _inherit = "account.move.line"
    
    def _get_thu_chi(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for line in self.browse(cr, uid, ids):
            if line.mlg_type in ['chi_no_doanh_thu','chi_dien_thoai','chi_bao_hiem','phai_tra_ky_quy','tam_ung','chi_ho']:
                result[line.id] = 'Chi'
            else:
                result[line.id] = 'Thu'
        return result
    
    def _get_con_lai(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for line in self.browse(cr, uid, ids):
            result[line.id] = line.debit - line.credit
        return result
    
    _columns = {
        'bai_giaoca_id': fields.many2one('bai.giaoca', 'Bãi giao ca'),
        'mlg_type': fields.selection([('no_doanh_thu','Nợ DT-BH-AL'),
                                      ('chi_ho_dien_thoai','Chi hộ điện thoại'),
                                      ('phai_thu_bao_hiem','Phải thu bảo hiểm'),
                                      ('phai_thu_ky_quy','Phải thu ký quỹ'),
                                      ('phat_vi_pham','Phạt vi phạm'),
                                      ('thu_no_xuong','Thu nợ xưởng'),
                                      ('thu_phi_thuong_hieu','Thu phí thương hiệu'),
                                      ('tra_gop_xe','Trả góp xe'),
                                      ('hoan_tam_ung','Hoàn tạm ứng'),
                                      ('chi_no_doanh_thu','Chi nợ doanh thu'),
                                      ('chi_dien_thoai','Chi điện thoại'),
                                      ('chi_bao_hiem','Chi bảo hiểm'),
                                      ('phai_tra_ky_quy','Phải trả ký quỹ'),
                                      ('tam_ung','Tạm ứng'),
                                      ('chi_ho','Chi hộ'),],'Loại công nợ'),
        'thu_chi': fields.function(_get_thu_chi,type='char', string='Thu/Chi', store=True),
        'con_lai': fields.function(_get_con_lai,type='float', string='Còn lại', store=True),
        'fusion_id': fields.char('Fusion Thu', size=1024),
        'loai_giaodich': fields.char('Loại giao dịch', size=1024),
        'sotienlai_line': fields.one2many('so.tien.lai', 'move_line_id', 'So tien lai line')
    }
    
account_move_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
