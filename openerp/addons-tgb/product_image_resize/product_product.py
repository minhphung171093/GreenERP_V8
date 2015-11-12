# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 OpenERP SA (<http://openerp.com>).
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

import math
import re
import time


from openerp import api, tools, SUPERUSER_ID
from openerp.osv import osv, fields, expression
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import psycopg2

import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round, float_compare


class product_product(osv.osv):
    _inherit = 'product.product'

    _columns = {
        'width': fields.integer('Width'),
        'height': fields.integer('Height'),
    }
    
    def change_width_height(self, cr, uid,active_model,id, context=None):
        width = 0
        height = 0
        if id:
            product = self.pool.get(active_model).browse(cr, uid, int(id))
            try:
                if product.width:
                    width = product.width
                if product.height:
                    height = product.height
            except Exception, e:
                pass
        return [width,height]
    
product_product()

class product_template(osv.osv):
    _inherit = 'product.template'


    _columns = {
        'width': fields.integer('Width'),
        'height': fields.integer('Height'),
    }
    
    
product_template()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: