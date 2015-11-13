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
from openerp.addons.web import http as openerpweb


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
#     
#     @openerpweb.httprequest
#     def index(self, req, data, token):
#         data = json.loads(data)
#         model = data.get('model', [])
#         columns_headers = data.get('headers', [])
#         rows = data.get('rows', [])
# 
#         return req.make_response(
#             self.from_data(columns_headers, rows),
#             headers=[
#                 ('Content-Disposition', 'attachment; filename="%s"'
#                     % self.filename(model)),
#                 ('Content-Type', self.content_type)
#             ],
#             cookies={'fileToken': token}
#         )
    
    def cover_print(self, cr, uid, model, record, report_name, report_filename, report_extention, context=None):
        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('name','=',report_name)])
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            report_service = 'report.' + report.report_name
            service = netsvc.LocalService(report_service)
            result = False
            try:
                (result, format) = service.create(cr, uid, [record.id], {'model': model}, context=context)
            except:
                pass
            if result:
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', ' ', report_filename)
                    file_name += report_extention
                    return {
                        'db_datas': result,
                        'datas_fname': file_name,
                    }
        return {'db_datas': False,
                'datas_fname': False}
    
product_product()

class product_template(osv.osv):
    _inherit = 'product.template'


    _columns = {
        'width': fields.integer('Width', required=False),
        'height': fields.integer('Height', required=False),
    }
    
    
product_template()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: