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

class danhsach_congno(osv.osv_memory):
    _name = "danhsach.congno"
    
    _columns = {
        'from_date': fields.date('Ngày bắt đầu', required=True),
        'to_date': fields.date('Ngày kết thúc', required=True),
        'partner_ids': fields.many2many('res.partner', 'dscn_doituong_ref', 'dscn_id', 'doituong_id', 'Đối tượng'),
        'doi_xe_ids': fields.many2many('account.account', 'dscn_doixe_ref', 'dscn_id', 'doixe_id', 'Đội xe'),
        'bai_giaoca_ids': fields.many2many('bai.giaoca', 'dscn_baigiaoca_ref', 'dscn_id', 'baigiaoca_id', 'Bãi giao ca'),
        'chinhanh_id': fields.many2one('account.account','Chi nhánh'),
        'chinhanh_ids': fields.many2many('account.account', 'dscn_chinhanh_ref', 'dscn_id', 'chinhanh_id', 'Chi nhánh'),
        'so_hoa_don':fields.char('Số hóa đơn',size = 64),
        'bien_so_xe_ids': fields.many2many('bien.so.xe','dscn_biensoxe_ref', 'dscn_id', 'biensoxe_id','Biển số xe'),
        'loai_bao_hiem_id': fields.many2one('loai.bao.hiem','Loại bảo hiểm'),
        'so_hop_dong': fields.char('Số hợp đồng', size=1024),
        'ma_bang_chiettinh_chiphi_sua': fields.char('Mã chiết tính'),
        'loai_vipham_id': fields.many2one('loai.vi.pham', 'Loại vi phạm'),
        'loai_tamung_id': fields.many2one('loai.tam.ung', 'Loại tạm ứng'),
        'loai_kyquy_id': fields.many2one('loai.ky.quy', 'Loại ký quỹ'),
        'loai_nodoanhthu_id': fields.many2one('loai.no.doanh.thu', 'Loại nợ DT-BH-AL'),
    }
    
    def _get_chinhanh(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.chinhanh_id and user.chinhanh_id.id or False
    
    _defaults = {
        'from_date': time.strftime('%Y-%m-01'),
        'to_date': lambda *a: str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10],
        'chinhanh_id': _get_chinhanh,
    }
    
    def onchange_chinhanh(self, cr, uid, ids, chinhanh_ids=[], context=None):
        domain = {}
        if chinhanh_ids and chinhanh_ids[0] and chinhanh_ids[0][2]:
            domain={
                'doi_xe_ids': [('type','=','other'),('parent_id','child_of',chinhanh_ids[0][2])]
            }
        return {'value': {}, 'domain': domain}
    
    def onchange_doi_xe(self, cr, uid, ids, doi_xe_ids=[], context=None):
        domain = {}
        if doi_xe_ids and doi_xe_ids[0] and doi_xe_ids[0][2]:
            partner_ids = self.pool.get('res.partner').search(cr, uid, [('property_account_receivable','=',doi_xe_ids[0][2])])
            domain={
                'partner_ids': [('customer','=',True),('id','in',partner_ids)],
                'bai_giaoca_ids': [('account_id','child_of',doi_xe_ids[0][2])]
            }
        return {'value': {}, 'domain': domain}
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'danhsach.congno'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        name_report = context['name_report']
        return {'type': 'ir.actions.report.xml', 'report_name': name_report, 'datas': datas}
        
danhsach_congno()

