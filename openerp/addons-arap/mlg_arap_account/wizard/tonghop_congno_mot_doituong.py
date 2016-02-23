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

class tonghop_congno_mot_doituong(osv.osv_memory):
    _name = "tonghop.congno.mot.doituong"
    
    _columns = {
        'period_from_id': fields.many2one('account.period','Từ tháng'),
        'period_to_id': fields.many2one('account.period','Đến tháng'),
        'loai_doituong': fields.selection([('taixe','Lái xe'),
                                           ('nhadautu','Nhà đầu tư'),
                                           ('nhanvienvanphong','Nhân viên văn phòng')], 'Loại đối tượng', required=True),
        'partner_id': fields.many2one('res.partner','Đối tượng', required=True),
        'loai_congno_ids': fields.many2many('loai.cong.no', 'thcnmdt_loaicongno_ref', 'thcnmdt_id', 'loaicongno_id','Công nợ'),
        'chinhanh_id': fields.many2one('account.account','Chi nhánh'),
        'loai_tamung_id': fields.many2one('loai.tam.ung', 'Loại tạm ứng'),
        'loai_nodoanhthu_id': fields.many2one('loai.no.doanh.thu', 'Loại nợ DT-BH-AL'),
        'loai_vipham_id': fields.many2one('loai.vi.pham', 'Loại vi phạm'),
        'loai_baohiem_id': fields.many2one('loai.bao.hiem', 'Loại bảo hiểm'),
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
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        this = self.browse(cr, uid, ids[0])
        if this.period_from_id.id!=this.period_to_id.id and this.period_from_id.date_stop > this.period_to_id.date_start:
            raise osv.except_osv(_('Cảnh báo!'), 'Tháng bắt đầu phải nhỏ hơn tháng kết thúc!')
            
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tonghop.congno.mot.doituong'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        name_report = context['name_report']
        return {'type': 'ir.actions.report.xml', 'report_name': name_report, 'datas': datas}
        
tonghop_congno_mot_doituong()

