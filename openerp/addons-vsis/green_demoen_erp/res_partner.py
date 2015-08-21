# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from datetime import datetime

class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'street_2': fields.char('Street', size=128),
        'street2_2': fields.char('Street2', size=128),
        'zip_2': fields.char('Zip', change_default=True, size=24),
        'city_2': fields.char('City', size=128),
        'state_id_2': fields.many2one("res.country.state", 'State'),
        'country_id_2': fields.many2one('res.country', 'Country'),
    }
     
res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
