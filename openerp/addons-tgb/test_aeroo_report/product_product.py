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

    def _get_image_variant(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = obj.image_variant or getattr(obj.product_tmpl_id, name)
        return result

    def _set_image_variant(self, cr, uid, id, name, value, args, context=None):
        product = self.browse(cr, uid, id, context=context)
        if product.width and product.height:
            image = tools.image_resize_image_big(value,size=(product.width,product.height))
        else:
            image = tools.image_resize_image_big(value)
        
        if product.product_tmpl_id.image:
            product.image_variant = image
        else:
            product.product_tmpl_id.image = image

    _columns = {
        'image_variant': fields.binary("Variant Image",
            help="This field holds the image used as image for the product variant, limited to 1024x1024px."),

        'image': fields.function(_get_image_variant, fnct_inv=_set_image_variant,
            string="Big-sized image", type="binary",
            help="Image of the product variant (Big-sized image of product template if false). It is automatically "\
                 "resized as a 1024x1024px image, with aspect ratio preserved."),
        'image_small': fields.function(_get_image_variant, fnct_inv=_set_image_variant,
            string="Small-sized image", type="binary",
            help="Image of the product variant (Small-sized image of product template if false)."),
        'image_medium': fields.function(_get_image_variant, fnct_inv=_set_image_variant,
            string="Medium-sized image", type="binary",
            help="Image of the product variant (Medium-sized image of product template if false)."),
        'width': fields.integer('Width'),
        'height': fields.integer('Height'),
    }
    
    def change_width_height(self, cr, uid, id, context=None):
        width = 0
        height = 0
        if id:
            product = self.browse(cr, uid, int(id))
            if product.width:
                width = product.width
            if product.height:
                height = product.height
        return [width,height]
    
product_product()

class product_template(osv.osv):
    _inherit = 'product.template'


    _columns = {
        'width': fields.integer('Width', required=False),
        'height': fields.integer('Height', required=False),
    }
    
    
product_template()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: