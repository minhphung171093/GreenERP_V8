# -*- coding: utf-8 -*-

from oorpc import OpenObjectRPC, define_arg
import psycopg2

def delete_trachiho_madoituong_bang_machinhanh(oorpc, cursor):
    sql = '''
        select ai.name
            from account_invoice ai
            left join res_partner rp on ai.partner_id=rp.id
            left join account_account aa on ai.chinhanh_id=aa.id
        
            where mlg_type='chi_ho' and rp.ma_doi_tuong=aa.code
    '''
    cursor.execute(sql)
    for invoice in cursor.fetchall():
        oorpc.xoa_cong_no('account.invoice', 'chi_ho', invoice[0])
        print 'Đã xóa: "%s"'%(invoice[0])
    return True

def update_tragopxe_thuchodoituong_rong(oorpc, cursor):
    sql = '''
        select ai.id as invoice_id, aa.code as ma_chinhanh
            from account_invoice ai
            left join account_account aa on ai.chinhanh_id=aa.id
            where ai.mlg_type='tra_gop_xe' and ai.thu_cho_doituong_id is null
    '''
    cursor.execute(sql)
    for line in cursor.fetchall():
        sql = '''
            select id from res_partner where nhadautugiantiep=True and ma_doi_tuong='%s'
        '''%(line[1])
        cursor.execute(sql)
        partner_ids = [r[0] for r in cursor.fetchall()]
        if partner_ids:
            oorpc.write('account.invoice',[line[0]],{'thu_cho_doituong_id': partner_ids[0]})
            print 'Đã update: "%s"'%(line[0])
    return True

if __name__ == '__main__':
    (options, args) = define_arg()
    oorpc = OpenObjectRPC('localhost', 'arap_16022016_1', 'admin', '1', '8069')
    db_conn_string = "host='localhost' port='5432' dbname='arap_16022016_1' user='openerp' password='openerp'"
    conn = psycopg2.connect(db_conn_string)
    cursor = conn.cursor()
    print 'In progress ...'
    delete_trachiho_madoituong_bang_machinhanh(oorpc, cursor)
    update_tragopxe_thuchodoituong_rong(oorpc, cursor)
    print 'Done.'
    
    
    
    