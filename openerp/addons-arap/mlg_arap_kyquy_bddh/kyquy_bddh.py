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

import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression
from openerp.tools.translate import _
import time
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import netsvc
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class cauhinh_kyquy_bddh(osv.osv):
    _name = "cauhinh.kyquy.bddh"
    
    _columns = {
        'name': fields.integer('Số tháng', required=True),
        'so_tien': fields.integer('Số tiền', digits=(16,0), required=True),
    }
    
    def send_mail(self, cr, uid, lead_email, msg_id,context=None):
        mail_message_pool = self.pool.get('mail.message')
        mail_mail = self.pool.get('mail.mail')
        msg = mail_message_pool.browse(cr, SUPERUSER_ID, msg_id, context=context)
        body_html = msg.body
        # email_from: partner-user alias or partner email or mail.message email_from
        if msg.author_id and msg.author_id.user_ids and msg.author_id.user_ids[0].alias_domain and msg.author_id.user_ids[0].alias_name:
            email_from = '%s <%s@%s>' % (msg.author_id.name, msg.author_id.user_ids[0].alias_name, msg.author_id.user_ids[0].alias_domain)
        elif msg.author_id:
            email_from = '%s <%s>' % (msg.author_id.name, msg.author_id.email)
        else:
            email_from = msg.email_from

        references = False
        if msg.parent_id:
            references = msg.parent_id.message_id

        mail_values = {
            'mail_message_id': msg.id,
            'auto_delete': True,
            'body_html': body_html,
            'email_from': email_from,
            'email_to' : lead_email,
            'references': references,
        }
        email_notif_id = mail_mail.create(cr, uid, mail_values, context=context)
        try:
             mail_mail.send(cr, uid, [email_notif_id], context=context)
        except Exception:
            a = 1
        return True
    
    def tinh_kyquy_bddh(self, cr, uid, context=None):
        lichsu_obj = self.pool.get('lichsu.kyquy.bddh')
        try:
            noidung_loi=''
            date_now = time.strftime('%Y-%m-%d')
            chinhanhline_obj = self.pool.get('chi.nhanh.line')
            kyquy_obj = self.pool.get('thu.ky.quy')
            sql = '''
                select id from loai_ky_quy where upper(code)='KY_QUY_DH_BD' limit 1
            '''
            cr.execute(sql)
            loai_kq_ids = [r[0] for r in cr.fetchall()]
            sql = '''
                select name,so_tien from cauhinh_kyquy_bddh limit 1
            '''
            cr.execute(sql)
            for line in cr.dictfetchall():
                sql = '''
                    select id
                        
                        from chi_nhanh_line
                        
                        where (ngaychay_cuoi is null or (ngaychay_cuoi is not null and '%s'::date-ngaychay_cuoi::date>=%s))
                            and partner_id in (select id from res_partner where nhadautu=True)
                            and id in (select chinhanhline_id from chinhanhline_biensoxe_ref)
                '''%(date_now,line['name']*30)
                cr.execute(sql)
                chinhanh_line_ids = [r[0] for r in cr.fetchall()]
                for chinhanhline in chinhanhline_obj.browse(cr, uid, chinhanh_line_ids):
                    sotien_conlai = chinhanhline.sotien_conlai
                    kyquy_vals = []
                    bien_so_xe_ids = [r.id for r in chinhanhline.bien_so_xe_ids]
                    for bsx in bien_so_xe_ids:
                        if sotien_conlai>=line['so_tien']:
                            kyquy_vals.append({
                                'chinhanh_id': chinhanhline.chinhanh_id.id,
                                'loai_doituong': 'nhadautu',
                                'partner_id': chinhanhline.partner_id.id,
                                'so_tien': line['so_tien'],
                                'ngay_thu': date_now,
                                'loai_kyquy_id': loai_kq_ids[0],
                                'bien_so_xe_id': bsx,
                            })
                            sotien_conlai=sotien_conlai-line['so_tien']
                        else:
                            sotien_conlai=-1
                    if sotien_conlai>=0:
                        for vals in kyquy_vals:
                            kyquy_obj.create(cr, uid, vals)
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'partner_id': chinhanhline.partner_id.id,
                            'chinhanh_id': chinhanhline.chinhanh_id.id,
                            'bien_so_xe_ids': [(6,0,bien_so_xe_ids)],
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                    else:
                        noidung_loi = 'Số tiền còn lại không đủ để tạo phải thu ký quỹ cho các biển số xe này'
                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'partner_id': chinhanhline.partner_id.id,
                            'chinhanh_id': chinhanhline.chinhanh_id.id,
                            'bien_so_xe_ids': [(6,0,bien_so_xe_ids)],
                            'trang_thai': 'Lỗi',
                            'noidung_loi': noidung_loi,
                        })
                        biensoxe = [r.name for r in chinhanhline.bien_so_xe_ids]
                        biensoxe = str(biensoxe)
                        biensoxe = biensoxe.replace('[','')
                        biensoxe = biensoxe.replace(']','')
                        body='''
                            <p>Ngày: %s</p>
                            <p>Nhà đầu tư: %s</p>
                            <p>Chi nhánh: %s</p>
                            <p>Biển số xe: %s</p>
                            <p>Ghi chú: %s</p>
                        '''%(ngay,chinhanhline.partner_id.name,biensoxe,chinhanhline.chinhanh_id.name,noidung_loi)
                        user = self.pool.get('res.users').browse(cr, 1, 1)
                        partner = user.partner_id
                        partner.signup_prepare()
                        post_values = {
                            'subject': 'Lỗi chạy ký quỹ BĐĐH tự động',
                            'body': body,
                            'partner_ids': [],
                            }
                        lead_email = partner.email
                        msg_id = self.pool.get('res.partner').message_post(cr, uid, [partner.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, lead_email, msg_id, context)
        except Exception, e:
            cr.rollback()
            noidung_loi = str(e).replace("'","''")
            lichsu_obj.create(cr, uid, {
                'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                'partner_id': False,
                'chinhanh_id': False,
                'bien_so_xe_ids': False,
                'trang_thai': 'Lỗi',
                'noidung_loi': noidung_loi,
            })
            cr.commit()
        return True
    
cauhinh_kyquy_bddh()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
