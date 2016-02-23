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
        'bien_so_xe_ids': fields.many2many('bien.so.xe', 'partner_biensoxe_ref', 'partner_id', 'bsx_id','Biển số xe'),
    }
    
chi_nhanh_line()

class lichsu_kyquy_bddh(osv.osv):
    _name = 'lichsu.kyquy.bddh'
    _order = 'name desc'
    
    _columns = {
        'name': fields.date('Ngày chạy'),
        'chinhanh_line_id': fields.many2one('chi.nhanh.line','Chi nhánh line'),
        'bien_so_xe_id': fields.many2one('bien.so.xe', 'Biển số xe'),
    }
    
lichsu_kyquy_bddh()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
