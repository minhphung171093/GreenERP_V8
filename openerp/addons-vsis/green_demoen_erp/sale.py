# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from datetime import datetime

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    _columns = {
        'product_category_id': fields.many2one('product.category','Subtitle',required=True),
    }
     
sale_order_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
