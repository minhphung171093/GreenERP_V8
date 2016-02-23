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
class lichsu_inphieu(osv.osv):
    _name = "lichsu.inphieu"
    _order = 'name desc'
    _columns = {
        'name': fields.text('Ma phiếu'),
        'chinhanh_id': fields.many2one('account.account','Chi nhánh', readonly=False),
        'date_print': fields.datetime('Ngày'),
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
                                      ('chi_ho','Chi hộ'),],'Loại công nợ', readonly=True),
        'create_user_id': fields.many2one('res.users','User'),
        'so_tien': fields.float('Số tiền',digits=(16,0)),
    }
lichsu_inphieu()