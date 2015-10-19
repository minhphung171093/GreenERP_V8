# -*- coding: utf-8 -*-
# #############################################################################
# 
# #############################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _
import sys
import os
import logging
_logger = logging.getLogger(__name__)

# from xlrd import open_workbook
# 
# import os
# from openerp import modules
# base_path = os.path.dirname(modules.get_module_path('general_report_account'))

# class account_balance_sheet_report_template(osv.osv):
#     _name = "account.balance.sheet.report.template"
#     _columns = {
#         'name': fields.char('Name', size=256, required=True),
#         'code': fields.char('Code', size=256, required=True),
#         'note': fields.char('Note', size=500),
#         'lines': fields.one2many('account.balance.sheet.report.template.line', 'template_id', 'Lines'),
#     }
#     
#     def init(self, cr):
#         wb = open_workbook(base_path + '/general_report_account/data/1_account_balance_sheet_template.xls')
#         for s in wb.sheets():
#             for row in range(1,s.nrows):
#                 val0 = s.cell(row,0).value
#                 val1 = s.cell(row,1).value
#                 val2 = s.cell(row,2).value
#                 this = self.search(cr, 1, [('code','=',val1)])
#                 if not this:
#                     self.create(cr, 1, {'name': val0,'code':val1,'note':val2})
#             break
#         
# account_balance_sheet_report_template()
# 
# class account_balance_sheet_report_template_line(osv.osv):
#     _name = "account.balance.sheet.report.template.line"
#     _columns = {
#         'category': fields.selection([
#             ('asset', 'Asset'),
#             ('equity', 'Equity')], 'Sum type', required=True),
#                 
#         'name': fields.char('Name', size=500, required=True),
#         'code': fields.char('Code', size=500, required=True),
#         'note': fields.char('Note', size=500),
#         'type': fields.selection([
#             ('dr', 'Dr or 0'),
#             ('cr', 'Cr or 0'),
#             ('bl_dr', 'Balance Dr'),
#             ('bl_cr', 'Balance Cr'),], 'Sum type', required=True),
#         'account_ids': fields.many2many('account.account','balance_sheet_account_account','balance_sheet_id', 'account_id', 'Accounts'),
#         'template_id': fields.many2one('account.balance.sheet.report.template', 'Template', required=True, ondelete='cascade'),
#     }
#     _defaults={
#                'type': 'dr',
#                'category': 'asset',
#                }
#     
# #     def init(self, cr):
# #         wb = open_workbook(base_path + '/general_report_account/data/account_balance_sheet_template_line.xls')
# #         for s in wb.sheets():
# #             for row in range(1,s.nrows):
# #                 val0 = s.cell(row,0).value
# #                 val1 = s.cell(row,1).value
# #                 val2 = s.cell(row,2).value
# #                 this = self.search(cr, 1, [('code','=',val1)])
# #                 if not this:
# #                     self.create(cr, 1, {'name': val0,'code':val1,'note':val2})
# #             break
#         
# account_balance_sheet_report_template_line()

class sql_balance_sheet(osv.osv):
    _name = "sql.balance.sheet"
    _auto = False
    
    #For reports
    def get_line(self, cr, start_date, end_date, times, company_id):
        query = '''
            -- select * from fin_balance_sheet_report_ts() where type = 1 order by seq;
            select * from fin_balance_sheet_report_ts('%s','%s', '%s', %s) order by seq;
        ''' %(start_date, end_date, times, company_id)
        cr.execute(query)
        return cr.dictfetchall()
    
    def get_line_nv(self, cr, start_date, end_date, times, company_id):
        query = '''
            -- select * from fin_balance_sheet_report_nv() where type = 2 order by seq;
            select * from fin_balance_sheet_report_nv('%s','%s', '%s', %s) order by seq;
        ''' %(start_date, end_date, times, company_id)
        cr.execute(query)
        return cr.dictfetchall()
    
    def init(self, cr):
        self.fin_balance_data(cr)
        self.fin_get_detailsbalance(cr)
        self.fin_get_balance_dr(cr)
        self.fin_get_balance_cr(cr)
        self.fin_get_balance_all2(cr)
        self.fin_get_balance_all(cr)
        
        self.fin_balance_sheet_report(cr)
        cr.commit()
        return True
    
    def fin_balance_data(self, cr):
        cr.execute("select exists (select 1 from pg_type where typname = 'fin_balance_data')")
        res = cr.fetchone()
        if res and res[0]:
            cr.execute('''delete from pg_type where typname = 'fin_balance_data';
                            delete from pg_class where relname='fin_balance_data';
                            commit;''')
        sql = '''
        CREATE TYPE fin_balance_data AS
           (seq integer,
            line_no character varying(16),
            description character varying(250),
            code character varying(32),
            illustrate character varying(32),
            prior_amount numeric,
            current_amount numeric,
            type integer,
            format integer);
        ALTER TYPE fin_balance_data
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True
    
    def fin_profit_loss_data(self, cr):
        cr.execute("select exists (select 1 from pg_proc where proname = 'fin_profit_loss_data')")
        res = cr.fetchone()
        if res and res[0]:
            return True
        sql = '''
        CREATE TYPE fin_profit_loss_data AS
           (prior_amt1 numeric,
            curr_amt1 numeric,
            prior_amt2 numeric,
            curr_amt2 numeric,
            prior_amt3 numeric,
            curr_amt3 numeric,
            prior_amt4 numeric,
            curr_amt4 numeric,
            prior_amt5 numeric,
            curr_amt5 numeric,
            prior_amt6 numeric,
            curr_amt6 numeric,
            prior_amt7 numeric,
            curr_amt7 numeric,
            prior_amt8 numeric,
            curr_amt8 numeric,
            prior_amt9 numeric,
            curr_amt9 numeric,
            prior_amt10 numeric,
            curr_amt10 numeric,
            prior_amt11 numeric,
            curr_amt11 numeric,
            prior_amt12 numeric,
            curr_amt12 numeric,
            prior_amt13 numeric,
            curr_amt13 numeric,
            prior_amt14 numeric,
            curr_amt14 numeric,
            prior_amt15 numeric,
            curr_amt15 numeric,
            prior_amt16 numeric,
            curr_amt16 numeric,
            prior_amt17 numeric,
            curr_amt17 numeric,
            prior_amt18 numeric,
            curr_amt18 numeric,
            prior_amt71 numeric,
            curr_amt71 numeric);
        ALTER TYPE fin_profit_loss_data
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True
    
    def fin_get_detailsbalance(self,cr):
#         cr.execute("select exists (select 1 from pg_proc where proname = 'fin_get_detailsbalance')")
#         res = cr.fetchone()
#         if res and res[0]:
#             return True
        sql = '''
        DROP FUNCTION IF EXISTS fin_get_detailsbalance(date, date, text, character varying, integer) CASCADE;
        commit;
        
        CREATE OR REPLACE FUNCTION fin_get_detailsbalance(date, date, text, character varying, integer)
          RETURNS numeric AS
        $BODY$
        DECLARE
            rec        record;
            lst_account    text = '';
            bal_dr    numeric = 0;
            bal_cr    numeric = 0;
        BEGIN
            lst_account = fin_get_array_accountid($3);
            
            if lst_account <> '' then
                for rec in execute '
                        select  account_id, case when sum(remain_dr) > sum(remain_cr)
                                then sum(remain_dr) - sum(remain_cr) else 0 end balance_dr,
                                case when sum(remain_dr) < sum(remain_cr) then
                                    sum(remain_cr) - sum(remain_dr) else 0 end balance_cr
                        from (
                                select  aml.account_id, sum(aml.debit) remain_dr, sum(aml.credit) remain_cr
                                from account_move amh left join account_move_line aml 
                                        on amh.id = aml.move_id
                                    left join account_journal as ajn on aml.journal_id = ajn.id
                                where amh.state = ''posted'' and aml.state = ''valid''
                                    and ajn.type = ''situation'' and aml.account_id in ('||lst_account||')
                                    and date_trunc(''year'', aml.date) = date_trunc(''year'', date($1))
                                    and amh.company_id = $3
                                group by aml.account_id
                                union all
                                select  aml.account_id, sum(aml.debit) remain_dr, sum(aml.credit) remain_cr
                                from account_move amh left join account_move_line aml 
                                        on amh.id = aml.move_id
                                    left join account_journal as ajn on aml.journal_id = ajn.id
                                where amh.state = ''posted'' and aml.state = ''valid''
                                    and ajn.type != ''situation'' and aml.account_id in ('||lst_account||')
                                    and date_trunc(''day'', aml.date) between date_trunc(''year'', date($1))
                                    and date($2) and amh.company_id = $3
                                group by aml.account_id
                        ) vw group by account_id' using $1, $2, $5
                loop
                    bal_dr = bal_dr + coalesce(rec.balance_dr, 0);
                    bal_cr = bal_cr + coalesce(rec.balance_cr, 0);
                end loop;
            else
                bal_dr = 0;
                bal_cr = 0;
            end if;
            
            if $4 = 'dr' then
                return bal_dr;
            else
                return bal_cr;
            end if;
            
        END;$BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100;
        ALTER FUNCTION fin_get_detailsbalance(date, date, text, character varying, integer)
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True
    
    def fin_get_balance_dr(self,cr):
#         cr.execute("select exists (select 1 from pg_proc where proname = 'fin_get_balance_dr')")
#         res = cr.fetchone()
#         if res and res[0]:
#             return True
        sql = '''
        DROP FUNCTION IF EXISTS fin_get_balance_dr(date, date, text, integer) CASCADE;
        commit;
        
        CREATE OR REPLACE FUNCTION fin_get_balance_dr(date, date, text, integer)
          RETURNS numeric AS
        $BODY$
        DECLARE
            rec        record;
            lst_account    text = '';
            bal_dr    numeric = 0;
            bal_cr    numeric = 0;
        BEGIN
            lst_account = fin_get_array_accountid($3);
            
            if lst_account <> '' then
                for rec in execute '
                        select sum (debit) balance_dr, sum(credit) balance_cr
                        from (
                                select  account_id, partner_id,
                                        case when sum(dr_amount) > sum(cr_amount) then
                                            sum(dr_amount) - sum(cr_amount)
                                            else 0 end debit,
                                        case when sum(dr_amount) < sum(cr_amount) then
                                            sum(cr_amount) - sum(dr_amount)
                                            else 0 end credit
                                from (
                                        select  aml.account_id, aml.partner_id,
                                                sum(aml.debit) dr_amount, sum(aml.credit) cr_amount
                                        from account_move_line aml left join account_move amh on aml.move_id = amh.id
                                            left join account_journal ajn on aml.journal_id = ajn.id
                                        where amh.state = ''posted'' and aml.state = ''valid''
                                            and ajn.type = ''situation''
                                            and date_trunc(''year'', aml.date) = date_trunc(''year'', date($1))
                                            and aml.account_id in ('||lst_account||')
                                            and amh.company_id = $3
                                        group by aml.account_id, aml.partner_id
                                        union all
                                        select  aml.account_id, aml.partner_id,
                                                sum(aml.debit) dr_amount, sum(aml.credit) cr_amount
                                        from account_move_line aml left join account_move amh on aml.move_id = amh.id
                                            left join account_journal ajn on aml.journal_id = ajn.id
                                        where amh.state = ''posted'' and aml.state = ''valid''
                                            and ajn.type != ''situation''
                                            and date_trunc(''year'', aml.date) = date_trunc(''year'', date($1))
                                            and date_trunc(''day'', aml.date) <= date_trunc(''day'', date($2))
                                            and aml.account_id in ('||lst_account||')
                                            and amh.company_id = $3
                                        group by aml.account_id, aml.partner_id
                                    ) vw
                                group by account_id, partner_id
                            )balance' using $1, $2, $4
                loop
                    bal_dr = bal_dr + coalesce(rec.balance_dr, 0);
                    bal_cr = bal_cr + coalesce(rec.balance_cr, 0);
                end loop;
            else
                bal_dr = 0;
                bal_cr = 0;
            end if;
            return bal_dr;
        END;$BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100;
        ALTER FUNCTION fin_get_balance_dr(date, date, text, integer)
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True
    
    def fin_get_balance_cr(self,cr):
#         cr.execute("select exists (select 1 from pg_proc where proname = 'fin_get_balance_cr')")
#         res = cr.fetchone()
#         if res and res[0]:
#             return True
        sql = '''
        DROP FUNCTION IF EXISTS fin_get_balance_cr(date, date, text, integer) CASCADE;
        commit;
        
        CREATE OR REPLACE FUNCTION fin_get_balance_cr(date, date, text, integer)
          RETURNS numeric AS
        $BODY$
        DECLARE
            rec        record;
            lst_account    text = '';
            bal_dr    numeric = 0;
            bal_cr    numeric = 0;
        BEGIN
            lst_account = fin_get_array_accountid($3);
            if lst_account <> '' then
                for rec in execute '
                        select sum (debit) balance_dr, sum(credit) balance_cr
                        from (
                                select  account_id, partner_id,
                                        case when sum(dr_amount) > sum(cr_amount) then
                                            sum(dr_amount) - sum(cr_amount)
                                            else 0 end debit,
                                        case when sum(dr_amount) < sum(cr_amount) then
                                            sum(cr_amount) - sum(dr_amount)
                                            else 0 end credit
                                from (
                                        select  aml.account_id, aml.partner_id,
                                                sum(aml.debit) dr_amount, sum(aml.credit) cr_amount
                                        from account_move_line aml left join account_move amh on aml.move_id = amh.id
                                            left join account_journal ajn on aml.journal_id = ajn.id
                                        where amh.state = ''posted'' and aml.state = ''valid''
                                            and ajn.type = ''situation''
                                            and date_trunc(''year'', aml.date) = date_trunc(''year'', date($1))
                                            and aml.account_id in ('||lst_account||')
                                            and amh.company_id = $3
                                        group by aml.account_id, aml.partner_id
                                        union all
                                        select  aml.account_id, aml.partner_id,
                                                sum(aml.debit) dr_amount, sum(aml.credit) cr_amount
                                        from account_move_line aml left join account_move amh on aml.move_id = amh.id
                                            left join account_journal ajn on aml.journal_id = ajn.id
                                        where amh.state = ''posted'' and aml.state = ''valid''
                                            and ajn.type != ''situation''
                                            and date_trunc(''year'', aml.date) = date_trunc(''year'', date($1))
                                            and date_trunc(''day'', aml.date) <= date_trunc(''day'', date($2))
                                            and aml.account_id in ('||lst_account||')
                                            and amh.company_id = $3
                                        group by aml.account_id, aml.partner_id
                                    ) vw
                                group by account_id, partner_id
                            )balance' using $1, $2, $4
                loop
                    bal_dr = bal_dr + coalesce(rec.balance_dr, 0);
                    bal_cr = bal_cr + coalesce(rec.balance_cr, 0);
                end loop;
            else
                bal_dr = 0;
                bal_cr = 0;
            end if;
            return bal_cr;
        END;$BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100;
        ALTER FUNCTION fin_get_balance_cr(date, date, text, integer)
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True
    
    
    def fin_get_balance_all2(self,cr):
#         cr.execute("select exists (select 1 from pg_proc where proname = 'fin_get_balance_all2')")
#         res = cr.fetchone()
#         if res and res[0]:
#             return True
        sql = '''
        DROP FUNCTION IF EXISTS fin_get_balance_all2(date, date, text, text, character varying, integer) CASCADE;
        commit;
        
        CREATE OR REPLACE FUNCTION fin_get_balance_all2(date, date, text, text, character varying, integer)
          RETURNS numeric AS
        $BODY$
        DECLARE
            rec        record;
            lst_account    text = '';
            bal_dr    numeric = 0;
            bal_cr    numeric = 0;
        BEGIN
            lst_account = fin_get_array_accountid2($3, $4);
        
            if lst_account <> '' then
                for rec in execute '
                        select  sum(aml.debit) balance_dr, sum(aml.credit) balance_cr
                        from account_move amh left join account_move_line aml 
                                on amh.id = aml.move_id
                            left join account_journal ajn on aml.journal_id = ajn.id
                        where amh.state = ''posted'' and aml.state = ''valid''
                            and ajn.type = ''situation'' and aml.account_id in ('||lst_account||')
                            and date_trunc(''year'', aml.date) = date_trunc(''year'', date($1))
                            and amh.company_id = $3
                        union all
                        select  sum(aml.debit) balance_dr, sum(aml.credit) balance_cr
                        from account_move amh left join account_move_line aml 
                                on amh.id = aml.move_id
                            left join account_journal ajn on aml.journal_id = ajn.id
                        where amh.state = ''posted'' and aml.state = ''valid''
                            and ajn.type != ''situation'' and aml.account_id in ('||lst_account||')
                            and date_trunc(''day'', aml.date) between date_trunc(''year'', date($1))
                            and date($2)
                            and amh.company_id = $3' using $1, $2, $6
                loop
                    bal_dr = bal_dr + coalesce(rec.balance_dr, 0);
                    bal_cr = bal_cr + coalesce(rec.balance_cr, 0);
                end loop;
            else
                bal_dr = 0;
                bal_cr = 0;
            end if;
            
            if $5 = 'dr' then
                return (bal_dr - bal_cr);
            else
                return (bal_cr - bal_dr);
            end if;
            
        END;$BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100;
        ALTER FUNCTION fin_get_balance_all2(date, date, text, text, character varying, integer)
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True
    
    def fin_get_balance_all(self,cr):
#         cr.execute("select exists (select 1 from pg_proc where proname = 'fin_get_balance_all')")
#         res = cr.fetchone()
#         if res and res[0]:
#             return True
        sql = '''
        DROP FUNCTION IF EXISTS fin_get_balance_all(date, date, text, character varying, integer) CASCADE;
        commit;
        
        CREATE OR REPLACE FUNCTION fin_get_balance_all(date, date, text, character varying, integer)
          RETURNS numeric AS
        $BODY$
        DECLARE
            rec        record;
            lst_account    text = '';
            bal_dr    numeric = 0;
            bal_cr    numeric = 0;
        BEGIN
            lst_account = fin_get_array_accountid($3);
            
            if lst_account <> '' then
                for rec in execute '
                        select  sum(aml.debit) balance_dr, sum(aml.credit) balance_cr
                        from account_move amh left join account_move_line aml 
                                on amh.id = aml.move_id
                            left join account_journal ajn on aml.journal_id = ajn.id
                        where amh.state = ''posted'' and aml.state = ''valid''
                            and ajn.type = ''situation'' and aml.account_id in ('||lst_account||')
                            and date_trunc(''year'', aml.date) = date_trunc(''year'', date($1))
                            and amh.company_id = $3
                        union all
                        select  sum(aml.debit) balance_dr, sum(aml.credit) balance_cr
                        from account_move amh left join account_move_line aml 
                                on amh.id = aml.move_id
                            left join account_journal ajn on aml.journal_id = ajn.id
                        where amh.state = ''posted'' and aml.state = ''valid''
                            and ajn.type != ''situation'' and aml.account_id in ('||lst_account||')
                            and date_trunc(''day'', aml.date) between date_trunc(''year'', date($1))
                            and date($2)
                            and amh.company_id = $3' using $1, $2, $5
                loop
                    bal_dr = bal_dr + coalesce(rec.balance_dr, 0);
                    bal_cr = bal_cr + coalesce(rec.balance_cr, 0);
                end loop;
            else
                bal_dr = 0;
                bal_cr = 0;
            end if;
            
            if $4 = 'dr' then
                return (bal_dr - bal_cr);
            else
                return (bal_cr - bal_dr);
            end if;
            
        END;$BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100;
        ALTER FUNCTION fin_get_balance_all(date, date, text, character varying, integer)
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True
    
    def fin_balance_sheet_report(self,cr):
#         cr.execute("select exists (select 1 from pg_proc where proname = 'fin_balance_sheet_report')")
#         res = cr.fetchone()
#         if res and res[0]:
#             return True
        sql_ts = self.get_sql_ts() 
        cr.execute(sql_ts)
        
        sql_nv = self.get_sql_nv()
        cr.execute(sql_nv)
        return True
    
    def get_sql_ts(self):
        sql = '''
        DROP FUNCTION IF EXISTS fin_balance_sheet_report_ts(date, date, character varying, integer) CASCADE;
        commit;
        
        CREATE OR REPLACE FUNCTION fin_balance_sheet_report_ts(date, date, character varying, integer)
          RETURNS SETOF fin_balance_data AS
        $BODY$
        DECLARE
            _cur_sdate    alias for $1;
            _cur_edate    alias for $2;
            _type        alias for $3;
            rec_pl        record;
            bal_data    fin_balance_data%ROWTYPE;
            prior_sdate    date;
            prior_edate    date;
            
            prior_all    numeric = 0;
            curr_all    numeric = 0;
            prior_grp1    numeric = 0;
            curr_grp1    numeric = 0;
            prior_grp2    numeric;
            curr_grp2    numeric;
            prior_grp3    numeric;
            curr_grp3    numeric;
        BEGIN
            select * into prior_sdate,prior_edate from fn_get_prior_rangedate(_cur_sdate, _type);
            RAISE NOTICE 'Prior date range: % - %', prior_sdate, prior_edate;
            
            /*    Lấy số liệu phần TÀI SẢN    */
            -- === A. TÀI SẢN NGẮN HẠN ===
            prior_grp1 = 0;    curr_grp1 = 0;
            -- ===== Muc I =====
            prior_grp2 = 0;    curr_grp2 = 0;
            -- 1. lấy chỉ tiêu 111
            bal_data.seq = 3;
            bal_data.line_no = '1.';
            bal_data.description = 'Tiền';
            bal_data.code = '111';
            bal_data.illustrate = '';
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '111 112 113', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '111 112 113', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 2. lấy chỉ tiêu 112
            bal_data.seq = 4;
            bal_data.line_no = '2.';
            bal_data.description = 'Các khoản tương đương tiền';
            bal_data.code = '112';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '12811 12881', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '12811 12881', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 3. lấy chỉ tiêu 110 = 111 + 112
            bal_data.seq = 2;
            bal_data.line_no = 'I.';
            bal_data.description = 'Tiền và các khoản tương đương tiền';
            bal_data.code = '110';
            bal_data.illustrate = null;
            bal_data.prior_amount = prior_grp2;
            bal_data.current_amount = curr_grp2;
            bal_data.type = 1;
            bal_data.format = 1;
            return next bal_data;
            
            -- ===== Muc II =====
            prior_grp2 = 0;    curr_grp2 = 0;
            -- 4. lấy chỉ tiêu 121
            bal_data.seq = 6;
            bal_data.line_no = '1.';
            bal_data.description = 'Chứng khoán kinh doanh';
            bal_data.code = '121';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '121', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '121', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 5. lấy chỉ tiêu 122
            bal_data.seq = 7;
            bal_data.line_no = '2.';
            bal_data.description = 'Dự phòng giảm giá đầu tư chứng khoán kinh doanh (*)';
            bal_data.code = '122';
            bal_data.illustrate = null;
            bal_data.prior_amount = -1*fin_get_balance_all(prior_sdate, prior_edate, '2291', 'cr', $4);
            bal_data.current_amount = -1*fin_get_balance_all(_cur_sdate, _cur_edate, '2291', 'cr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 6. lấy chỉ tiêu 123
            bal_data.seq = 8;
            bal_data.line_no = '3.';
            bal_data.description = 'Đầu tư nắm giữ đến ngày đáo hạn';
            bal_data.code = '123';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '12812 12821 12882', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '12812 12821 12882', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 7. lấy chỉ tiêu 120 = 121 + 122 + 123
            bal_data.seq = 5;
            bal_data.line_no = 'II.';
            bal_data.description = 'Các khoản đầu tư tài chính ngắn hạn';
            bal_data.code = '120';
            bal_data.illustrate = '';
            bal_data.prior_amount = prior_grp2;
            bal_data.current_amount = curr_grp2;
            bal_data.type = 1;
            bal_data.format = 1;
            return next bal_data;
            
            -- ===== Muc III =====
            prior_grp2 = 0;    curr_grp2 = 0;
            -- 8. lấy chỉ tiêu 131
            bal_data.seq = 10;
            bal_data.line_no = '1.';
            bal_data.description = 'Phải thu của khách hàng';
            bal_data.code = '131';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_dr(prior_sdate, prior_edate, '1311', $4);
            bal_data.current_amount = fin_get_balance_dr(_cur_sdate, _cur_edate, '1311', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 9. lấy chỉ tiêu 132
            bal_data.seq = 11;
            bal_data.line_no = '2.';
            bal_data.description = 'Trả trước cho người bán';
            bal_data.code = '132';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_dr(prior_sdate, prior_edate, '3311', $4);
            bal_data.current_amount = fin_get_balance_dr(_cur_sdate, _cur_edate, '3311', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 10. lấy chỉ tiêu 133
            bal_data.seq = 12;
            bal_data.line_no = '3.';
            bal_data.description = 'Phải thu nội bộ ngắn hạn';
            bal_data.code = '133';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '13621 13631 13681', 'dr', $4) -
                                    fin_get_balance_all(prior_sdate, prior_edate, '33621 33631 33681', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '13621 13631 13681', 'dr', $4) -
                                    fin_get_balance_all(_cur_sdate, _cur_edate, '33621 33631 33681', 'cr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 11. lấy chỉ tiêu 134
            bal_data.seq = 13;
            bal_data.line_no = '4.';
            bal_data.description = 'Phải thu theo tiến độ kế hoạch hợp đồng xây dựng';
            bal_data.code = '134';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_dr(prior_sdate, prior_edate, '337', $4);
            bal_data.current_amount = fin_get_balance_dr(_cur_sdate, _cur_edate, '337', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 12. lấy chỉ tiêu 135
            bal_data.seq = 14;
            bal_data.line_no = '5.';
            bal_data.description = 'Phải thu về cho vay ngắn hạn';
            bal_data.code = '135';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '12831', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '12831', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 13. lấy chỉ tiêu 136
            bal_data.seq = 15;
            bal_data.line_no = '6.';
            bal_data.description = 'Phải thu ngắn hạn khác';
            bal_data.code = '136';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '13851 13881 33411 33481 33811 33821 33831 33841 33851 33861 33871 33881 1411 2441', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '13851 13881 33411 33481 33811 33821 33831 33841 33851 33861 33871 33881 1411 2441', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 14. lấy chỉ tiêu 137
            bal_data.seq = 16;
            bal_data.line_no = '7.';
            bal_data.description = 'Dự phòng phải thu ngắn hạn khó đòi (*)';
            bal_data.code = '137';
            bal_data.illustrate = null;
            bal_data.prior_amount = -1*fin_get_balance_all(prior_sdate, prior_edate, '22931', 'cr', $4);
            bal_data.current_amount = -1*fin_get_balance_all(_cur_sdate, _cur_edate, '22931', 'cr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 15. lấy chỉ tiêu 139
            bal_data.seq = 17;
            bal_data.line_no = '8.';
            bal_data.description = 'Tài sản thiếu chờ xử lý';
            bal_data.code = '139';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '1381', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '1381', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 16. lấy chỉ tiêu 130 = 131 + 132 + 133 + 134 + 135 + 136 + 137 + 139
            bal_data.seq = 9;
            bal_data.line_no = 'III.';
            bal_data.description = 'Các khoản phải thu ngắn hạn';
            bal_data.code = '130';
            bal_data.illustrate = null;
            bal_data.prior_amount = prior_grp2;
            bal_data.current_amount = curr_grp2;
            bal_data.type = 1;
            bal_data.format = 1;
            return next bal_data;
            
            -- ===== Muc IV =====
            prior_grp2 = 0;    curr_grp2 = 0;
            -- 17. lấy chỉ tiêu 141
            bal_data.seq = 19;
            bal_data.line_no = '1.';
            bal_data.description = 'Hàng tồn kho';
            bal_data.code = '141';
            bal_data.illustrate = '';
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '151 152 153 1541 156 157 158', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '151 152 153 1541 156 157 158', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 18. lấy chỉ tiêu 149 
            bal_data.seq = 20;
            bal_data.line_no = '2.';
            bal_data.description = 'Dự phòng giảm giá hàng tồn kho (*)';
            bal_data.code = '149';
            bal_data.illustrate = null;
            bal_data.prior_amount = -1*fin_get_balance_all(prior_sdate, prior_edate, '2294', 'cr', $4);
            bal_data.current_amount = -1*fin_get_balance_all(_cur_sdate, _cur_edate, '2294', 'cr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 19. lấy chỉ tiêu 140 = 141 + 149
            bal_data.seq = 18;
            bal_data.line_no = 'IV.';
            bal_data.description = 'Hàng tồn kho';
            bal_data.code = '140';
            bal_data.illustrate = null;
            bal_data.prior_amount = prior_grp2;
            bal_data.current_amount = curr_grp2;
            bal_data.type = 1;
            bal_data.format = 1;
            return next bal_data;
            
            -- ===== Muc V =====
            prior_grp2 = 0;    curr_grp2 = 0;
            -- 20. lấy chỉ tiêu 151
            bal_data.seq = 22;
            bal_data.line_no = '1.';
            bal_data.description = 'Chi phí trả trước ngắn hạn';
            bal_data.code = '151';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '2421', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '2421', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 21. lấy chỉ tiêu 152
            bal_data.seq = 23;
            bal_data.line_no = '2.';
            bal_data.description = 'Thuế GTGT được khấu trừ';
            bal_data.code = '152';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '133', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '133', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 22. lấy chỉ tiêu 153
            bal_data.seq = 24;
            bal_data.line_no = '3.';
            bal_data.description = 'Thuế và các khoản khác phải thu Nhà nước';
            bal_data.code = '153';
            bal_data.illustrate = '';
            bal_data.prior_amount = fin_get_detailsbalance(prior_sdate, prior_edate, '333', 'dr', $4);
            bal_data.current_amount = fin_get_detailsbalance(_cur_sdate, _cur_edate, '333', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 23. lấy chỉ tiêu 154
            bal_data.seq = 25;
            bal_data.line_no = '4.';
            bal_data.description = 'Giao dịch mua bán lại trái phiếu Chính phủ';
            bal_data.code = '154';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '171', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '171', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 24. lấy chỉ tiêu 155
            bal_data.seq = 26;
            bal_data.line_no = '4.';
            bal_data.description = 'Tài sản ngắn hạn khác';
            bal_data.code = '155';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '2288', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '2288', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 25. lấy chỉ tiêu 150 = 151 + 152 + 154 + 155
            bal_data.seq = 21;
            bal_data.line_no = 'V.';
            bal_data.description = 'Tài sản ngắn hạn khác';
            bal_data.code = '150';
            bal_data.illustrate = null;
            bal_data.prior_amount = prior_grp2;
            bal_data.current_amount = curr_grp2;
            bal_data.type = 1;
            bal_data.format = 1;
            return next bal_data;
            
            -- 26. lấy chỉ tiêu 100 = 110 + 120 + 130 + 140 + 150
            bal_data.seq = 1;
            bal_data.line_no = 'A-';
            bal_data.description = 'TÀI SẢN NGẮN HẠN';
            bal_data.code = '100';
            bal_data.illustrate = null;
            bal_data.prior_amount = prior_grp1;
            bal_data.current_amount = curr_grp1;
            bal_data.type = 1;
            bal_data.format = 1;
            return next bal_data;
            
            -- === B. TÀI SẢN DÀI HẠN ===
            prior_all = prior_grp1;    curr_all = curr_grp1;
            prior_grp1 = 0;    curr_grp1 = 0;
            -- ===== Muc I =====
            prior_grp2 = 0;    curr_grp2 = 0;
            
            -- 27. lấy chỉ tiêu 211
            bal_data.seq = 29;
            bal_data.line_no = '1.';
            bal_data.description = 'Phải thu dài hạn của khách hàng';
            bal_data.code = '211';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '1312', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '1312', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 28. lấy chỉ tiêu 212
            bal_data.seq = 30;
            bal_data.line_no = '2.';
            bal_data.description = 'Trả trước cho người bán dài hạn';
            bal_data.code = '212';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '3312', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '3312', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 29. lấy chỉ tiêu 213
            bal_data.seq = 31;
            bal_data.line_no = '3.';
            bal_data.description = 'Vốn kinh doanh ở đơn vị trực thuộc';
            bal_data.code = '213';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '1361', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '1361', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 30. lấy chỉ tiêu 214
            bal_data.seq = 32;
            bal_data.line_no = '4.';
            bal_data.description = 'Phải thu dài hạn nội bộ';
            bal_data.code = '214';
            bal_data.illustrate = '';
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '13622 13632 13682', 'dr', $4) -
                                    fin_get_balance_all(prior_sdate, prior_edate, '33622 33632 33682', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '13622 13632 13682', 'dr', $4) -
                                    fin_get_balance_all(_cur_sdate, _cur_edate, '33622 33632 33682', 'cr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 31. lấy chỉ tiêu 215
            bal_data.seq = 33;
            bal_data.line_no = '5.';
            bal_data.description = 'Phải thu về cho vay dài hạn';
            bal_data.code = '215';
            bal_data.illustrate = '';
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '12832', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '12832', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 32. lấy chỉ tiêu 216 hỏi lại
            bal_data.seq = 34;
            bal_data.line_no = '6.';
            bal_data.description = 'Phải thu dài hạn khác';
            bal_data.code = '219';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '13852 13882 33412 33482 33812 33822 33832 33842 33852 33862 33872 33882 1412 2442', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '13852 13882 33412 33482 33812 33822 33832 33842 33852 33862 33872 33882 1412 2442', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 33. lấy chỉ tiêu 219
            bal_data.seq = 35;
            bal_data.line_no = '7.';
            bal_data.description = 'Dự phòng phải thu dài hạn khó đòi (*)';
            bal_data.code = '219';
            bal_data.illustrate = null;
            bal_data.prior_amount = -1*fin_get_balance_all(prior_sdate, prior_edate, '22932', 'cr', $4);
            bal_data.current_amount = -1*fin_get_balance_all(_cur_sdate, _cur_edate, '22932', 'cr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 34. lấy chỉ tiêu 210 = 211 + 212 + 213 + 214 + 215 + 216 +219
            bal_data.seq = 28;
            bal_data.line_no = 'I.';
            bal_data.description = 'Các khoản phải thu dài hạn';
            bal_data.code = '210';
            bal_data.illustrate = null;
            bal_data.prior_amount = prior_grp2;
            bal_data.current_amount = curr_grp2;
            bal_data.type = 1;
            bal_data.format = 1;
            return next bal_data;
        
            -- ===== Muc II =====
            prior_grp2 = 0;    curr_grp2 = 0;
            
            -- 35. lấy chỉ tiêu 222
            prior_grp3 = 0;    curr_grp3 = 0;
            
            bal_data.seq = 38;
            bal_data.line_no = null;
            bal_data.description = '- Nguyên giá';
            bal_data.code = '222';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '211', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '211', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 2;
            
            prior_grp3 = prior_grp3 + bal_data.prior_amount;
            curr_grp3 = curr_grp3 + bal_data.current_amount;
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 36. lấy chỉ tiêu 223
            bal_data.seq = 39;
            bal_data.line_no = null;
            bal_data.description = '- Giá trị hao mòn lũy kế (*)';
            bal_data.code = '223';
            bal_data.illustrate = null;
            bal_data.prior_amount = -1*fin_get_balance_all(prior_sdate, prior_edate, '2141', 'cr', $4);
            bal_data.current_amount = -1*fin_get_balance_all(_cur_sdate, _cur_edate, '2141', 'cr', $4);
            bal_data.type = 1;
            bal_data.format = 2;
            
            prior_grp3 = prior_grp3 + bal_data.prior_amount;
            curr_grp3 = curr_grp3 + bal_data.current_amount;
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 37. lấy chỉ tiêu 221
            bal_data.seq = 37;
            bal_data.line_no = '1.';
            bal_data.description = 'Tài sản cố định hữu hình';
            bal_data.code = '221';
            bal_data.illustrate = '';
            bal_data.prior_amount = prior_grp3;
            bal_data.current_amount = curr_grp3;
            bal_data.type = 1;
            bal_data.format = 0;
            return next bal_data;
            
            -- 38. lấy chỉ tiêu 225
            prior_grp3 = 0;    curr_grp3 = 0;
            
            bal_data.seq = 41;
            bal_data.line_no = null;
            bal_data.description = '- Nguyên giá';
            bal_data.code = '225';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '212', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '212', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 2;
            
            prior_grp3 = prior_grp3 + bal_data.prior_amount;
            curr_grp3 = curr_grp3 + bal_data.current_amount;
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 39. lấy chỉ tiêu 226
            bal_data.seq = 42;
            bal_data.line_no = null;
            bal_data.description = '- Giá trị hao mòn lũy kế (*)';
            bal_data.code = '226';
            bal_data.illustrate = null;
            bal_data.prior_amount = -1*fin_get_balance_all(prior_sdate, prior_edate, '2142', 'cr', $4);
            bal_data.current_amount = -1*fin_get_balance_all(_cur_sdate, _cur_edate, '2142', 'cr', $4);
            bal_data.type = 1;
            bal_data.format = 2;
            
            prior_grp3 = prior_grp3 + bal_data.prior_amount;
            curr_grp3 = curr_grp3 + bal_data.current_amount;
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 40. lấy chỉ tiêu 224
            bal_data.seq = 40;
            bal_data.line_no = '2.';
            bal_data.description = 'Tài sản cố định thuê tài chính';
            bal_data.code = '224';
            bal_data.illustrate = '';
            bal_data.prior_amount = prior_grp3;
            bal_data.current_amount = curr_grp3;
            bal_data.type = 1;
            bal_data.format = 0;
            return next bal_data;
            
            -- 41. lấy chỉ tiêu 228
            prior_grp3 = 0;    curr_grp3 = 0;
            
            bal_data.seq = 44;
            bal_data.line_no = null;
            bal_data.description = '- Nguyên giá';
            bal_data.code = '228';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '213', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '213', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 2;
            
            prior_grp3 = prior_grp3 + bal_data.prior_amount;
            curr_grp3 = curr_grp3 + bal_data.current_amount;
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 42. lấy chỉ tiêu 229
            bal_data.seq = 45;
            bal_data.line_no = null;
            bal_data.description = '- Giá trị hao mòn lũy kế (*)';
            bal_data.code = '229';
            bal_data.illustrate = null;
            bal_data.prior_amount = -1*fin_get_balance_all(prior_sdate, prior_edate, '2143', 'cr', $4);
            bal_data.current_amount = -1*fin_get_balance_all(_cur_sdate, _cur_edate, '2143', 'cr', $4);
            bal_data.type = 1;
            bal_data.format = 2;
            
            prior_grp3 = prior_grp3 + bal_data.prior_amount;
            curr_grp3 = curr_grp3 + bal_data.current_amount;
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 43. lấy chỉ tiêu 227
            bal_data.seq = 43;
            bal_data.line_no = '3.';
            bal_data.description = 'Tài sản cố định vô hình';
            bal_data.code = '227';
            bal_data.illustrate = '';
            bal_data.prior_amount = prior_grp3;
            bal_data.current_amount = curr_grp3;
            bal_data.type = 1;
            bal_data.format = 0;
            return next bal_data;
            
            -- 44. lấy chỉ tiêu 220 = 221 + 224 + 227
            bal_data.seq = 36;
            bal_data.line_no = 'II.';
            bal_data.description = 'Tài sản cố định';
            bal_data.code = '220';
            bal_data.illustrate = null;
            bal_data.prior_amount = prior_grp2;
            bal_data.current_amount = curr_grp2;
            bal_data.type = 1;
            bal_data.format = 1;
            return next bal_data;
            
            -- ===== Muc III =====
            prior_grp2 = 0;    curr_grp2 = 0;
            
            -- 45. lấy chỉ tiêu 231
            bal_data.seq = 47;
            bal_data.line_no = null;
            bal_data.description = '- Nguyên giá';
            bal_data.code = '231';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '217', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '217', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 2;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 46. lấy chỉ tiêu 232
            bal_data.seq = 48;
            bal_data.line_no = null;
            bal_data.description = '- Giá trị hao mòn lũy kế (*)';
            bal_data.code = '232';
            bal_data.illustrate = null;
            bal_data.prior_amount = -1*fin_get_balance_all(prior_sdate, prior_edate, '2147', 'cr', $4);
            bal_data.current_amount = -1*fin_get_balance_all(_cur_sdate, _cur_edate, '2147', 'cr', $4);
            bal_data.type = 1;
            bal_data.format = 2;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 47. lấy chỉ tiêu 230 = 231 + 232
            bal_data.seq = 46;
            bal_data.line_no = 'III.';
            bal_data.description = 'Bất động sản đầu tư';
            bal_data.code = '230';
            bal_data.illustrate = '';
            bal_data.prior_amount = prior_grp2;
            bal_data.current_amount = curr_grp2;
            bal_data.type = 1;
            bal_data.format = 1;
            return next bal_data;
            
            -- ===== Muc IV =====
            prior_grp2 = 0;    curr_grp2 = 0;
            
            -- 48. lấy chỉ tiêu 241
            bal_data.seq = 50;
            bal_data.line_no = '1.';
            bal_data.description = 'Chi phí sản xuất kinh doanh dở dang dài hạn';
            bal_data.code = '241';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '1542', 'dr', $4) - fin_get_balance_all(prior_sdate, prior_edate, '2294', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '1542', 'dr', $4) - fin_get_balance_all(_cur_sdate, _cur_edate, '2294', 'cr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 49. lấy chỉ tiêu 242
            bal_data.seq = 51;
            bal_data.line_no = '2.';
            bal_data.description = 'Chi phí xây dựng cơ bản dở dang';
            bal_data.code = '242';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '241', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(prior_sdate, prior_edate, '241', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 50. lấy chỉ tiêu 240 = 241 + 242
            bal_data.seq = 49;
            bal_data.line_no = 'IV.';
            bal_data.description = 'Tài sản dở dang dài hạn';
            bal_data.code = '240';
            bal_data.illustrate = '';
            bal_data.prior_amount = prior_grp2;
            bal_data.current_amount = curr_grp2;
            bal_data.type = 1;
            bal_data.format = 1;
            return next bal_data;
            
            -- ===== Muc V =====
            prior_grp2 = 0;    curr_grp2 = 0;
            
            -- 51. lấy chỉ tiêu 251
            bal_data.seq = 53;
            bal_data.line_no = '1.';
            bal_data.description = 'Đầu tư vào công ty con';
            bal_data.code = '251';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '221', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '221', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 52. lấy chỉ tiêu 252
            bal_data.seq = 54;
            bal_data.line_no = '2.';
            bal_data.description = 'Đầu tư vào công ty liên doanh, liên kết';
            bal_data.code = '252';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '222', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '222', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 53. lấy chỉ tiêu 253
            bal_data.seq = 55;
            bal_data.line_no = '3.';
            bal_data.description = 'Đầu tư góp vốn vào đơn vị khác';
            bal_data.code = '253';
            bal_data.illustrate = '';
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '2281', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '2281', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 54. lấy chỉ tiêu 254
            bal_data.seq = 56;
            bal_data.line_no = '4.';
            bal_data.description = 'Dự phòng giảm giá đầu tư tài chính dài hạn (*)';
            bal_data.code = '254';
            bal_data.illustrate = null;
            bal_data.prior_amount = -1*fin_get_balance_all(prior_sdate, prior_edate, '2292', 'dr', $4);
            bal_data.current_amount = -1*fin_get_balance_all(_cur_sdate, _cur_edate, '2292', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 55. lấy chỉ tiêu 255
            bal_data.seq = 57;
            bal_data.line_no = '5.';
            bal_data.description = 'Đầu tư nắm giữ đến ngày đáo hạn';
            bal_data.code = '255';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '12813 12822 12883', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '12813 12822 12883', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 56. lấy chỉ tiêu 250 = 251 + 252 + 253 + 254 + 255
            bal_data.seq = 52;
            bal_data.line_no = 'V.';
            bal_data.description = 'Đầu tư tài chính dài hạn';
            bal_data.code = '250';
            bal_data.illustrate = null;
            bal_data.prior_amount = prior_grp2;
            bal_data.current_amount = curr_grp2;
            bal_data.type = 1;
            bal_data.format = 1;
            return next bal_data;
            
            -- ===== Muc VI =====
            prior_grp2 = 0;    curr_grp2 = 0;
            
            -- 57. lấy chỉ tiêu 261
            bal_data.seq = 59;
            bal_data.line_no = '1.';
            bal_data.description = 'Chi phí trả trước dài hạn';
            bal_data.code = '261';
            bal_data.illustrate = '';
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '2422', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '2422', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 58. lấy chỉ tiêu 262
            bal_data.seq = 60;
            bal_data.line_no = '2.';
            bal_data.description = 'Tài sản thuế thu nhập hoãn lại';
            bal_data.code = '262';
            bal_data.illustrate = '';
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '243', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '243', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 59. lấy chỉ tiêu 263
            bal_data.seq = 61;
            bal_data.line_no = '3.';
            bal_data.description = 'Thiết bị, vật tư, phụ tùng thay thế dài hạn';
            bal_data.code = '263';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '1534', 'dr', $4) - fin_get_balance_all(prior_sdate, prior_edate, '2294', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '1534', 'dr', $4) - fin_get_balance_all(_cur_sdate, _cur_edate, '2294', 'cr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 60. lấy chỉ tiêu 268
            bal_data.seq = 62;
            bal_data.line_no = '4.';
            bal_data.description = 'Tài sản dài hạn khác';
            bal_data.code = '268';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '2288', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '2288', 'dr', $4);
            bal_data.type = 1;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 61. lấy chỉ tiêu 260 = 261 + 262 + 263 + 268
            bal_data.seq = 58;
            bal_data.line_no = 'VI.';
            bal_data.description = 'Tài sản dài hạn khác';
            bal_data.code = '260';
            bal_data.illustrate = null;
            bal_data.prior_amount = prior_grp2;
            bal_data.current_amount = curr_grp2;
            bal_data.type = 1;
            bal_data.format = 1;
            return next bal_data;
            
            -- 62. lấy chỉ tiêu 200 = 210 + 220 + 230 + 240 + 250 + 260
            bal_data.seq = 27;
            bal_data.line_no = 'B-';
            bal_data.description = 'TÀI SẢN DÀI HẠN';
            bal_data.code = '200';
            bal_data.illustrate = null;
            bal_data.prior_amount = prior_grp1;
            bal_data.current_amount = curr_grp1;
            bal_data.type = 1;
            bal_data.format = 1;
            return next bal_data;
            
            -- 63. lấy chỉ tiêu 270 (TS Total) = 100 + 200
            bal_data.seq = 63;
            bal_data.line_no = null;
            bal_data.description = 'TỔNG CỘNG TÀI SẢN';
            bal_data.code = '270';
            bal_data.illustrate = null;
            bal_data.prior_amount = prior_all + prior_grp1;
            bal_data.current_amount = curr_all + curr_grp1;
            bal_data.type = 1;
            bal_data.format = 1;
            return next bal_data;
            /* =====    END TÀI SẢN    ===== */
            return;
        END; $BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100
          ROWS 1000;
        ALTER FUNCTION fin_balance_sheet_report_ts(date, date, character varying, integer)
          OWNER TO openerp;
        '''
        return sql
    
    def get_sql_nv(self):
        sql = '''
        DROP FUNCTION IF EXISTS fin_balance_sheet_report_nv(date, date, character varying, integer) CASCADE;
        commit;
        
        CREATE OR REPLACE FUNCTION fin_balance_sheet_report_nv(date, date, character varying, integer)
          RETURNS SETOF fin_balance_data AS
        $BODY$
        DECLARE
            _cur_sdate    alias for $1;
            _cur_edate    alias for $2;
            _type        alias for $3;
            rec_pl        record;
            bal_data    fin_balance_data%ROWTYPE;
            prior_sdate    date;
            prior_edate    date;
            
            prior_all    numeric = 0;
            curr_all    numeric = 0;
            prior_grp1    numeric = 0;
            curr_grp1    numeric = 0;
            prior_grp2    numeric;
            curr_grp2    numeric;
            prior_grp3    numeric;
            curr_grp3    numeric;
        BEGIN
            select * into prior_sdate,prior_edate from fn_get_prior_rangedate(_cur_sdate, _type);
            RAISE NOTICE 'Prior date range: % - %', prior_sdate, prior_edate;
            
            /*    Lấy số liệu phần NGUỒN VỐN    */
            -- === C. NỢ PHẢI TRẢ ===
            prior_grp1 = 0;    curr_grp1 = 0;
            -- ===== Muc I =====
            prior_grp2 = 0;    curr_grp2 = 0;
            
            -- 64 lấy chỉ tiêu 311
            bal_data.seq = 66;
            bal_data.line_no = '1.';
            bal_data.description = 'Phải trả người bán ngắn hạn';
            bal_data.code = '311';
            bal_data.illustrate = '';
            bal_data.prior_amount = fin_get_balance_cr(prior_sdate, prior_edate, '3311', $4);
            bal_data.current_amount = fin_get_balance_cr(_cur_sdate, _cur_edate, '3311', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 65. lấy chỉ tiêu 312
            bal_data.seq = 67;
            bal_data.line_no = '2.';
            bal_data.description = 'Người mua trả tiền trước ngắn hạn';
            bal_data.code = '312';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_cr(prior_sdate, prior_edate, '1311', $4);
            bal_data.current_amount = fin_get_balance_cr(_cur_sdate, _cur_edate, '1311', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 66. lấy chỉ tiêu 313
            bal_data.seq = 68;
            bal_data.line_no = '3.';
            bal_data.description = 'Thuế và các khoản phải nộp Nhà nước';
            bal_data.code = '313';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_detailsbalance(prior_sdate, prior_edate, '333', 'cr', $4);
            bal_data.current_amount = fin_get_detailsbalance(_cur_sdate, _cur_edate, '333', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;

            -- 67. lấy chỉ tiêu 314
            bal_data.seq = 69;
            bal_data.line_no = '4.';
            bal_data.description = 'Phải trả người lao động';
            bal_data.code = '314';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '334', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '334', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 68. lấy chỉ tiêu 315
            bal_data.seq = 70;
            bal_data.line_no = '5.';
            bal_data.description = 'Chi phí phải trả ngắn hạn';
            bal_data.code = '315';
            bal_data.illustrate = '';
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '3351', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '3351', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 69. lấy chỉ tiêu 316
            bal_data.seq = 71;
            bal_data.line_no = '6.';
            bal_data.description = 'Phải trả nội bộ ngắn hạn';
            bal_data.code = '316';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '33621 33631 33681', 'cr', $4) -
                                    fin_get_balance_all(prior_sdate, prior_edate, '13621 13631 13681', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '33621 33631 33681', 'cr', $4) -
                                    fin_get_balance_all(_cur_sdate, _cur_edate, '13621 13631 13681', 'dr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 70. lấy chỉ tiêu 317
            bal_data.seq = 72;
            bal_data.line_no = '7.';
            bal_data.description = 'Phải trả theo tiến độ kế hoạch hợp đồng xây dựng';
            bal_data.code = '317';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_cr(prior_sdate, prior_edate, '337', $4);
            bal_data.current_amount = fin_get_balance_cr(_cur_sdate, _cur_edate, '337', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 71. lấy chỉ tiêu 318
            bal_data.seq = 73;
            bal_data.line_no = '8.';
            bal_data.description = 'Doanh thu chưa thực hiện ngắn hạn';
            bal_data.code = '318';
            bal_data.illustrate = '';
            bal_data.prior_amount = fin_get_detailsbalance(prior_sdate, prior_edate, '33871', 'cr', $4);
            bal_data.current_amount = fin_get_detailsbalance(_cur_sdate, _cur_edate, '33871', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 72. lấy chỉ tiêu 319
            bal_data.seq = 74;
            bal_data.line_no = '9.';
            bal_data.description = 'Phải trả ngắn hạn khác';
            bal_data.code = '319';
            bal_data.illustrate = '';
            bal_data.prior_amount = fin_get_detailsbalance(prior_sdate, prior_edate, '33811 33821 33821 33831 33841 33851 33861 33871 33881 138 33411 33481', 'cr', $4);
            bal_data.current_amount = fin_get_detailsbalance(_cur_sdate, _cur_edate, '33811 33821 33821 33831 33841 33851 33861 33871 33881 138 33411 33481', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 73. lấy chỉ tiêu 320
            bal_data.seq = 75;
            bal_data.line_no = '10.';
            bal_data.description = 'Vay và nợ thuê tài chính ngắn hạn';
            bal_data.code = '320';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '341 3431', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '341 3431', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 74. lấy chỉ tiêu 321
            bal_data.seq = 76;
            bal_data.line_no = '11.';
            bal_data.description = 'Dự phòng phải trả ngắn hạn';
            bal_data.code = '321';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_detailsbalance(prior_sdate, prior_edate, '35211 35221 35231 35241', 'cr', $4);
            bal_data.current_amount = fin_get_detailsbalance(_cur_sdate, _cur_edate, '35211 35221 35231 35241', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 75. lấy chỉ tiêu 322
            bal_data.seq = 77;
            bal_data.line_no = '12.';
            bal_data.description = 'Quỹ khen thưởng phúc lợi';
            bal_data.code = '322';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '353', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '353', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 76. lấy chỉ tiêu 323
            bal_data.seq = 78;
            bal_data.line_no = '13.';
            bal_data.description = 'Quỹ bình ổn giá';
            bal_data.code = '323';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '357', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '357', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 77. lấy chỉ tiêu 324
            bal_data.seq = 79;
            bal_data.line_no = '14.';
            bal_data.description = 'Giao dịch mua bán lại trái phiếu Chính phủ';
            bal_data.code = '324';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '171', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '171', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 78. lấy chỉ tiêu 310 = 311 + 312 + 313 + 314 + 315 + 316 + 317 + 318 + 319 + 320 + 321 + 322 + 323 + 324
            bal_data.seq = 65;
            bal_data.line_no = 'I.';
            bal_data.description = 'Nợ ngắn hạn';
            bal_data.code = '310';
            bal_data.illustrate = null;
            bal_data.prior_amount = prior_grp2;
            bal_data.current_amount = curr_grp2;
            bal_data.type = 2;
            bal_data.format = 1;
            return next bal_data;
            
            -- ===== Muc II =====
            prior_grp2 = 0;    curr_grp2 = 0;
            
            -- 79. lấy chỉ tiêu 331
            bal_data.seq = 81;
            bal_data.line_no = '1.';
            bal_data.description = 'Phải trả người bán dài hạn';
            bal_data.code = '331';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_cr(prior_sdate, prior_edate, '3312', $4);
            bal_data.current_amount = fin_get_balance_cr(_cur_sdate, _cur_edate, '3312', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
        
            -- 80. lấy chỉ tiêu 332
            bal_data.seq = 82;
            bal_data.line_no = '2.';
            bal_data.description = 'Người mua trả tiền trước dài hạn';
            bal_data.code = '332';
            bal_data.illustrate = '';
            bal_data.prior_amount = fin_get_balance_cr(prior_sdate, prior_edate, '1312', $4);
            bal_data.current_amount = fin_get_balance_cr(_cur_sdate, _cur_edate, '1312', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 81. lấy chỉ tiêu 333
            bal_data.seq = 83;
            bal_data.line_no = '3.';
            bal_data.description = 'Chi phí phải trả dài hạn';
            bal_data.code = '333';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '3352', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '3352', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 82. lấy chỉ tiêu 334
            bal_data.seq = 84;
            bal_data.line_no = '4.';
            bal_data.description = 'Phải trả nội bộ về vốn kinh doanh';
            bal_data.code = '334';
            bal_data.illustrate = '';
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '3361', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(prior_sdate, prior_edate, '3361', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 83. lấy chỉ tiêu 335
            bal_data.seq = 85;
            bal_data.line_no = '5.';
            bal_data.description = 'Phải trả nội bộ dài hạn';
            bal_data.code = '335';
            bal_data.illustrate = '';
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '33622 33632 33682', 'cr', $4) -
                                    fin_get_balance_all(prior_sdate, prior_edate, '13622 13632 13682', 'dr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '33622 33632 33682', 'cr', $4) -
                                    fin_get_balance_all(_cur_sdate, _cur_edate, '13622 13632 13682', 'dr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 84. lấy chỉ tiêu 336
            bal_data.seq = 86;
            bal_data.line_no = '6.';
            bal_data.description = 'Doanh thu chưa thực hiện dài hạn';
            bal_data.code = '336';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '33872', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '33872', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 85. lấy chỉ tiêu 337
            bal_data.seq = 87;
            bal_data.line_no = '7.';
            bal_data.description = 'Phải trả dài hạn khác';
            bal_data.code = '337';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '33812 33822 33832 33842 33852 33862 33872 33882 33412 33482' , 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '33812 33822 33832 33842 33852 33862 33872 33882 33412 33482', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 86. lấy chỉ tiêu 338
            bal_data.seq = 88;
            bal_data.line_no = '8.';
            bal_data.description = 'Vay và nợ thuê tài chính dài hạn';
            bal_data.code = '338';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '341', 'cr', $4) +
                                    fin_get_balance_all(prior_sdate, prior_edate, '34311', 'cr', $4) - 
                                    fin_get_balance_all(prior_sdate, prior_edate, '34312', 'dr', $4) +
                                    fin_get_balance_all(prior_sdate, prior_edate, '34313', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '341', 'cr', $4)+
                                      fin_get_balance_all(_cur_sdate, _cur_edate, '34311', 'cr', $4) - 
                                      fin_get_balance_all(_cur_sdate, _cur_edate, '34312', 'dr', $4) +
                                      fin_get_balance_all(_cur_sdate, _cur_edate, '34313', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 87. lấy chỉ tiêu 339
            bal_data.seq = 89;
            bal_data.line_no = '9.';
            bal_data.description = 'Trái phiếu chuyển đổi';
            bal_data.code = '339';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '3432', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '3432', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 88. lấy chỉ tiêu 340
            bal_data.seq = 90;
            bal_data.line_no = '10.';
            bal_data.description = 'Cổ phiếu ưu đãi';
            bal_data.code = '340';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '411121', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '411121', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 89. lấy chỉ tiêu 341
            bal_data.seq = 91;
            bal_data.line_no = '11.';
            bal_data.description = 'Thuế thu nhập hoãn lại phải trả';
            bal_data.code = '341';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '347', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '347', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 90. lấy chỉ tiêu 342
            bal_data.seq = 92;
            bal_data.line_no = '12.';
            bal_data.description = 'Dự phòng phải trả dài hạn';
            bal_data.code = '342';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '3522', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '3522', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 91. lấy chỉ tiêu 343
            bal_data.seq = 93;
            bal_data.line_no = '13.';
            bal_data.description = 'Quỹ phát triển khoa học và công nghệ';
            bal_data.code = '343';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '356', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '356', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 92. lấy chỉ tiêu 330 = 331 + 332 + 333 + 334 + 335 + 336 + 337 + 338 + 339 + 340 + 341 + 342 + 343
            bal_data.seq = 80;
            bal_data.line_no = 'II.';
            bal_data.description = 'Nợ dài hạn';
            bal_data.code = '330';
            bal_data.illustrate = null;
            bal_data.prior_amount = prior_grp2;
            bal_data.current_amount = curr_grp2;
            bal_data.type = 2;
            bal_data.format = 1;
            return next bal_data;
            
            -- 93. lấy chỉ tiêu 300 = 310 + 330
            bal_data.seq = 64;
            bal_data.line_no = 'C-';
            bal_data.description = 'NỢ PHẢI TRẢ';
            bal_data.code = '300';
            bal_data.illustrate = null;
            bal_data.prior_amount = prior_grp1;
            bal_data.current_amount = curr_grp1;
            bal_data.type = 2;
            bal_data.format = 1;
            return next bal_data;
            
            -- === D. VỐN CHỦ SỞ HỮU ===
            prior_all = prior_grp1;    curr_all = curr_grp1;
            prior_grp1 = 0;    curr_grp1 = 0;
            -- ===== Muc I =====
            prior_grp2 = 0;    curr_grp2 = 0;
            
            -- 94. lấy chỉ tiêu 411
            bal_data.seq = 96;
            bal_data.line_no = '1.';
            bal_data.description = 'Vốn đầu tư của chủ sở hữu';
            bal_data.code = '411';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '4111', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '4111', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 95. lấy chỉ tiêu 412
            bal_data.seq = 97;
            bal_data.line_no = '2.';
            bal_data.description = 'Thặng dư vốn cổ phần';
            bal_data.code = '412';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '4112', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '4112', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 96. lấy chỉ tiêu 413
            bal_data.seq = 98;
            bal_data.line_no = '3.';
            bal_data.description = 'Quyền chọn chuyển đổi trái phiếu';
            bal_data.code = '413';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '4113', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '4113', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 97. lấy chỉ tiêu 414
            bal_data.seq = 99;
            bal_data.line_no = '4.';
            bal_data.description = 'Vốn khác của chủ sở hữu';
            bal_data.code = '414';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '4118', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '4118', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 98. lấy chỉ tiêu 415
            bal_data.seq = 100;
            bal_data.line_no = '5.';
            bal_data.description = 'Cổ phiếu quỹ (*)';
            bal_data.code = '415';
            bal_data.illustrate = null;
            bal_data.prior_amount = -1*fin_get_balance_all(prior_sdate, prior_edate, '419', 'dr', $4);
            bal_data.current_amount = -1*fin_get_balance_all(_cur_sdate, _cur_edate, '419', 'dr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 99. lấy chỉ tiêu 416
            bal_data.seq = 101;
            bal_data.line_no = '6.';
            bal_data.description = 'Chênh lệch đánh giá lại tài sản';
            bal_data.code = '416';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '412', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '412', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 100. lấy chỉ tiêu 417
            bal_data.seq = 102;
            bal_data.line_no = '7.';
            bal_data.description = 'Chênh lệch tỷ giá hối đoái';
            bal_data.code = '417';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '413', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '413', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 101. lấy chỉ tiêu 418
            bal_data.seq = 103;
            bal_data.line_no = '8.';
            bal_data.description = 'Quỹ đầu tư phát triển';
            bal_data.code = '418';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '414', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '414', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 102. lấy chỉ tiêu 419
            bal_data.seq = 104;
            bal_data.line_no = '9.';
            bal_data.description = 'Quỹ hỗ trợ sắp xếp doanh nghiệp';
            bal_data.code = '419';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '417', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '417', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 103. lấy chỉ tiêu 420
            bal_data.seq = 105;
            bal_data.line_no = '10.';
            bal_data.description = 'Quỹ khác thuộc vốn chủ sở hữu';
            bal_data.code = '420';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '418', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '418', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 104. lấy chỉ tiêu 421
            bal_data.seq = 106;
            bal_data.line_no = '11.';
            bal_data.description = 'Lợi nhuận sau thuế chưa phân phối';
            bal_data.code = '421';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '421', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '421', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 105. lấy chỉ tiêu 421a
            bal_data.seq = 107;
            bal_data.line_no = null;
            bal_data.description = '- LST chưa phân phối lũy kế đến cuối kỳ trước';
            bal_data.code = '421a';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '4211', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '4211', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 106. lấy chỉ tiêu 421b
            bal_data.seq = 108;
            bal_data.line_no = null;
            bal_data.description = '- LST chưa phân phối kỳ này';
            bal_data.code = '421b';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '4212', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '4212', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 107. lấy chỉ tiêu 422
            bal_data.seq = 109;
            bal_data.line_no = '12.';
            bal_data.description = 'Nguồn vốn đầu tư XDCB';
            bal_data.code = '422';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '441', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '441', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 108. lấy chỉ tiêu 410 = 411 + 412 + 413 + 414 + 415 + 416 + 417 + 418 + 419 + 420 + 421 + 422
            bal_data.seq = 95;
            bal_data.line_no = 'I.';
            bal_data.description = 'Vốn chủ sở hữu';
            bal_data.code = '410';
            bal_data.illustrate = '';
            bal_data.prior_amount = prior_grp2;
            bal_data.current_amount = curr_grp2;
            bal_data.type = 2;
            bal_data.format = 1;
            return next bal_data;
            
            -- ===== Muc II =====
            prior_grp2 = 0;    curr_grp2 = 0;
            
            -- 109. lấy chỉ tiêu 431
            bal_data.seq = 111;
            bal_data.line_no = '1.';
            bal_data.description = 'Nguồn kinh phí';
            bal_data.code = '431';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_cr(prior_sdate, prior_edate, '461', $4) -
                                    fin_get_balance_dr(prior_sdate, prior_edate, '161', $4);
            bal_data.current_amount = fin_get_balance_cr(_cur_sdate, _cur_edate, '461', $4) -
                                    fin_get_balance_dr(_cur_sdate, _cur_edate, '161', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;
            
            -- 110. lấy chỉ tiêu 432
            bal_data.seq = 112;
            bal_data.line_no = '2.';
            bal_data.description = 'Nguồn kinh phí đã hình thành';
            bal_data.code = '432';
            bal_data.illustrate = null;
            bal_data.prior_amount = fin_get_balance_all(prior_sdate, prior_edate, '466', 'cr', $4);
            bal_data.current_amount = fin_get_balance_all(_cur_sdate, _cur_edate, '466', 'cr', $4);
            bal_data.type = 2;
            bal_data.format = 0;
            
            prior_grp2 = prior_grp2 + bal_data.prior_amount;
            curr_grp2 = curr_grp2 + bal_data.current_amount;
            prior_grp1 = prior_grp1 + bal_data.prior_amount;
            curr_grp1 = curr_grp1 + bal_data.current_amount;
            return next bal_data;

            -- 111. lấy chỉ tiêu 430 = 431 + 432
            bal_data.seq = 110;
            bal_data.line_no = 'II.';
            bal_data.description = 'Nguồn kinh phí và quỹ khác';
            bal_data.code = '430';
            bal_data.illustrate = null;
            bal_data.prior_amount = prior_grp2;
            bal_data.current_amount = curr_grp2;
            bal_data.type = 2;
            bal_data.format = 1;
            return next bal_data;
            
            -- 112. lấy chỉ tiêu 400 = 410 + 430
            bal_data.seq = 94;
            bal_data.line_no = 'D-';
            bal_data.description = 'VỐN CHỦ SỞ HỮU';
            bal_data.code = '400';
            bal_data.illustrate = null;
            bal_data.prior_amount = prior_grp1;
            bal_data.current_amount = curr_grp1;
            bal_data.type = 2;
            bal_data.format = 1;
            return next bal_data;
            
            -- 113. lấy chỉ tiêu 440 (NV Total) = 300 + 400
            bal_data.seq = 113;
            bal_data.line_no = null;
            bal_data.description = 'TỔNG CỘNG NGUỒN VỐN';
            bal_data.code = '440';
            bal_data.illustrate = null;
            bal_data.prior_amount = prior_all + prior_grp1;
            bal_data.current_amount = curr_all + curr_grp1;
            bal_data.type = 2;
            bal_data.format = 1;
            return next bal_data;
            /* =====    END NGUỒN VỐN    ===== */
            
            return;
        END; $BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100
          ROWS 1000;
        ALTER FUNCTION fin_balance_sheet_report_nv(date, date, character varying, integer)
          OWNER TO openerp;
        '''
        return sql
    
sql_balance_sheet()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
