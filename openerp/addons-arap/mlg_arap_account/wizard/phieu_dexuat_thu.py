# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class phieu_de_xuat(osv.osv_memory):
    _name = "phieu.de.xuat"
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(phieu_de_xuat, self).default_get(cr, uid, fields, context=context)
        if context.get('active_id', False) and context.get('active_model')=='account.invoice':
            invoice_obj = self.pool.get('account.invoice')
            invoice = invoice_obj.browse(cr, uid, context['active_id'])
            res.update({'so_tien': invoice.residual,
                        'partner_id': invoice.partner_id.id,
                        'loai_doituong': invoice.loai_doituong,
                        'mlg_type': invoice.mlg_type,
                        })
            if context.get('default_loai', False) and context['default_loai']=='chi':
                res.update({'so_tien': invoice.so_tien,'diengiai':invoice.dien_giai})
        if context.get('active_id', False) and context.get('active_model')=='thu.ky.quy':
            kyquy_obj = self.pool.get('thu.ky.quy')
            kyquy = kyquy_obj.browse(cr, uid, context['active_id'])
            res.update({'so_tien': kyquy.so_tien,
                        'partner_id': kyquy.partner_id.id,
                        'loai_doituong': kyquy.loai_doituong,
                        })    
        return res
    
    _columns = {
        'so_tien': fields.float('Số tiền',digits=(16,0), required=True),
        'phuongthuc_thanhtoan': fields.selection([('tienmat','Tiền mặt'),('nganhang','Ngân hàng')],'Phương thức thanh toán', required=True),
        'partner_id': fields.many2one('res.partner','Đối tượng'),
        'ngay': fields.date('Ngày'),
        'diengiai': fields.char('Diễn giải', size=1024),
        'loai_doituong': fields.selection([('taixe','Lái xe'),('nhadautu','Nhà đầu tư'),('nhanvienvanphong','Nhân viên văn phòng')],'Loại đối tượng'),
        'mlg_type': fields.selection([('no_doanh_thu','Nợ doanh thu'),
                                      ('chi_ho_dien_thoai','Chi hộ điện thoại'),
                                      ('phai_thu_bao_hiem','Phải thu bảo hiểm'),
                                      ('phai_thu_ky_quy','Phải thu ký quỹ'),
                                      ('phat_vi_pham','Phạt vi phạm'),
                                      ('thu_no_xuong','Thu nợ xưởng'),
                                      ('thu_phi_thuong_hieu','Thu phí thương hiệu'),
                                      ('tra_gop_xe','Trả góp xe'),
                                      ('hoan_tam_ung','Hoàn tạm ứng'),
                                      ('chi_no_doanh_thu','Chi nợ doanh thu'),
                                      ('chi_dien_thoai','Chi điện thoại'),
                                      ('chi_bao_hiem','Chi bảo hiểm'),
                                      ('phai_tra_ky_quy','Phải trả ký quỹ'),
                                      ('tam_ung','Tạm ứng'),
                                      ('chi_ho','Chi hộ'),],'Loại công nợ'),
        'loai': fields.selection([('thu','Thu'),('chi','Chi')],'Loại'),
    }
    
    _defaults = {
        'phuongthuc_thanhtoan': 'tienmat',
        'ngay': time.strftime('%Y-%m-%d'),
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'account.invoice'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        if context.get('mlg_type', False) and context.get('loai_doituong', False):
            report_name = 'pdxt_'+context['mlg_type']+'_'+context['loai_doituong']
            if context['mlg_type']=='chi_ho':
                report_name = 'pdxt_chi_ho'
        return {'type': 'ir.actions.report.xml', 'report_name': report_name, 'datas': datas}
    
    def print_thukyquy_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'thu.ky.quy'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        if context.get('loai_doituong', False):
            report_name = 'pdxt_kyquy_'+context['loai_doituong']
        return {'type': 'ir.actions.report.xml', 'report_name': report_name, 'datas': datas}
        
phieu_de_xuat()

