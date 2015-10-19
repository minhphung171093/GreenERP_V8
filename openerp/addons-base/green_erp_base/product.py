# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
import time
DATE_FORMAT = "%Y-%m-%d"
from openerp import SUPERUSER_ID

import os
from openerp import modules


class product_product(osv.osv):
    _inherit = "product.product"
    
    _columns = {
        'account_deducted_id': fields.many2one('account.account', 'Deducted Account'),
    }
    
product_product()

class product_category(osv.osv):
    _inherit = "product.category"
    
    _columns = {
        'account_deducted_id': fields.many2one('account.account', 'Deducted Account'),
    }
    
product_category()

class bang_tam_init(osv.osv):
    _name = 'bang.tam.init'

    _columns = {
        'name': fields.char('Ten OBJ', size=1024),
        'da_chay': fields.boolean('Đã chạy'),
    }
bang_tam_init()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: