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
        kq = False
        noidung_loi=''
        date_now = time.strftime('%Y-%m-%d')
        try:
            kq_obj = self.pool.get('chinhanhline.biensoxe.kyquybddh')
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
                    select id from chinhanhline_biensoxe_kyquybddh where kich_hoat=True
                        and (ngaychay_cuoi is null or (ngaychay_cuoi is not null and '%s'::date-ngaychay_cuoi::date>=%s))
                        and chinhanhline_id in (select id from chi_nhanh_line where partner_id in (select id from res_partner where nhadautu=True))
                '''%(date_now,line['name']*30)
                cr.execute(sql)
                kq_ids = [r[0] for r in cr.fetchall()]
                for kq in kq_obj.browse(cr, uid, kq_ids):
                    sotien_dathu = kq.sotien_dathu
                    if sotien_dathu>=line['so_tien']:
#                         vals={
#                             'chinhanh_id': kq.chinhanhline_id.chinhanh_id.id,
#                             'loai_doituong': 'nhadautu',
#                             'partner_id': kq.chinhanhline_id.partner_id.id,
#                             'so_tien': line['so_tien'],
#                             'ngay_thu': date_now,
#                             'loai_kyquy_id': loai_kq_ids[0],
#                             'bien_so_xe_id': kq.bien_so_xe_id.id,
#                         }
#                         kyquy_obj.create(cr, uid, vals) #Chờ xác nhận thông tin sẽ tạo cái gì?

                        sotien_cantru = line['so_tien']
                        sql = '''
                            select id, sotien_conlai
                                from thu_ky_quy
                                
                                where sotien_conlai>0 and chinhanh_id=%s and partner_id=%s and state='paid' and bien_so_xe_id=%s
                                
                                order by ngay_thu,id
                        '''%(kq.chinhanhline_id.chinhanh_id.id,kq.chinhanhline_id.partner_id.id,kq.bien_so_xe_id.id)
                        cr.execute(sql)
                        for kyquy in cr.dictfetchall():
                            if not sotien_cantru:
                                break
                            if sotien_cantru<kyquy['sotien_conlai']:
                                kyquy_obj.write(cr, uid, [kyquy['id']],{'sotien_conlai':kyquy['sotien_conlai']-sotien_cantru})
                                sotien_cantru = 0
                            else:
                                kyquy_obj.write(cr, uid, [kyquy['id']],{'sotien_conlai':0})
                                sotien_cantru = sotien_cantru-kyquy['sotien_conlai']

                        lichsu_obj.create(cr, uid, {
                            'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'partner_id': kq.chinhanhline_id.partner_id.id,
                            'chinhanh_id': kq.chinhanhline_id.chinhanh_id.id,
                            'bien_so_xe_id': kq.bien_so_xe_id.id,
                            'trang_thai': 'Thành công',
                            'noidung_loi': '',
                        })
                        sotien_dathu=sotien_dathu-line['so_tien']
                        kq_obj.write(cr, uid, [kq.id], {'ngaychay_cuoi':date_now})
                        if not sotien_dathu:
                            sotien_dathu = 0
#                             kq_obj.write(cr, uid, [kq.id], {'kich_hoat':False}) #nếu cấn trừ hết thì có inactive biển số xe đó k?
                            
                    else:
                        noidung_loi = 'Số tiền đã thu của biển số xe "%s" không đủ'%(kq.bien_so_xe_id.name)
                        raise osv.except_osv(_('Cảnh báo!'), 'Số tiền đã thu của biển số xe "%s" không đủ'%(kq.bien_so_xe_id.name))
        except Exception, e:
            cr.rollback()
            if not noidung_loi:
                noidung_loi = str(e).replace("'","''")
            lichsu_obj.create(cr, uid, {
                'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                'partner_id': kq and kq.chinhanhline_id.partner_id.id or False,
                'chinhanh_id': kq and kq.chinhanhline_id.chinhanh_id.id or False,
                'bien_so_xe_id': kq and kq.bien_so_xe_id.id or False,
                'trang_thai': 'Lỗi',
                'noidung_loi': noidung_loi,
            })
            body='''
                <p>Ngày: %s</p>
                <p>Nhà đầu tư: %s</p>
                <p>Chi nhánh: %s</p>
                <p>Biển số xe: %s</p>
                <p>Ghi chú: %s</p>
            '''%(time.strftime('%d/%m/%Y'),kq and kq.chinhanhline_id.partner_id.name or '',kq and kq.chinhanhline_id.chinhanh_id.name or '',kq and kq.bien_so_xe_id.name or '',noidung_loi)
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
            cr.commit()
        return True
    
cauhinh_kyquy_bddh()

class thu_ky_quy(osv.osv):
    _inherit = "thu.ky.quy"
    
    def bt_thu(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            if line.bien_so_xe_id.id:
                sql = '''
                    select id,kich_hoat,chinhanhline_id from chinhanhline_biensoxe_kyquybddh where bien_so_xe_id=%s
                        and chinhanhline_id in (select id from chi_nhanh_line where chinhanh_id=%s and partner_id=%s) limit 1
                '''%(line.bien_so_xe_id.id,line.chinhanh_id.id,line.partner_id.id)
                cr.execute(sql)
                kq = cr.fetchone()
                kq_obj = self.pool.get('chinhanhline.biensoxe.kyquybddh')
                if kq:
                    if not kq[1]:
                        kq_obj.write(cr, uid, [kq[0]], {'kich_hoat':True})
                else:
                    sql = '''
                        select id from chi_nhanh_line where chinhanh_id=%s and partner_id=%s limit 1
                    '''%(line.chinhanh_id.id,line.partner_id.id)
                    cr.execute(sql)
                    chinhanhline_ids = [r[0] for r in cr.fetchall()]
                    if chinhanhline_ids:
                        kq_obj.create(cr, uid, {'bien_so_xe_id': line.bien_so_xe_id.id,'chinhanhline_id': chinhanhline_ids[0],'kich_hoat':True})
        return super(thu_ky_quy, self).bt_thu(cr, uid, ids, context)
    
thu_ky_quy()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
