# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import logging
import re

from openerp import tools

from email.header import decode_header
from openerp import SUPERUSER_ID
from openerp.osv import osv, orm, fields
from openerp.tools import html_email_clean
from openerp.tools.translate import _
from HTMLParser import HTMLParser

_logger = logging.getLogger(__name__)

class mail_message(osv.Model):
    _inherit = 'mail.message'
    
    def _get_default_from(self, cr, uid, context=None):
        this = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
        if this.alias_name and this.alias_domain:
            return '%s <%s@%s>' % (this.name, this.alias_name, this.alias_domain)
        elif this.name:
            return '%s' % (this.name)
        raise osv.except_osv(_('Invalid Action!'), _("Unable to send email, please configure the sender's email address or alias."))
    
mail_message()