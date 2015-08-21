# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

import hashlib
import itertools
import logging
import os
import re

from openerp import tools
from openerp.tools.translate import _
from openerp.exceptions import AccessError
from openerp.osv import fields,osv
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)

class ir_attachment(osv.osv):

    _inherit = 'ir.attachment'
    _columns = {
        'vanban_den_id': fields.many2one('vanban.den','Văn bản đến'),
        'vanban_di_id': fields.many2one('vanban.di','Văn bản đi'),
    }
    def create(self, cr, uid, values, context=None):
        self.check(cr, uid, [], mode='write', context=context, values=values)
        if 'file_size' in values:
            del values['file_size']
        if 'vanban_den_id' in values:
            values['res_id'] = values['vanban_den_id']
            values['res_model'] = 'vanban.den'
        if 'vanban_di_id' in values:
            values['res_id'] = values['vanban_di_id']
            values['res_model'] = 'vanban.di'
        return super(ir_attachment, self).create(cr, uid, values, context)
ir_attachment
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
