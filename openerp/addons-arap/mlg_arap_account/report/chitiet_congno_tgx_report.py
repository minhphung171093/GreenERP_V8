# -*- coding: utf-8 -*-
##############################################################################
#
#    HLVSolution, Open Source Management Solution
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
import random
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.tongcongno = 0
        self.localcontext.update({
            'get_doituong': self.get_doituong,
            'convert_date': self.convert_date,
            'get_title_doituong': self.get_title_doituong,
            'get_nodauky': self.get_nodauky,
            'convert_amount': self.convert_amount,
            'get_chitiet_congno': self.get_chitiet_congno,
            'get_title': self.get_title,
            'get_nocuoiky': self.get_nocuoiky,
            'get_tongcongno': self.get_tongcongno,
            'get_from_thang': self.get_from_thang,
            'get_to_thang': self.get_to_thang,
            'get_payment': self.get_payment,
            'get_chinhanh': self.get_chinhanh,
            'get_lichsu_thutienlai': self.get_lichsu_thutienlai,
            'get_bsx': self.get_bsx,
            'get_tonglaithu': self.get_tonglaithu,
            'get_sdtlkdauky': self.get_sdtlkdauky,
            'get_sdtlkcuoiky': self.get_sdtlkcuoiky,
            'get_tongcongno_dathu': self.get_tongcongno_dathu,
        })
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        return ''
    
    def convert_amount(self, amount):
        a = format(int(amount),',')
        return a
    
    def get_from_thang(self):
        wizard_data = self.localcontext['data']['form']
        period_id = wizard_data['period_from_id']
        return period_id and period_id[1] or ''
    
    def get_to_thang(self):
        wizard_data = self.localcontext['data']['form']
        period_id = wizard_data['period_to_id']
        return period_id and period_id[1] or ''
    
    def get_chinhanh(self):
        wizard_data = self.localcontext['data']['form']
        chinhanh_id = wizard_data['chinhanh_id']
        if not chinhanh_id:
            return {'name':'','code':''}
        account = self.pool.get('account.account').browse(self.cr, self.uid, chinhanh_id[0])
        return {'name':account.name,'code':account.code}
    
    def get_doituong(self):
        wizard_data = self.localcontext['data']['form']
        partner_ids = wizard_data['partner_ids']
        if partner_ids:
            return partner_ids
        else:
            period_from_id = wizard_data['period_from_id']
            period_to_id = wizard_data['period_to_id']
            chinhanh_id = wizard_data['chinhanh_id']
            period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
            period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
            mlg_type = wizard_data['mlg_type']
            bien_so_xe_ids = wizard_data['bien_so_xe_ids']
            sql = '''
                select partner_id from account_invoice where date_invoice between '%s' and '%s' and chinhanh_id=%s
                    and state in ('open','paid') and mlg_type='%s' 
            '''%(period_from.date_start,period_to.date_stop,chinhanh_id[0],mlg_type)
            doi_xe_ids = wizard_data['doi_xe_ids']
            if doi_xe_ids:
                doi_xe_ids = str(doi_xe_ids).replace('[', '(')
                doi_xe_ids = str(doi_xe_ids).replace(']', ')')
                sql+='''
                    and account_id in %s 
                '''%(doi_xe_ids)
            bai_giaoca_ids = wizard_data['bai_giaoca_ids']
            if bai_giaoca_ids:
                bai_giaoca_ids = str(bai_giaoca_ids).replace('[', '(')
                bai_giaoca_ids = str(bai_giaoca_ids).replace(']', ')')
                sql+='''
                    and bai_giaoca_id in %s 
                '''%(bai_giaoca_ids)
            if bien_so_xe_ids:
                bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
                bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
                sql+='''
                    and bien_so_xe_id in %s 
                '''%(bien_so_xe_ids)
                
            sql += ''' group by partner_id '''
            self.cr.execute(sql)
            partner_ids = [r[0] for r in self.cr.fetchall()]
            sql = '''
                select partner_id from congno_dauky where period_id=%s
                    and id in (select congno_dauky_id from congno_dauky_line where chinhanh_id=%s and mlg_type='%s')
            '''%(period_from_id[0],chinhanh_id[0],mlg_type)
            self.cr.execute(sql)
            for partner_id in self.cr.fetchall():
                if partner_id[0] not in partner_ids:
                    partner_ids.append(partner_id[0])
            return partner_ids
    
    def get_title(self):
        wizard_data = self.localcontext['data']['form']
        mlg_type = wizard_data['mlg_type']
        tt = ''
        if mlg_type=='no_doanh_thu':
            tt='NỢ DT-BH-AL'
        if mlg_type=='chi_ho_dien_thoai':
            tt='CHI HỘ ĐIỆN THOẠI'
        if mlg_type=='phai_thu_bao_hiem':
            tt='BẢO HIỂM'
        if mlg_type=='phat_vi_pham':
            tt='PHẠT VI PHẠM'
        if mlg_type=='thu_no_xuong':
            tt='NỢ XƯỞNG'
        if mlg_type=='thu_phi_thuong_hieu':
            tt='PHÍ THƯƠNG HIỆU'
        if mlg_type=='tra_gop_xe':
            tt='TRẢ GÓP XE'
        if mlg_type=='hoan_tam_ung':
            tt='TẠM ỨNG'
        if mlg_type=='phai_tra_ky_quy':
            tt='TRẢ KÝ QUỸ'
        if mlg_type=='chi_ho':
            tt='CHI HỘ'
        return tt
    
    def get_title_doituong(self, partner_id):
        if partner_id:
            partner = self.pool.get('res.partner').browse(self.cr, self.uid, partner_id)
            return (partner.ma_doi_tuong or '')+'_'+(partner.name or '')
        return ''
    
    def get_bsx(self, partner_id):
        res = []
        wizard_data = self.localcontext['data']['form']
        if partner_id:
            period_from_id = wizard_data['period_from_id']
            period_to_id = wizard_data['period_to_id']
            period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
            period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
            chinhanh_id = wizard_data['chinhanh_id']
            mlg_type = wizard_data['mlg_type']
            bien_so_xe_ids = wizard_data['bien_so_xe_ids']
            sql = '''
                select id, name from bien_so_xe where id in (
                        select bien_so_xe_id from account_invoice where mlg_type='%s' and partner_id=%s and state in ('open','paid')
                            and chinhanh_id=%s and date_invoice between '%s' and '%s'
                    ) 
            '''%(mlg_type,partner_id,chinhanh_id[0],period_from.date_start,period_to.date_stop)
            
            if bien_so_xe_ids:
                bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
                bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
                sql+='''
                    and id in %s 
                '''%(bien_so_xe_ids)
            
            self.cr.execute(sql)
            return self.cr.dictfetchall()
        return res
    
    def get_nodauky(self, partner_id):
        wizard_data = self.localcontext['data']['form']
        if partner_id:
            period_id = wizard_data['period_from_id']
            period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_id[0])
            chinhanh_id = wizard_data['chinhanh_id']
            mlg_type = wizard_data['mlg_type']
            bien_so_xe_ids = wizard_data['bien_so_xe_ids']
            sql = '''
                select case when sum(COALESCE(residual,0)+COALESCE(sotien_lai_conlai,0))!=0 then sum(COALESCE(residual,0)+COALESCE(sotien_lai_conlai,0)) else 0 end nodauky
                    from account_invoice where mlg_type='%s' and chinhanh_id=%s and partner_id=%s
                        and date_invoice <'%s' and state in ('open','paid') 
            '''%(mlg_type,chinhanh_id[0],partner_id,period_from.date_start)
            if bien_so_xe_ids:
                bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
                bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
                sql+='''
                    and bien_so_xe_id in %s 
                '''%(bien_so_xe_ids)
            self.cr.execute(sql)
            return self.cr.fetchone()[0]
        return 0
    
    def get_tongcongno(self):
        return self.tongcongno
    
    def get_tongcongno_dathu(self):
        wizard_data = self.localcontext['data']['form']
        partner_ids = self.get_doituong()
        if partner_ids:
            partner_ids = str(partner_ids).replace('[', '(')
            partner_ids = str(partner_ids).replace(']', ')')
            
            period_from_id = wizard_data['period_from_id']
            period_to_id = wizard_data['period_to_id']
            period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
            period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
            chinhanh_id = wizard_data['chinhanh_id']
            mlg_type = wizard_data['mlg_type']
            bien_so_xe_ids = wizard_data['bien_so_xe_ids']
            sql = '''
                select case when sum(COALESCE(so_tien,0)-COALESCE(residual,0))!=0
                            then sum(COALESCE(so_tien,0)-COALESCE(residual,0))
                            else 0 end thutrongky
                            
                    from account_invoice where mlg_type='%s' and chinhanh_id=%s and partner_id in %s
                        and date_invoice between '%s' and '%s' and state in ('open','paid') 
            '''%(mlg_type,chinhanh_id[0],partner_ids,period_from.date_start,period_to.date_stop)
            if bien_so_xe_ids:
                bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
                bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
                sql+='''
                    and bien_so_xe_id in %s 
                '''%(bien_so_xe_ids)
            self.cr.execute(sql)
            thutrongky = self.cr.fetchone()[0]
            return thutrongky
        return 0
    
    def get_nocuoiky(self, partner_id):
        wizard_data = self.localcontext['data']['form']
        if partner_id:
            period_from_id = wizard_data['period_from_id']
            period_to_id = wizard_data['period_to_id']
            period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
            period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
            chinhanh_id = wizard_data['chinhanh_id']
            mlg_type = wizard_data['mlg_type']
            bien_so_xe_ids = wizard_data['bien_so_xe_ids']
            sql = '''
                select case when sum(COALESCE(residual,0)+COALESCE(sotien_lai_conlai,0))!=0 then sum(COALESCE(residual,0)+COALESCE(sotien_lai_conlai,0)) else 0 end notrongky
                    from account_invoice where mlg_type='%s' and chinhanh_id=%s and partner_id=%s
                        and date_invoice between '%s' and '%s' and state in ('open','paid') 
            '''%(mlg_type,chinhanh_id[0],partner_id,period_from.date_start,period_to.date_stop)
            if bien_so_xe_ids:
                bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
                bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
                sql+='''
                    and bien_so_xe_id in %s 
                '''%(bien_so_xe_ids)
            self.cr.execute(sql)
            notrongky = self.cr.fetchone()[0]
            nodauky = self.get_nodauky(partner_id)
            nocuoiky = nodauky+notrongky
            self.tongcongno += nocuoiky
            return nocuoiky
        return 0
    
    def get_chitiet_congno(self, partner_id, bsx_id):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        mlg_type = wizard_data['mlg_type']
        sql = '''
            select ai.id as invoice_id,ai.date_invoice as ngay,ai.name as maphieudexuat,rp.ma_doi_tuong as madoituong,rp.name as tendoituong,
                (COALESCE(ai.so_tien,0)+COALESCE(sotien_lai,0)) as no, (COALESCE(ai.so_tien,0)-COALESCE(ai.residual,0)) as co,
                ai.fusion_id as fusion_id,ai.loai_giaodich as loai_giaodich,ai.dien_giai as dien_giai
            
                from account_invoice ai
                left join res_partner rp on rp.id = ai.partner_id
                
                where ai.partner_id=%s and ai.state in ('open','paid') and ai.date_invoice between '%s' and '%s' and ai.chinhanh_id=%s
                    and ai.mlg_type='%s' and ai.bien_so_xe_id=%s
        '''%(partner_id,period_from.date_start,period_to.date_stop,chinhanh_id[0],mlg_type,bsx_id)
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_payment(self, invoice_id):
        if not invoice_id:
            return []
        invoice = self.pool.get('account.invoice').browse(self.cr, self.uid, invoice_id)
        return invoice.payment_ids
    
    def get_lichsu_thutienlai(self, invoice_id):
        if not invoice_id:
            return []
        invoice = self.pool.get('account.invoice').browse(self.cr, self.uid, invoice_id)
        return invoice.lichsu_thutienlai_line
            
    def get_tonglaithu(self):
        partner_ids = self.get_doituong()
        if partner_ids:
            partner_ids = str(partner_ids).replace('[', '(')
            partner_ids = str(partner_ids).replace(']', ')')
            
            wizard_data = self.localcontext['data']['form']
            period_from_id = wizard_data['period_from_id']
            period_to_id = wizard_data['period_to_id']
            period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
            period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
            chinhanh_id = wizard_data['chinhanh_id']
            mlg_type = wizard_data['mlg_type']
            sql = '''
                select case when sum(so_tien)!=0 then sum(so_tien) else 0 end tonglaithu
                    from so_tien_lai where invoice_id in (select id from account_invoice where mlg_type='%s' and chinhanh_id=%s
                        and date_invoice between '%s' and '%s' and state in ('open','paid') and partner_id in %s)
            '''%(mlg_type,chinhanh_id[0],period_from.date_start,period_to.date_stop,partner_ids)
            self.cr.execute(sql)
            return self.cr.fetchone()[0]
        return 0
    
    def get_sdtlkdauky(self, partner_id,bsx_id):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_from = self.pool.get('account.period').browse(self.cr, self.uid, period_from_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        mlg_type = wizard_data['mlg_type']
        sql = '''
            select case when sum(COALESCE(so_tien,0)-COALESCE(residual,0))!=0 then sum(COALESCE(so_tien,0)-COALESCE(residual,0)) else 0 end sdtlkdauky
                from account_invoice where mlg_type='%s' and chinhanh_id=%s
                    and date_invoice < '%s' and state in ('open','paid') and bien_so_xe_id=%s and partner_id=%s
        '''%(mlg_type,chinhanh_id[0],period_from.date_start,bsx_id,partner_id)
        self.cr.execute(sql)
        return self.cr.fetchone()[0]
    
    def get_sdtlkcuoiky(self, partner_id,bsx_id):
        wizard_data = self.localcontext['data']['form']
        period_to_id = wizard_data['period_to_id']
        period_to = self.pool.get('account.period').browse(self.cr, self.uid, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        mlg_type = wizard_data['mlg_type']
        sql = '''
            select case when sum(COALESCE(so_tien,0)-COALESCE(residual,0))!=0 then sum(COALESCE(so_tien,0)-COALESCE(residual,0)) else 0 end sdtlkdauky
                from account_invoice where mlg_type='%s' and chinhanh_id=%s
                    and date_invoice <= '%s' and state in ('open','paid') and bien_so_xe_id=%s and partner_id=%s
        '''%(mlg_type,chinhanh_id[0],period_to.date_stop,bsx_id,partner_id)
        self.cr.execute(sql)
        return self.cr.fetchone()[0]
            
    
    