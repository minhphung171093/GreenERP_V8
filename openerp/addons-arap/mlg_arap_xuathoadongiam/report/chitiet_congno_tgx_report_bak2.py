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
        self.nocuoiky = 0
        self.tongsdtlkck = 0
        self.tonglaithu = 0
        self.tongthu = 0
        self.bsx_ids = []
        
        self.partner_ids = []
        self.ndk_dict = {}
        self.bsx_dict = {}
        self.ctcn_dict = {}
        self.nck_dict = {}
        self.sdtlkdauky_dict = {}
        self.sdtlkcuoiky_dict = {}
        
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
            'get_only_payment': self.get_only_payment,
            'get_only_lichsu_thutienlai': self.get_only_lichsu_thutienlai,
            'get_lai_co': self.get_lai_co,
            'get_name_invoice': self.get_name_invoice,
            'get_only_pay_sotienlai': self.get_only_pay_sotienlai,
            'get_chusohuu': self.get_chusohuu,
            'get_tsdtlkcuoiky': self.get_tsdtlkcuoiky,
            'get_khoitao': self.get_khoitao,
        })
        
    def get_khoitao(self):
        self.get_doituong_data()
        self.get_nodauky_data()
        self.get_bsx_data()
        self.get_chitiet_congno_data()
        self.get_nocuoiky_data()
        self.get_sdtlkdauky_data()
        self.get_sdtlkcuoiky_data()
        return True
        
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
        account = self.pool.get('account.account').browse(self.cr, 1, chinhanh_id[0])
        return {'name':account.name,'code':account.code}
    
    def get_tsdtlkcuoiky(self):
        tongsdtlkck = self.tongsdtlkck
        self.tongsdtlkck = 0
        return tongsdtlkck
    
    def get_chusohuu(self):
        wizard_data = self.localcontext['data']['form']
        chusohuu_id = wizard_data['chusohuu_id']
        if chusohuu_id:
            return 'Chủ sở hữu: '+chusohuu_id[1]
        else:
            return ''
    
    def get_doituong(self):
        return self.partner_ids
    
    def get_doituong_data(self):
        wizard_data = self.localcontext['data']['form']
        partner_ids = wizard_data['partner_ids']
        if partner_ids:
            return partner_ids
        else:
            period_from_id = wizard_data['period_from_id']
            period_to_id = wizard_data['period_to_id']
            chinhanh_id = wizard_data['chinhanh_id']
            period_from = self.pool.get('account.period').browse(self.cr, 1, period_from_id[0])
            period_to = self.pool.get('account.period').browse(self.cr, 1, period_to_id[0])
            mlg_type = wizard_data['mlg_type']
            tat_toan = wizard_data['tat_toan']
            bien_so_xe_ids = wizard_data['bien_so_xe_ids']
            chusohuu_id = wizard_data['chusohuu_id']
            
            if not tat_toan:
                sql_partner = 'select partner_id '
                sql_bsx = 'select bien_so_xe_id '
                sql = '''
                    from account_invoice where date_invoice between '%s' and '%s' and chinhanh_id=%s
                        and state in ('open','paid') and mlg_type='%s' 
                        and (ngay_tat_toan is null or (ngay_tat_toan is not null and '%s'<ngay_tat_toan)) 
                '''%(period_from.date_start,period_to.date_stop,chinhanh_id[0],mlg_type,period_to.date_stop)
                
            else:
                sql = '''
                    select partner_id from account_invoice where chinhanh_id=%s
                        and state in ('open','paid') and mlg_type='%s' 
                '''%(chinhanh_id[0],mlg_type)
                
                sql +='''
                    and tat_toan=True and ngay_tat_toan between '%s' and '%s'  
                '''%(period_from.date_start,period_to.date_stop)
                
            if chusohuu_id:
                sql += '''
                    and thu_cho_doituong_id=%s 
                '''%(chusohuu_id[0])
                
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
                
            partner_ids = []
            if not tat_toan:
                sql_bsx = sql_bsx+sql+ ''' group by bien_so_xe_id '''
                self.cr.execute(sql_bsx)
                self.bsx_ids = [r[0] for r in self.cr.fetchall()]
                sql = sql_partner+sql
                sql_old_partner = '''
                    select partner_id from account_invoice where date_invoice<'%s' and bien_so_xe_id in (
                '''%(period_from.date_start)+sql_bsx+')'
                self.cr.execute(sql_old_partner)
                partners = self.cr.fetchall()
                for partner_id in partners:
                    if partner_id[0] not in partner_ids:
                        partner_ids.append(partner_id[0])
                        
                sql_2 = '''
                select partner_id, bien_so_xe_id,invoice_name, sum(sotien) from (
                    select partner_id, bien_so_xe_id,name as invoice_name, 
                        case when sum(COALESCE(so_tien,0)+COALESCE(sotien_lai,0))!=0 then sum(COALESCE(so_tien,0)+COALESCE(sotien_lai,0)) else 0 end sotien
                        from account_invoice where date_invoice<'%s' and state in ('open','paid') and mlg_type='%s' 
                            and (ngay_tat_toan is null or (ngay_tat_toan is not null and '%s'<ngay_tat_toan)) 
                        '''%(period_from.date_start,mlg_type,period_to.date_stop)
                if chusohuu_id:
                    sql_2 += '''
                        and thu_cho_doituong_id=%s 
                    '''%(chusohuu_id[0])
                    
                doi_xe_ids = wizard_data['doi_xe_ids']
                if doi_xe_ids:
                    doi_xe_ids = str(doi_xe_ids).replace('[', '(')
                    doi_xe_ids = str(doi_xe_ids).replace(']', ')')
                    sql_2+='''
                        and account_id in %s 
                    '''%(doi_xe_ids)
                bai_giaoca_ids = wizard_data['bai_giaoca_ids']
                if bai_giaoca_ids:
                    bai_giaoca_ids = str(bai_giaoca_ids).replace('[', '(')
                    bai_giaoca_ids = str(bai_giaoca_ids).replace(']', ')')
                    sql_2+='''
                        and bai_giaoca_id in %s 
                    '''%(bai_giaoca_ids)
                if bien_so_xe_ids:
                    bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
                    bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
                    sql_2+='''
                        and bien_so_xe_id in %s 
                    '''%(bien_so_xe_ids)
                sql_2 += ' group by partner_id,bien_so_xe_id,name '
                sql_2 += '''
                    union
                    select ai.partner_id as partner_id, ai.bien_so_xe_id as bien_so_xe_id,ai.name as invoice_name,
                            case when sum(COALESCE(aml.credit,0))!=0 then -1*sum(COALESCE(aml.credit,0)) else 0 end sotien
                        from account_move_line aml
                        left join account_voucher av on aml.move_id=aml.move_id
                        left join account_invoice ai on av.reference=ai.name
                        where ai.state in ('open','paid') and ai.date_invoice<'%s' and ai.mlg_type='%s' 
                            and (ai.ngay_tat_toan is null or (ai.ngay_tat_toan is not null and '%s'<ai.ngay_tat_toan)) and aml.date<'%s'  
                '''%(period_from.date_start,mlg_type,period_to.date_stop,period_from.date_start)
                if chusohuu_id:
                    sql_2 += '''
                        and ai.thu_cho_doituong_id=%s 
                    '''%(chusohuu_id[0])
                    
                doi_xe_ids = wizard_data['doi_xe_ids']
                if doi_xe_ids:
                    doi_xe_ids = str(doi_xe_ids).replace('[', '(')
                    doi_xe_ids = str(doi_xe_ids).replace(']', ')')
                    sql_2+='''
                        and ai.account_id in %s 
                    '''%(doi_xe_ids)
                bai_giaoca_ids = wizard_data['bai_giaoca_ids']
                if bai_giaoca_ids:
                    bai_giaoca_ids = str(bai_giaoca_ids).replace('[', '(')
                    bai_giaoca_ids = str(bai_giaoca_ids).replace(']', ')')
                    sql_2+='''
                        and ai.bai_giaoca_id in %s 
                    '''%(bai_giaoca_ids)
                if bien_so_xe_ids:
                    bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
                    bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
                    sql_2+='''
                        and ai.bien_so_xe_id in %s 
                    '''%(bien_so_xe_ids)
                sql_2 += ' group by ai.partner_id,ai.bien_so_xe_id,ai.name '
                sql_2 += '''
                    union
                    select ai.partner_id as partner_id, ai.bien_so_xe_id as bien_so_xe_id,ai.name as invoice_name,
                            case when sum(COALESCE(stl.so_tien,0))!=0 then -1*sum(COALESCE(stl.so_tien,0)) else 0 end sotien
                        from so_tien_lai stl
                        left join account_invoice ai on stl.invoice_id=ai.id
                        where ai.state in ('open','paid') and ai.date_invoice<'%s' and ai.mlg_type='%s' 
                            and (ai.ngay_tat_toan is null or (ai.ngay_tat_toan is not null and '%s'<ai.ngay_tat_toan)) and stl.ngay<'%s' 
                '''%(period_from.date_start,mlg_type,period_to.date_stop,period_from.date_start)
                if chusohuu_id:
                    sql_2 += '''
                        and ai.thu_cho_doituong_id=%s 
                    '''%(chusohuu_id[0])
                    
                doi_xe_ids = wizard_data['doi_xe_ids']
                if doi_xe_ids:
                    doi_xe_ids = str(doi_xe_ids).replace('[', '(')
                    doi_xe_ids = str(doi_xe_ids).replace(']', ')')
                    sql_2+='''
                        and ai.account_id in %s 
                    '''%(doi_xe_ids)
                bai_giaoca_ids = wizard_data['bai_giaoca_ids']
                if bai_giaoca_ids:
                    bai_giaoca_ids = str(bai_giaoca_ids).replace('[', '(')
                    bai_giaoca_ids = str(bai_giaoca_ids).replace(']', ')')
                    sql_2+='''
                        and ai.bai_giaoca_id in %s 
                    '''%(bai_giaoca_ids)
                if bien_so_xe_ids:
                    bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
                    bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
                    sql_2+='''
                        and ai.bien_so_xe_id in %s 
                    '''%(bien_so_xe_ids)
                sql_2 += ' group by ai.partner_id,ai.bien_so_xe_id,ai.name )foo group by partner_id, bien_so_xe_id,invoice_name having sum(sotien)>0 '
                self.cr.execute(sql_2)
                partners = self.cr.dictfetchall()
                for partner_id in partners:
                    if partner_id['partner_id'] not in partner_ids:
                        partner_ids.append(partner_id['partner_id'])
            
            sql += ''' group by partner_id '''
            self.cr.execute(sql)
            for partner_id in self.cr.fetchall():
                if partner_id[0] not in partner_ids:
                    partner_ids.append(partner_id[0])
            sql = '''
                select partner_id from congno_dauky where period_id=%s
                    and id in (select congno_dauky_id from congno_dauky_line where chinhanh_id=%s and mlg_type='%s')
            '''%(period_from_id[0],chinhanh_id[0],mlg_type)
            self.cr.execute(sql)
            for partner_id in self.cr.fetchall():
                if partner_id[0] not in partner_ids:
                    partner_ids.append(partner_id[0])
            self.partner_ids = partner_ids
            return True
    
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
            partner = self.pool.get('res.partner').browse(self.cr, 1, partner_id)
            return (partner.ma_doi_tuong or '')+'_'+(partner.name or '')
        return ''
    
    def get_bsx(self, partner_id):
        if self.bsx_dict.get(partner_id, False):
            return self.bsx_dict[partner_id]
        return []
    
    def get_bsx_data(self):
        res = []
        wizard_data = self.localcontext['data']['form']
        if self.partner_ids:
            p_ids = self.partner_ids
            p_ids = str(p_ids).replace('[', '(')
            p_ids = str(p_ids).replace(']', ')')
            
            period_from_id = wizard_data['period_from_id']
            period_to_id = wizard_data['period_to_id']
            period_from = self.pool.get('account.period').browse(self.cr, 1, period_from_id[0])
            period_to = self.pool.get('account.period').browse(self.cr, 1, period_to_id[0])
            chinhanh_id = wizard_data['chinhanh_id']
            mlg_type = wizard_data['mlg_type']
            tat_toan = wizard_data['tat_toan']
            bien_so_xe_ids = wizard_data['bien_so_xe_ids']
            chusohuu_id = wizard_data['chusohuu_id']
            sql_bsx = '''
                select ai.partner_id as partner_id, bsx.id as id, bsx.name as name
                    from bien_so_xe bsx
                    left join account_invoice ai on bsx.id=ai.bien_so_xe_id
                    
                    where ai.mlg_type='%s' and ai.partner_id in %s and ai.state in ('open','paid')
                            and ai.chinhanh_id=%s 
            '''%(mlg_type,p_ids,chinhanh_id[0])
            
            sql_bsx_only_pay = '''
                select ai.partner_id as partner_id, bsx.id as id, bsx.name as name
                    from bien_so_xe bsx
                    left join account_invoice ai on bsx.id=ai.bien_so_xe_id
                    left join account_voucher av on ai.name=av.reference
                    left join account_move_line aml on aml.move_id=av.move_id
                    
                    where ai.mlg_type='%s' and ai.partner_id in %s and ai.state in ('open','paid')
                            and ai.chinhanh_id=%s and aml.date between '%s' and '%s' 
            '''%(mlg_type,p_ids,chinhanh_id[0],period_from.date_start,period_to.date_stop)
            
            sql_bsx_only_lai = '''
                select ai.partner_id as partner_id, bsx.id as id, bsx.name as name
                    from bien_so_xe bsx
                    left join account_invoice ai on bsx.id=ai.bien_so_xe_id
                    left join so_tien_lai stl on stl.invoice_id=ai.id
                    
                    where ai.mlg_type='%s' and ai.partner_id in %s and ai.state in ('open','paid')
                            and ai.chinhanh_id=%s and stl.ngay between '%s' and '%s' 
            '''%(mlg_type,p_ids,chinhanh_id[0],period_from.date_start,period_to.date_stop)
            
            if chusohuu_id:
                sql_bsx += '''
                    and ai.thu_cho_doituong_id=%s 
                '''%(chusohuu_id[0])
                
                sql_bsx_only_pay += '''
                    and ai.thu_cho_doituong_id=%s 
                '''%(chusohuu_id[0])
                
                sql_bsx_only_lai += '''
                    and ai.thu_cho_doituong_id=%s 
                '''%(chusohuu_id[0])
            if not tat_toan:
                sql_bsx +='''
                    and (ai.ngay_tat_toan is null or (ai.ngay_tat_toan is not null and '%s'<ai.ngay_tat_toan)) and ai.date_invoice between '%s' and '%s'  
                '''%(period_to.date_stop,period_from.date_start,period_to.date_stop)
                
                sql_bsx_only_pay +='''
                    and (ai.ngay_tat_toan is null or (ai.ngay_tat_toan is not null and '%s'<ai.ngay_tat_toan)) and ai.date_invoice <= '%s'  
                '''%(period_to.date_stop,period_to.date_stop)
                
                sql_bsx_only_lai +='''
                    and (ai.ngay_tat_toan is null or (ai.ngay_tat_toan is not null and '%s'<ai.ngay_tat_toan)) and ai.date_invoice <= '%s'  
                '''%(period_to.date_stop,period_to.date_stop)
            else:
                sql_bsx +='''
                    and ai.tat_toan=True and ai.ngay_tat_toan between '%s' and '%s' 
                '''%(period_from.date_start,period_to.date_stop)
                
                sql_bsx_only_pay +='''
                    and ai.tat_toan=True and ai.ngay_tat_toan between '%s' and '%s' 
                '''%(period_from.date_start,period_to.date_stop)
                
                sql_bsx_only_lai +='''
                    and ai.tat_toan=True and ai.ngay_tat_toan between '%s' and '%s' 
                '''%(period_from.date_start,period_to.date_stop)
            if bien_so_xe_ids:
                bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
                bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
                sql_bsx+='''
                    and bsx.id in %s 
                '''%(bien_so_xe_ids)
                
                sql_bsx_only_pay+='''
                    and bsx.id in %s 
                '''%(bien_so_xe_ids)
                
                sql_bsx_only_lai+='''
                    and bsx.id in %s 
                '''%(bien_so_xe_ids)
            
            sql_bsx += ''' group by ai.partner_id, bsx.id, bsx.name '''
                
            sql_bsx_only_pay += ''' group by ai.partner_id, bsx.id, bsx.name '''
            
            sql_bsx_only_lai += ''' group by ai.partner_id, bsx.id, bsx.name '''
            
            sql_tong_bsx = '''
                select partner_id, id, name from (
            '''+sql_bsx+' union '+sql_bsx_only_pay+' union '+sql_bsx_only_lai+' )bsxtong group by partner_id, id, name'
            self.cr.execute(sql_tong_bsx)
            self.bsx_ids += [r['id'] for r in self.cr.dictfetchall()]
            
            sql_2 = ''
            if not tat_toan:
                sql_2 = '''
                    select ai.partner_id as partner_id, bsx.id as id, bsx.name as name
                        from bien_so_xe bsx
                        left join account_invoice ai on bsx.id=ai.bien_so_xe_id
                        
                        where ai.date_invoice<'%s' 
                '''%(period_from.date_start)
                if chusohuu_id:
                    sql_2 += '''
                        and ai.thu_cho_doituong_id=%s 
                    '''%(chusohuu_id[0])
                if self.bsx_ids:
                    b_ids = self.bsx_ids
                    b_ids = str(b_ids).replace('[', '(')
                    b_ids = str(b_ids).replace(']', ')')
                    sql_2+='''
                        and ai.bien_so_xe_id in %s 
                    '''%(b_ids)
                if bien_so_xe_ids:
                    bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
                    bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
                    sql_2+='''
                        and bsx.id in %s 
                    '''%(bien_so_xe_ids)
                sql_2 += '''
                    group by ai.partner_id, bsx.id, bsx.name
                '''
                    
                sql_3 = '''
                select partner_id, id, name from (
                select partner_id, id, name, invoice_name, sum(sotien) from (
                    select ai.partner_id as partner_id, bsx.id as id, bsx.name as name,ai.name as invoice_name,
                        case when sum(COALESCE(ai.so_tien,0)+COALESCE(ai.sotien_lai,0))!=0 then sum(COALESCE(ai.so_tien,0)+COALESCE(ai.sotien_lai,0)) else 0 end sotien
                        from account_invoice ai
                            left join bien_so_xe bsx on bsx.id=ai.bien_so_xe_id
                        where ai.date_invoice<'%s' and ai.state in ('open','paid') and ai.mlg_type='%s' 
                            and (ai.ngay_tat_toan is null or (ai.ngay_tat_toan is not null and '%s'<ai.ngay_tat_toan)) 
                        '''%(period_from.date_start,mlg_type,period_to.date_stop)
                if chusohuu_id:
                    sql_3 += '''
                        and ai.thu_cho_doituong_id=%s 
                    '''%(chusohuu_id[0])
                    
                doi_xe_ids = wizard_data['doi_xe_ids']
                if doi_xe_ids:
                    doi_xe_ids = str(doi_xe_ids).replace('[', '(')
                    doi_xe_ids = str(doi_xe_ids).replace(']', ')')
                    sql_3+='''
                        and ai.account_id in %s 
                    '''%(doi_xe_ids)
                bai_giaoca_ids = wizard_data['bai_giaoca_ids']
                if bai_giaoca_ids:
                    bai_giaoca_ids = str(bai_giaoca_ids).replace('[', '(')
                    bai_giaoca_ids = str(bai_giaoca_ids).replace(']', ')')
                    sql_3+='''
                        and ai.bai_giaoca_id in %s 
                    '''%(bai_giaoca_ids)
                if bien_so_xe_ids:
                    bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
                    bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
                    sql_3+='''
                        and ai.bien_so_xe_id in %s 
                    '''%(bien_so_xe_ids)
                sql_3 += ' group by ai.partner_id, bsx.id, bsx.name,ai.name '
                sql_3 += '''
                    union
                    select ai.partner_id as partner_id, bsx.id as id, bsx.name as name,ai.name as invoice_name,
                            case when sum(COALESCE(aml.credit,0))!=0 then -1*sum(COALESCE(aml.credit,0)) else 0 end sotien
                        from account_move_line aml
                        left join account_voucher av on aml.move_id=aml.move_id
                        left join account_invoice ai on av.reference=ai.name
                        left join bien_so_xe bsx on bsx.id=ai.bien_so_xe_id 
                        where ai.state in ('open','paid') and ai.date_invoice<'%s' and ai.mlg_type='%s' 
                            and (ai.ngay_tat_toan is null or (ai.ngay_tat_toan is not null and '%s'<ai.ngay_tat_toan)) and aml.date<'%s'  
                '''%(period_from.date_start,mlg_type,period_to.date_stop,period_from.date_start)
                if chusohuu_id:
                    sql_3 += '''
                        and ai.thu_cho_doituong_id=%s 
                    '''%(chusohuu_id[0])
                    
                doi_xe_ids = wizard_data['doi_xe_ids']
                if doi_xe_ids:
                    doi_xe_ids = str(doi_xe_ids).replace('[', '(')
                    doi_xe_ids = str(doi_xe_ids).replace(']', ')')
                    sql_3+='''
                        and ai.account_id in %s 
                    '''%(doi_xe_ids)
                bai_giaoca_ids = wizard_data['bai_giaoca_ids']
                if bai_giaoca_ids:
                    bai_giaoca_ids = str(bai_giaoca_ids).replace('[', '(')
                    bai_giaoca_ids = str(bai_giaoca_ids).replace(']', ')')
                    sql_3+='''
                        and ai.bai_giaoca_id in %s 
                    '''%(bai_giaoca_ids)
                if bien_so_xe_ids:
                    bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
                    bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
                    sql_3+='''
                        and ai.bien_so_xe_id in %s 
                    '''%(bien_so_xe_ids)
                sql_3 += ' group by ai.partner_id,bsx.id, bsx.name,ai.name '
                sql_3 += '''
                    union
                    select ai.partner_id as partner_id, bsx.id as id, bsx.name as name,ai.name as invoice_name,
                            case when sum(COALESCE(stl.so_tien,0))!=0 then -1*sum(COALESCE(stl.so_tien,0)) else 0 end sotien
                        from so_tien_lai stl
                        left join account_invoice ai on stl.invoice_id=ai.id
                        left join bien_so_xe bsx on bsx.id=ai.bien_so_xe_id 
                        where ai.state in ('open','paid') and ai.date_invoice<'%s' and ai.mlg_type='%s' 
                            and (ai.ngay_tat_toan is null or (ai.ngay_tat_toan is not null and '%s'<ai.ngay_tat_toan)) and stl.ngay<'%s' 
                '''%(period_from.date_start,mlg_type,period_to.date_stop,period_from.date_start)
                if chusohuu_id:
                    sql_3 += '''
                        and ai.thu_cho_doituong_id=%s 
                    '''%(chusohuu_id[0])
                    
                doi_xe_ids = wizard_data['doi_xe_ids']
                if doi_xe_ids:
                    doi_xe_ids = str(doi_xe_ids).replace('[', '(')
                    doi_xe_ids = str(doi_xe_ids).replace(']', ')')
                    sql_3+='''
                        and ai.account_id in %s 
                    '''%(doi_xe_ids)
                bai_giaoca_ids = wizard_data['bai_giaoca_ids']
                if bai_giaoca_ids:
                    bai_giaoca_ids = str(bai_giaoca_ids).replace('[', '(')
                    bai_giaoca_ids = str(bai_giaoca_ids).replace(']', ')')
                    sql_3+='''
                        and ai.bai_giaoca_id in %s 
                    '''%(bai_giaoca_ids)
                if bien_so_xe_ids:
                    bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
                    bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
                    sql_3+='''
                        and ai.bien_so_xe_id in %s 
                    '''%(bien_so_xe_ids)
                sql_3 += ' group by ai.partner_id,bsx.id, bsx.name,ai.name )foo3 group by partner_id, id, name,invoice_name having sum(sotien)>0 )foo4  '
                    
            if sql_2:
                sql_tong_bsx = '''
                    select partner_id, id, name from (
                '''+sql_tong_bsx+''' 
                    union 
                '''+sql_2+' union '+sql_3+ ')foo'
            print 'TONG',sql_tong_bsx
            print 'SQL3',sql_3
            self.cr.execute(sql_tong_bsx)
            bsxs = self.cr.dictfetchall()
            for bsx in bsxs:
                if bsx['id'] not in self.bsx_ids:
                    self.bsx_ids.append(bsx['id'])
                if self.bsx_dict.get(bsx['partner_id'], False):
                    self.bsx_dict[bsx['partner_id']].append({'id': bsx['id'], 'name': bsx['name']})
                else:
                    self.bsx_dict[bsx['partner_id']] = [{'id': bsx['id'], 'name': bsx['name']}]
            return True
        return True
    
    def get_nodauky(self, partner_id):
        if self.ndk_dict.get(partner_id,False):
            nodauky = self.ndk_dict[partner_id]
            return nodauky
        return 0
    
    def get_nodauky_data(self):
        wizard_data = self.localcontext['data']['form']
        period_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, 1, period_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, 1, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        mlg_type = wizard_data['mlg_type']
        bien_so_xe_ids = wizard_data['bien_so_xe_ids']
        tat_toan = wizard_data['tat_toan']
        chusohuu_id = wizard_data['chusohuu_id']
        
        if self.partner_ids:
            p_ids = self.partner_ids
            p_ids = str(p_ids).replace('[', '(')
            p_ids = str(p_ids).replace(']', ')')
            sql_dathu_dauky = '''
                select ai.partner_id as partner_id, case when sum(aml.credit)!=0 then -1*sum(aml.credit) else 0 end sotien
                    from account_move_line aml
                    left join account_voucher av on aml.move_id = av.move_id
                    left join account_invoice ai on av.reference = ai.name
                    
                    where ai.mlg_type='%s' and ai.state in ('open','paid') and ai.chinhanh_id=%s and ai.partner_id in %s  
            '''%(mlg_type,chinhanh_id[0],p_ids)
            if not tat_toan:
                sql_dathu_dauky +='''
                    and (ai.ngay_tat_toan is null or (ai.ngay_tat_toan is not null and '%s'<ai.ngay_tat_toan)) and ai.date_invoice<'%s' 
                '''%(period_to.date_stop,period_from.date_start)
            else:
                sql_dathu_dauky +='''
                    and ai.tat_toan=True and ai.ngay_tat_toan between '%s' and '%s'  
                '''%(period_from.date_start,period_to.date_stop)
            if chusohuu_id:
                sql_dathu_dauky += '''
                    and ai.thu_cho_doituong_id=%s 
                '''%(chusohuu_id[0])
            if bien_so_xe_ids:
                bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
                bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
                sql_dathu_dauky+='''
                    and ai.bien_so_xe_id in %s 
                '''%(bien_so_xe_ids)
            sql_dathu_dauky += '''
                and aml.date < '%s' 
                group by ai.partner_id
            '''%(period_from.date_start)
            
            sql_no_dauky = '''
                select partner_id, case when sum(COALESCE(so_tien,0)+COALESCE(sotien_lai,0))!=0 then sum(COALESCE(so_tien,0)+COALESCE(sotien_lai,0)) else 0 end sotien
                    from account_invoice where mlg_type='%s' and chinhanh_id=%s and partner_id in %s
                        and state in ('open','paid') 
            '''%(mlg_type,chinhanh_id[0],p_ids)
            if not tat_toan:
                sql_no_dauky +='''
                    and (ngay_tat_toan is null or (ngay_tat_toan is not null and '%s'<ngay_tat_toan)) and date_invoice <'%s' 
                '''%(period_to.date_stop,period_from.date_start)
            else:
                sql_no_dauky +='''
                    and tat_toan=True and ngay_tat_toan between '%s' and '%s'  
                '''%(period_from.date_start,period_to.date_stop)
            if chusohuu_id:
                sql_no_dauky += '''
                    and thu_cho_doituong_id=%s 
                '''%(chusohuu_id[0])
            if bien_so_xe_ids:
                bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
                bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
                sql_no_dauky+='''
                    and bien_so_xe_id in %s 
                '''%(bien_so_xe_ids)
            sql_no_dauky += ''' group by partner_id '''
            
            sql_thulai_dauky = '''
                select ai.partner_id as partner_id, case when sum(stl.so_tien)!=0 then -1*sum(stl.so_tien) else 0 end sotien
                    from so_tien_lai stl
                    left join account_invoice ai on stl.invoice_id = ai.id
                    
                    where ai.mlg_type='%s' and ai.state in ('open','paid') and ai.chinhanh_id=%s and ai.partner_id in %s  
            '''%(mlg_type,chinhanh_id[0],p_ids)
            if not tat_toan:
                sql_thulai_dauky +='''
                    and (ai.ngay_tat_toan is null or (ai.ngay_tat_toan is not null and '%s'<ai.ngay_tat_toan)) and ai.date_invoice<'%s' 
                '''%(period_to.date_stop,period_from.date_start)
            else:
                sql_thulai_dauky +='''
                    and ai.tat_toan=True and ai.ngay_tat_toan between '%s' and '%s'  
                '''%(period_from.date_start,period_to.date_stop)
            if chusohuu_id:
                sql_thulai_dauky += '''
                    and ai.thu_cho_doituong_id=%s 
                '''%(chusohuu_id[0])
            if bien_so_xe_ids:
                bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
                bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
                sql_thulai_dauky+='''
                    and ai.bien_so_xe_id in %s 
                '''%(bien_so_xe_ids)
            sql_thulai_dauky += '''
                and stl.ngay < '%s'
                group by ai.partner_id
            '''%(period_from.date_start)
            
            sql_tong = '''
                select partner_id, sum(sotien) as sotien from (
            '''+sql_dathu_dauky+' union '+sql_no_dauky+' union '+sql_thulai_dauky+' )foo group by partner_id '
            
            self.cr.execute(sql_tong)
            ndks = self.cr.dictfetchall()
            
            for ndk in ndks:
                if self.ndk_dict.get(ndk['partner_id'],False):
                    self.ndk_dict[ndk['partner_id']] += ndk['sotien']
                else:
                    self.ndk_dict[ndk['partner_id']] = ndk['sotien']
            return True
        return True
    
    def get_tongcongno(self):
        return self.tongcongno
    
    def get_tongcongno_dathu(self):
        return self.tongthu
    
    def get_nocuoiky(self, partner_id):
        if self.nck_dict.get(partner_id,False):
            nocuoiky = self.nck_dict[partner_id]
            self.tongcongno += nocuoiky
            return nocuoiky
        return 0
    
    def get_nocuoiky_data(self):
        wizard_data = self.localcontext['data']['form']
        period_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, 1, period_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, 1, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        mlg_type = wizard_data['mlg_type']
        bien_so_xe_ids = wizard_data['bien_so_xe_ids']
        tat_toan = wizard_data['tat_toan']
        chusohuu_id = wizard_data['chusohuu_id']
        
        if self.partner_ids:
            p_ids = self.partner_ids
            p_ids = str(p_ids).replace('[', '(')
            p_ids = str(p_ids).replace(']', ')')
            sql_dathu_cuoiky = '''
                select ai.partner_id as partner_id, case when sum(aml.credit)!=0 then -1*sum(aml.credit) else 0 end sotien
                    from account_move_line aml
                    left join account_voucher av on aml.move_id = av.move_id
                    left join account_invoice ai on av.reference = ai.name
                    
                    where ai.mlg_type='%s' and ai.state in ('open','paid') and ai.chinhanh_id=%s and ai.partner_id in %s  
            '''%(mlg_type,chinhanh_id[0],p_ids)
            if not tat_toan:
                sql_dathu_cuoiky +='''
                    and (ai.ngay_tat_toan is null or (ai.ngay_tat_toan is not null and '%s'<ai.ngay_tat_toan)) and ai.date_invoice<='%s' 
                '''%(period_to.date_stop,period_to.date_stop)
            else:
                sql_dathu_cuoiky +='''
                    and ai.tat_toan=True and ai.ngay_tat_toan between '%s' and '%s'  
                '''%(period_from.date_start,period_to.date_stop)
            if chusohuu_id:
                sql_dathu_cuoiky += '''
                    and ai.thu_cho_doituong_id=%s 
                '''%(chusohuu_id[0])
            if bien_so_xe_ids:
                bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
                bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
                sql_dathu_cuoiky+='''
                    and ai.bien_so_xe_id in %s 
                '''%(bien_so_xe_ids)
            sql_dathu_cuoiky += '''
                and aml.date <= '%s' 
                group by ai.partner_id
            '''%(period_to.date_stop)
            
            sql_no_cuoiky = '''
                select partner_id, case when sum(COALESCE(so_tien,0)+COALESCE(sotien_lai,0))!=0 then sum(COALESCE(so_tien,0)+COALESCE(sotien_lai,0)) else 0 end sotien
                    from account_invoice where mlg_type='%s' and chinhanh_id=%s and partner_id in %s
                        and state in ('open','paid') 
            '''%(mlg_type,chinhanh_id[0],p_ids)
            if not tat_toan:
                sql_no_cuoiky +='''
                    and (ngay_tat_toan is null or (ngay_tat_toan is not null and '%s'<ngay_tat_toan)) and date_invoice <='%s' 
                '''%(period_to.date_stop,period_to.date_stop)
            else:
                sql_no_cuoiky +='''
                    and tat_toan=True and ngay_tat_toan between '%s' and '%s'  
                '''%(period_from.date_start,period_to.date_stop)
            if chusohuu_id:
                sql_no_cuoiky += '''
                    and thu_cho_doituong_id=%s 
                '''%(chusohuu_id[0])
            if bien_so_xe_ids:
                bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
                bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
                sql_no_cuoiky+='''
                    and bien_so_xe_id in %s 
                '''%(bien_so_xe_ids)
            sql_no_cuoiky += ''' group by partner_id '''
            
            sql_thulai_cuoiky = '''
                select ai.partner_id as partner_id, case when sum(stl.so_tien)!=0 then -1*sum(stl.so_tien) else 0 end sotien
                    from so_tien_lai stl
                    left join account_invoice ai on stl.invoice_id = ai.id
                    
                    where ai.mlg_type='%s' and ai.state in ('open','paid') and ai.chinhanh_id=%s and ai.partner_id in %s  
            '''%(mlg_type,chinhanh_id[0],p_ids)
            if not tat_toan:
                sql_thulai_cuoiky +='''
                    and (ai.ngay_tat_toan is null or (ai.ngay_tat_toan is not null and '%s'<ai.ngay_tat_toan)) and ai.date_invoice<='%s' 
                '''%(period_to.date_stop,period_from.date_start)
            else:
                sql_thulai_cuoiky +='''
                    and ai.tat_toan=True and ai.ngay_tat_toan between '%s' and '%s'  
                '''%(period_from.date_start,period_to.date_stop)
            if chusohuu_id:
                sql_thulai_cuoiky += '''
                    and ai.thu_cho_doituong_id=%s 
                '''%(chusohuu_id[0])
            if bien_so_xe_ids:
                bien_so_xe_ids = str(bien_so_xe_ids).replace('[', '(')
                bien_so_xe_ids = str(bien_so_xe_ids).replace(']', ')')
                sql_thulai_cuoiky+='''
                    and ai.bien_so_xe_id in %s 
                '''%(bien_so_xe_ids)
            sql_thulai_cuoiky += '''
                and stl.ngay <= '%s'
                group by ai.partner_id
            '''%(period_to.date_stop)
            
            sql_tong = '''
                select partner_id, sum(sotien) as sotien from (
            '''+sql_dathu_cuoiky+' union '+sql_no_cuoiky+' union '+sql_thulai_cuoiky+' )foo group by partner_id '
            
            self.cr.execute(sql_tong)
            ncks = self.cr.dictfetchall()
            
            for nck in ncks:
                if self.nck_dict.get(nck['partner_id'],False):
                    self.nck_dict[nck['partner_id']] += nck['sotien']
                else:
                    self.nck_dict[nck['partner_id']] = nck['sotien']
            return True
        return True
    
    def get_chitiet_congno(self, partner_id, bsx_id):
        if self.ctcn_dict.get(partner_id, False):
            if self.ctcn_dict[partner_id].get(bsx_id, False):
                return self.ctcn_dict[partner_id][bsx_id]
        return []
    
    def get_chitiet_congno_data(self):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, 1, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, 1, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        mlg_type = wizard_data['mlg_type']
        tat_toan = wizard_data['tat_toan']
        chusohuu_id = wizard_data['chusohuu_id']
        if self.bsx_ids and self.partner_ids:
            b_ids = self.bsx_ids
            b_ids = str(b_ids).replace('[', '(')
            b_ids = str(b_ids).replace(']', ')')
            
            p_ids = self.partner_ids
            p_ids = str(p_ids).replace('[', '(')
            p_ids = str(p_ids).replace(']', ')')
            
            sql = '''
                select ai.partner_id as partner_id, ai.bien_so_xe_id as bien_so_xe_id, ai.id as invoice_id,ai.date_invoice as ngay,ai.name as maphieudexuat,
                    rp.ma_doi_tuong as madoituong,rp.name as tendoituong,(COALESCE(ai.so_tien,0)+COALESCE(sotien_lai,0)) as no,
                    ai.fusion_id as fusion_id,ai.loai_giaodich as loai_giaodich,ai.dien_giai as dien_giai,ai.ngay_tat_toan as ngay_tat_toan
                
                    from account_invoice ai
                    left join res_partner rp on rp.id = ai.partner_id
                    
                    where ai.partner_id in %s and ai.state in ('open','paid') and ai.chinhanh_id=%s
                        and ai.mlg_type='%s' and ai.bien_so_xe_id in %s 
            '''%(p_ids,chinhanh_id[0],mlg_type,b_ids)
            if not tat_toan:
                sql +='''
                    and (ai.ngay_tat_toan is null or (ai.ngay_tat_toan is not null and '%s'<ai.ngay_tat_toan)) and ai.date_invoice between '%s' and '%s' 
                '''%(period_to.date_stop,period_from.date_start,period_to.date_stop)
            else:
                sql +='''
                    and ai.tat_toan=True and ai.ngay_tat_toan between '%s' and '%s' 
                '''%(period_from.date_start,period_to.date_stop)
            if chusohuu_id:
                sql += '''
                    and ai.thu_cho_doituong_id=%s 
                '''%(chusohuu_id[0])
            sql += '''
                group by ai.partner_id, ai.bien_so_xe_id, ai.id,ai.date_invoice,ai.name,rp.ma_doi_tuong,rp.name,
                    ai.fusion_id,ai.loai_giaodich,ai.dien_giai,ai.ngay_tat_toan
                    
                order by ai.date_invoice
            '''
            self.cr.execute(sql)
            ctcns = self.cr.dictfetchall()
            for ctcn in ctcns:
                if self.ctcn_dict.get(ctcn['partner_id'], False):
                    if self.ctcn_dict[ctcn['partner_id']].get(ctcn['bien_so_xe_id'], False):
                        self.ctcn_dict[ctcn['partner_id']][ctcn['bien_so_xe_id']].append({
                            'partner_id': ctcn['partner_id'],
                            'bien_so_xe_id': ctcn['bien_so_xe_id'],
                            'invoice_id': ctcn['invoice_id'],
                            'ngay': ctcn['ngay'],
                            'maphieudexuat': ctcn['maphieudexuat'],
                            'madoituong': ctcn['madoituong'],
                            'tendoituong': ctcn['tendoituong'],
                            'no': ctcn['no'],
                            'fusion_id': ctcn['fusion_id'],
                            'loai_giaodich': ctcn['loai_giaodich'],
                            'dien_giai': ctcn['dien_giai'],
                            'ngay_tat_toan': ctcn['ngay_tat_toan'],
                        })
                    else:
                        self.ctcn_dict[ctcn['partner_id']][ctcn['bien_so_xe_id']] = [{
                            'partner_id': ctcn['partner_id'],
                            'bien_so_xe_id': ctcn['bien_so_xe_id'],
                            'invoice_id': ctcn['invoice_id'],
                            'ngay': ctcn['ngay'],
                            'maphieudexuat': ctcn['maphieudexuat'],
                            'madoituong': ctcn['madoituong'],
                            'tendoituong': ctcn['tendoituong'],
                            'no': ctcn['no'],
                            'fusion_id': ctcn['fusion_id'],
                            'loai_giaodich': ctcn['loai_giaodich'],
                            'dien_giai': ctcn['dien_giai'],
                            'ngay_tat_toan': ctcn['ngay_tat_toan'],
                        }]
                else:
                    self.ctcn_dict[ctcn['partner_id']] = {ctcn['bien_so_xe_id']: [{
                            'partner_id': ctcn['partner_id'],
                            'bien_so_xe_id': ctcn['bien_so_xe_id'],
                            'invoice_id': ctcn['invoice_id'],
                            'ngay': ctcn['ngay'],
                            'maphieudexuat': ctcn['maphieudexuat'],
                            'madoituong': ctcn['madoituong'],
                            'tendoituong': ctcn['tendoituong'],
                            'no': ctcn['no'],
                            'fusion_id': ctcn['fusion_id'],
                            'loai_giaodich': ctcn['loai_giaodich'],
                            'dien_giai': ctcn['dien_giai'],
                            'ngay_tat_toan': ctcn['ngay_tat_toan'],
                    }]}
        return True
    
    def get_payment(self, invoice_id):
        if not invoice_id:
            return []
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, 1, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, 1, period_to_id[0])
        invoice = self.pool.get('account.invoice').browse(self.cr, 1, invoice_id)
        pays = []
        for pay in invoice.payment_ids:
            if pay.date >= period_from.date_start and pay.date<=period_to.date_stop:
                pays.append(pay)
                self.nocuoiky = self.nocuoiky-pay.credit
                if not pay.sotienlai_line:
                    self.tongthu += pay.credit
        return pays
    
    def get_only_payment(self, partner_id, bsx_id):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, 1, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, 1, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        mlg_type = wizard_data['mlg_type']
        tat_toan = wizard_data['tat_toan']
        chusohuu_id = wizard_data['chusohuu_id']
        sql = '''
            select case when sum(credit)!=0 then sum(credit) else 0 end sotien
                from account_move_line
                where move_id in (select move_id from account_voucher
                    where reference in (select name from account_invoice
                        where mlg_type='%s' and state in ('open','paid') and chinhanh_id=%s and partner_id=%s and bien_so_xe_id=%s 
        '''%(mlg_type,chinhanh_id[0],partner_id,bsx_id)
        if not tat_toan:
            sql +='''
                and (ngay_tat_toan is null or (ngay_tat_toan is not null and '%s'<ngay_tat_toan)) and date_invoice<'%s' 
            '''%(period_to.date_stop,period_from.date_start)
        else:
            sql +='''
                and tat_toan=True and ngay_tat_toan between '%s' and '%s' 
            '''%(period_from.date_start,period_to.date_stop)
        if chusohuu_id:
            sql += '''
                and thu_cho_doituong_id=%s 
            '''%(chusohuu_id[0])
        sql += ''' ))
                and date between '%s' and '%s' '''%(period_from.date_start,period_to.date_stop)
        self.cr.execute(sql)
        co = self.cr.fetchone()[0]
        self.nocuoiky = self.nocuoiky-co
        
        sql = '''
            select date,fusion_id,credit,ref,loai_giaodich,note_giaodich,id
                from account_move_line
                where credit!=0 and move_id in (select move_id from account_voucher
                    where reference in (select name from account_invoice
                        where mlg_type='%s' and state in ('open','paid') and chinhanh_id=%s and partner_id=%s and bien_so_xe_id=%s 
        '''%(mlg_type,chinhanh_id[0],partner_id,bsx_id)
        if not tat_toan:
            sql +='''
                and (ngay_tat_toan is null or (ngay_tat_toan is not null and '%s'<ngay_tat_toan))  and date_invoice<'%s' 
            '''%(period_to.date_stop,period_from.date_start)
        else:
            sql +='''
                and tat_toan=True and ngay_tat_toan between '%s' and '%s' 
            '''%(period_from.date_start,period_to.date_stop)
        if chusohuu_id:
            sql += '''
                and thu_cho_doituong_id=%s 
            '''%(chusohuu_id[0])
        sql += ''' ))
                and date between '%s' and '%s' '''%(period_from.date_start,period_to.date_stop)
        self.cr.execute(sql)
        onlypay = self.cr.dictfetchall()
        for only_pay in onlypay:
            if not self.get_only_pay_sotienlai(only_pay['id']):
                self.tongthu += only_pay['credit']
        return onlypay
    
    def get_only_pay_sotienlai(self, move_line_id):
        if move_line_id:
            move_line = self.pool.get('account.move.line').browse(self.cr, 1, move_line_id)
            if move_line.sotienlai_line:
                return True
        return False
    
    def get_lichsu_thutienlai(self, invoice_id):
        if not invoice_id:
            return []
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, 1, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, 1, period_to_id[0])
        invoice = self.pool.get('account.invoice').browse(self.cr, 1, invoice_id)
        invoice = self.pool.get('account.invoice').browse(self.cr, 1, invoice_id)
        pays = []
        for pay in invoice.lichsu_thutienlai_line:
            if pay.ngay >= period_from.date_start and pay.ngay<=period_to.date_stop:
                pays.append(pay)
                self.nocuoiky = self.nocuoiky-pay.so_tien
                self.tonglaithu += pay.so_tien
                self.tongthu += pay.move_line_id and pay.move_line_id.credit or 0
        return pays
            
    def get_only_lichsu_thutienlai(self, partner_id, bsx_id):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, 1, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, 1, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        mlg_type = wizard_data['mlg_type']
        tat_toan = wizard_data['tat_toan']
        chusohuu_id = wizard_data['chusohuu_id']
        sql = '''
            select case when sum(so_tien)!=0 then sum(so_tien) else 0 end sotien
                from so_tien_lai
                where invoice_id in (select id from account_invoice
                        where mlg_type='%s' and state in ('open','paid') and chinhanh_id=%s and partner_id=%s and bien_so_xe_id=%s 
        '''%(mlg_type,chinhanh_id[0],partner_id,bsx_id)
        if not tat_toan:
            sql +='''
                and (ngay_tat_toan is null or (ngay_tat_toan is not null and '%s'<ngay_tat_toan)) and date_invoice<'%s' 
            '''%(period_to.date_stop,period_from.date_start)
        else:
            sql +='''
                and tat_toan=True and ngay_tat_toan between '%s' and '%s' 
            '''%(period_from.date_start,period_to.date_stop)
        if chusohuu_id:
            sql += '''
                and thu_cho_doituong_id=%s 
            '''%(chusohuu_id[0])
        sql += ''' )
                and ngay between '%s' and '%s' '''%(period_from.date_start,period_to.date_stop)
        self.cr.execute(sql)
        co = self.cr.fetchone()[0]
        self.nocuoiky = self.nocuoiky-co
        
        sql = '''
            select ngay,fusion_id,so_tien,loai_giaodich,move_line_id,invoice_id
                from so_tien_lai
                where invoice_id in (select id from account_invoice
                        where mlg_type='%s' and state in ('open','paid') and chinhanh_id=%s and partner_id=%s and bien_so_xe_id=%s 
        '''%(mlg_type,chinhanh_id[0],partner_id,bsx_id)
        if not tat_toan:
            sql +='''
                and (ngay_tat_toan is null or (ngay_tat_toan is not null and '%s'<ngay_tat_toan))  and date_invoice<'%s' 
            '''%(period_to.date_stop,period_from.date_start)
        else:
            sql +='''
                and tat_toan=True and ngay_tat_toan between '%s' and '%s' 
            '''%(period_from.date_start,period_to.date_stop)
        if chusohuu_id:
            sql += '''
                and thu_cho_doituong_id=%s 
            '''%(chusohuu_id[0])
        sql += ''' )
                and ngay between '%s' and '%s' '''%(period_from.date_start,period_to.date_stop)
        self.cr.execute(sql)
        onlylai = self.cr.dictfetchall()
        for line in onlylai:
            self.tonglaithu += line['so_tien']
        return onlylai
    
    def get_name_invoice(self, invoice_id):
        if invoice_id:
            inv = self.pool.get('account.invoice').browse(self.cr, 1, invoice_id)
            return inv.name
        return ''
    
    def get_lai_co(self, move_line_id):
        if move_line_id:
            move_line = self.pool.get('account.move.line').browse(self.cr, 1, move_line_id)
            self.tongthu += move_line.credit
            return move_line.credit
        return 0
            
    def get_tonglaithu(self):
        return self.tonglaithu
    
    def get_sdtlkdauky(self, partner_id,bsx_id):
        if self.sdtlkdauky_dict.get(partner_id, False):
            if self.sdtlkdauky_dict[partner_id].get(bsx_id, False):
                return self.sdtlkdauky_dict[partner_id][bsx_id]
        return 0
    
    def get_sdtlkdauky_data(self):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, 1, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, 1, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        mlg_type = wizard_data['mlg_type']
        tat_toan = wizard_data['tat_toan']
        chusohuu_id = wizard_data['chusohuu_id']
        if self.bsx_ids and self.partner_ids:
            b_ids = self.bsx_ids
            b_ids = str(b_ids).replace('[', '(')
            b_ids = str(b_ids).replace(']', ')')
            
            p_ids = self.partner_ids
            p_ids = str(p_ids).replace('[', '(')
            p_ids = str(p_ids).replace(']', ')')
            
            sql = '''
                select ai.partner_id as partner_id, ai.bien_so_xe_id as bien_so_xe_id,
                    case when sum(aml.credit)!=0 then sum(aml.credit) else 0 end sotien
                    
                    from account_move_line aml
                    left join account_voucher av on aml.move_id=av.move_id
                    left join account_invoice ai on av.reference=ai.name
                    
                    where ai.mlg_type='%s' and ai.state in ('open','paid') and ai.chinhanh_id=%s and ai.partner_id in %s and ai.bien_so_xe_id in %s 
            '''%(mlg_type,chinhanh_id[0],p_ids,b_ids)
            if not tat_toan:
                sql +='''
                    and (ai.ngay_tat_toan is null or (ai.ngay_tat_toan is not null and '%s'<ai.ngay_tat_toan)) and ai.date_invoice<'%s' 
                '''%(period_to.date_stop,period_from.date_start)
            else:
                sql +='''
                    and ai.tat_toan=True and ai.ngay_tat_toan between '%s' and '%s'  
                '''%(period_from.date_start,period_to.date_stop)
            if chusohuu_id:
                sql += '''
                    and ai.thu_cho_doituong_id=%s 
                '''%(chusohuu_id[0])
            sql += '''
                    and aml.date < '%s' 
                group by ai.partner_id, ai.bien_so_xe_id
            '''%(period_from.date_start)
            self.cr.execute(sql)
            sptlkdaukys = self.cr.dictfetchall()
            for sptlkdauky in sptlkdaukys:
                if self.sdtlkdauky_dict.get(sptlkdauky['partner_id'],False):
                    if self.sdtlkdauky_dict[sptlkdauky['partner_id']].get(sptlkdauky['bien_so_xe_id'], False):
                        self.sdtlkdauky_dict[sptlkdauky['partner_id']][sptlkdauky['bien_so_xe_id']] += sptlkdauky['sotien']
                    else:
                        self.sdtlkdauky_dict[sptlkdauky['partner_id']][sptlkdauky['bien_so_xe_id']] = sptlkdauky['sotien']
                else:
                    self.sdtlkdauky_dict[sptlkdauky['partner_id']] = {sptlkdauky['bien_so_xe_id'] :sptlkdauky['sotien']}
        return True
    
    def get_sdtlkcuoiky(self, partner_id,bsx_id):
        if self.sdtlkcuoiky_dict.get(partner_id, False):
            if self.sdtlkcuoiky_dict[partner_id].get(bsx_id, False):
                lkcuoiky = self.sdtlkcuoiky_dict[partner_id][bsx_id]
                self.tongsdtlkck += lkcuoiky
                return lkcuoiky
        return 0
    
    def get_sdtlkcuoiky_data(self):
        wizard_data = self.localcontext['data']['form']
        period_from_id = wizard_data['period_from_id']
        period_to_id = wizard_data['period_to_id']
        period_from = self.pool.get('account.period').browse(self.cr, 1, period_from_id[0])
        period_to = self.pool.get('account.period').browse(self.cr, 1, period_to_id[0])
        chinhanh_id = wizard_data['chinhanh_id']
        mlg_type = wizard_data['mlg_type']
        tat_toan = wizard_data['tat_toan']
        chusohuu_id = wizard_data['chusohuu_id']
        if self.bsx_ids and self.partner_ids:
            b_ids = self.bsx_ids
            b_ids = str(b_ids).replace('[', '(')
            b_ids = str(b_ids).replace(']', ')')
            
            p_ids = self.partner_ids
            p_ids = str(p_ids).replace('[', '(')
            p_ids = str(p_ids).replace(']', ')')
        
            sql = '''
                select ai.partner_id as partner_id, ai.bien_so_xe_id as bien_so_xe_id,
                    case when sum(aml.credit)!=0 then sum(aml.credit) else 0 end sotien
                    
                    from account_move_line aml
                    left join account_voucher av on aml.move_id=av.move_id
                    left join account_invoice ai on av.reference=ai.name
                    
                    where ai.mlg_type='%s' and ai.state in ('open','paid') and ai.chinhanh_id=%s and ai.partner_id in %s and ai.bien_so_xe_id in %s 
            '''%(mlg_type,chinhanh_id[0],p_ids,b_ids)
            if not tat_toan:
                sql +='''
                    and (ai.ngay_tat_toan is null or (ai.ngay_tat_toan is not null and '%s'<ai.ngay_tat_toan)) and ai.date_invoice<='%s' 
                '''%(period_to.date_stop,period_to.date_stop)
            else:
                sql +='''
                    and ai.tat_toan=True and ai.ngay_tat_toan between '%s' and '%s'  
                '''%(period_from.date_start,period_to.date_stop)
            if chusohuu_id:
                    sql += '''
                        and ai.thu_cho_doituong_id=%s 
                    '''%(chusohuu_id[0])
            sql += '''
                and aml.date <= '%s' 
                group by ai.partner_id, ai.bien_so_xe_id
            '''%(period_to.date_stop)
            
            self.cr.execute(sql)
            sptlkcuoikys = self.cr.dictfetchall()
            for sptlkcuoiky in sptlkcuoikys:
                if self.sdtlkcuoiky_dict.get(sptlkcuoiky['partner_id'],False):
                    if self.sdtlkcuoiky_dict[sptlkcuoiky['partner_id']].get(sptlkcuoiky['bien_so_xe_id'], False):
                        self.sdtlkcuoiky_dict[sptlkcuoiky['partner_id']][sptlkcuoiky['bien_so_xe_id']] += sptlkcuoiky['sotien']
                    else:
                        self.sdtlkcuoiky_dict[sptlkcuoiky['partner_id']][sptlkcuoiky['bien_so_xe_id']] = sptlkcuoiky['sotien']
                else:
                    self.sdtlkcuoiky_dict[sptlkcuoiky['partner_id']] = {sptlkcuoiky['bien_so_xe_id'] :sptlkcuoiky['sotien']}
        return True
            
    
    