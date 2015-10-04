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

class res_partner(osv.osv):
    _inherit = 'res.partner'

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(res_partner, self).default_get(cr, uid, fields, context=context)
        if context.get('loai_doituong', False):
            sql = '''
                select res_id from ir_model_data where module='mlg_arap_account' and name='%s'
            '''%(context['loai_doituong'])
            cr.execute(sql)
            loai = cr.fetchone()
            if loai:
                res.update({'loai_doituong_id': loai[0]})
        return res

    _columns = {
        'property_account_payable': fields.property(
            type='many2one',
            relation='account.account',
            string="Account Payable",
            domain="[('type', '=', 'payable')]",
            help="This account will be used instead of the default one as the payable account for the current partner",
            required=False),
        'bai_giaoca_id': fields.many2one('bai.giaoca', 'Bãi giao ca'),
        'loai_doituong_id': fields.many2one('loai.doi.tuong', 'Loại đối tượng'),
        'ma_doi_tuong': fields.char('Mã đối tượng', size=1024),
        'bien_so_xe': fields.char('Biển số xe', size=1024),
        'loai_doituong': fields.related('loai_doituong_id', 'name', type='char', string='Loại đối tượng', readonly=True, store=True),
    }
    
res_partner()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
