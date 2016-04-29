# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _

class profile(osv.osv):
    _name = "profile"
    _description = "Profile"
    _columns = {
        'users_ids': fields.one2many('res.users', 'profile_id', string='Users', required=False, readonly=True),
        'name': fields.char('Profile Name', size=64, required=True),
        'groups_ids': fields.many2many('res.groups', 'profiles_groups_rel', 'profile_id', 'group_id', string='Groups', required=False, readonly=False),
    }
    _sql_constraints = [
        ('name_uniq', 'unique (name)',
            'The name of the profile must be unique!'),
    ]
    _order = "name"
    
    def copy(self, cr, uid, id, default=None, context=None):
        name = ''
        sql = '''
            SELECT name
            FROM profile
            WHERE id = %s
        '''
        cr.execute(sql, (id,))
        if cr.rowcount > 0:
            name = cr.fetchone()[0]
        default.update({'name': _('%s (copy)') % name, 'users_ids': []})        
        return super(profile, self).copy(cr, uid, id, default, context)
    
    def unlink(self, cr, uid, ids, context=None):
        user_ids = []
        for line in self.browse(cr, uid, ids):
            if line.users_ids:
                for user in line.users_ids:
                    user_ids.append(user.id)
        super(profile, self).unlink(cr, uid, ids, context)
        return self.update_groups(cr, uid, user_ids)
    
    def write(self, cr, uid, ids, vals, context=None):
        super(profile, self).write(cr, uid, ids, vals, context)
        for line in self.browse(cr, uid, ids):
            if line.users_ids:
                user_ids = [x.id for x in line.users_ids]
                self.update_groups(cr, uid, user_ids)
        return True
    
    def update_groups(self, cr, uid, uids):
        users_pool = self.pool.get('res.users')
        if uids:
            for user in users_pool.browse(cr, uid, uids):
                if not user.profile_id:
                    users_pool.write(cr, uid, [user.id], {'groups_id': [[6,0,[]]]})
                if user.profile_id and user.profile_id.groups_ids:
                    groups_ids = [x.id for x in user.profile_id.groups_ids]
                    users_pool.write(cr, uid, [user.id], {'groups_id': [[6,0,groups_ids]]})
                if user.id == 1:
                    sql = '''
                        DELETE
                        FROM res_groups_users_rel
                        WHERE uid = 1
                    '''
                    cr.execute(sql)
                    sql = '''
                        INSERT INTO res_groups_users_rel(uid, gid)
                        SELECT DISTINCT ru.id, rg.id
                        FROM res_users ru, res_groups rg
                        WHERE (ru.id = 1) 
                    '''
                    cr.execute(sql) 
#        try:
#            # firstly delete all groups information, ...
#            sql = '''
#                DELETE
#                FROM res_groups_users_rel
#                WHERE uid <> 1
#            '''
#            cr.execute(sql)
#            # ... then compute and insert all the groups information again. 
#            sql = '''
#                INSERT INTO res_groups_users_rel(uid, gid)
#                SELECT DISTINCT ru.id, rg.id
#                FROM res_users ru, res_groups rg
#                WHERE ru.id <> 1 AND EXISTS (
#                        SELECT 1
#                        FROM profiles_groups_rel
#                        WHERE group_id = rg.id AND 
#                            profile_id = ru.profile_id
#                        ) 
#            '''
#            cr.execute(sql)
#            
#        except:
#            pass
        return True
    
profile()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
