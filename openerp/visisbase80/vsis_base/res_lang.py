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

from openerp.osv import fields, osv
from openerp.tools.translate import _

class res_lang(osv.osv):
    _inherit = "res.lang"
    _columns = {
    }
    def init(self, cr):
        lang_ids = self.search(cr, 1, [('code','in',['vi_VN','en_US'])])
        if lang_ids:
            sql = '''
            UPDATE res_lang
            SET grouping = '[3,3,3,3,3]', date_format = '%d/%m/%Y'
            '''
            where = ' WHERE id in (%s)'%(','.join(map(str, lang_ids)))
            cr.execute(sql + where)
res_lang()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
