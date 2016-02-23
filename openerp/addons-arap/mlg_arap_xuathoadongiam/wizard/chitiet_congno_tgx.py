# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class chitiet_congno_tgx_tattoan(osv.osv_memory):
    _name = "chitiet.congno.tgx.tattoan"
    
    _columns = {
        'period_from_id': fields.many2one('account.period','Từ tháng'),
        'period_to_id': fields.many2one('account.period','Đến tháng'),
        'partner_ids': fields.many2many('res.partner', 'ctcntgxtt_doituong_ref', 'dscn_id', 'doituong_id', 'Đối tượng'),
        'doi_xe_ids': fields.many2many('account.account', 'ctcntgxtt_doixe_ref', 'dscn_id', 'doixe_id', 'Đội xe'),
        'bai_giaoca_ids': fields.many2many('bai.giaoca', 'ctcntgxtt_baigiaoca_ref', 'dscn_id', 'baigiaoca_id', 'Bãi giao ca'),
        'bien_so_xe_ids': fields.many2many('bien.so.xe','ctcntgxtt_biensoxe_ref', 'dscn_id', 'biensoxe_id','Biển số xe'),
        'chinhanh_id': fields.many2one('account.account','Chi nhánh'),
        'mlg_type': fields.selection([('no_doanh_thu','Nợ DT-BH-AL'),
                                      ('chi_ho_dien_thoai','Phải thu chi hộ điện thoại'),
                                      ('phai_thu_bao_hiem','Phải thu bảo hiểm'),
                                      ('phat_vi_pham','Phạt vi phạm'),
                                      ('thu_no_xuong','Thu nợ xưởng'),
                                      ('thu_phi_thuong_hieu','Thu phí thương hiệu'),
                                      ('tra_gop_xe','Trả góp xe'),
                                      ('hoan_tam_ung','Phải thu tạm ứng'),
                                      ],'Loại công nợ'),
        'tat_toan': fields.boolean('Đã xuất hóa đơn'),
    }
    
    def _get_chinhanh(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.chinhanh_id and user.chinhanh_id.id or False
    
    def _get_period(self, cr, uid, context=None):
        date_now = time.strftime('%Y-%m-%d')
        sql = '''
            select id,date_start,date_stop from account_period
                where '%s' between date_start and date_stop and special != 't' limit 1 
        '''%(date_now)
        cr.execute(sql)
        period = cr.fetchone()
        return period and period[0] or False
    
    _defaults = {
        'chinhanh_id': _get_chinhanh,
        'period_from_id': _get_period,
        'period_to_id': _get_period,
        'mlg_type': 'tra_gop_xe',
    }
    
    def onchange_doi_xe(self, cr, uid, ids, doi_xe_ids=[], context=None):
        domain = {}
        if doi_xe_ids and doi_xe_ids[0] and doi_xe_ids[0][2]:
            partner_ids = self.pool.get('res.partner').search(cr, uid, [('property_account_receivable','=',doi_xe_ids[0][2])])
            domain={
                'partner_ids': [('customer','=',True),('id','in',partner_ids)],
                'bai_giaoca_ids': [('account_id','child_of',doi_xe_ids[0][2])]
            }
        return {'value': {}, 'domain': domain}
    
    def onchange_bai_giaoca(self, cr, uid, ids, bai_giaoca_ids=[], context=None):
        domain = {}
        if bai_giaoca_ids and bai_giaoca_ids[0] and bai_giaoca_ids[0][2]:
            partner_ids = self.pool.get('res.partner').search(cr, uid, [('bai_giaoca_id','=',bai_giaoca_ids[0][2])])
            domain={
                'partner_ids': [('customer','=',True),('id','in',partner_ids)],
            }
        return {'value': {}, 'domain': domain}
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])
        if this.period_from_id.id!=this.period_to_id.id and this.period_from_id.date_stop > this.period_to_id.date_start:
            raise osv.except_osv(_('Cảnh báo!'), 'Tháng bắt đầu phải nhỏ hơn tháng kết thúc!')
        
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'chitiet.congno.tgx.tattoan'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        name_report = context['name_report']
        return {'type': 'ir.actions.report.xml', 'report_name': name_report, 'datas': datas}
        
chitiet_congno_tgx_tattoan()

