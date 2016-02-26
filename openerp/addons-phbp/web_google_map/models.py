# -*- coding: utf-8 -*-

from openerp.osv import osv
from openerp.osv import fields
from math import radians, cos, sin, asin, sqrt


class res_partner(osv.osv):

    _inherit = 'res.partner'

    _columns = {
        'lat': fields.float(u'Latitude', digits=(9, 6)),
        'lng': fields.float(u'Longitude', digits=(9, 6)),
        'radius': fields.float(u'Radius', digits=(9, 16)),
        'map': fields.dummy(),
        'points': fields.text('Points'), 
        'mo_ta': fields.text('Mo ta'),
    }
    
    def write_radius(self, cr, uid, id,active_model, vals, context=None):
#         if vals.get('radius',False):
#             vals.update({'points':'10.793740,106.658763,Diem 1;10.795204,106.659119,Diem 2;10.794135,106.658044,Diem 3'})#10.793740,106.658763,Diem 1;10.795204,106.659119,Diem 2;10.794135,106.658044,Diem 3
#         self.pool.get(active_model).write(cr, uid, [int(id)], vals, context)
        if vals.get('radius',False) and active_model=='rp.google.map':
            gg_map_obj = self.pool.get('rp.google.map')
            line = gg_map_obj.browse(cr, uid, int(id))
            vals.update(gg_map_obj.onchange_toado_bankinh( cr, uid, [], line.lat, line.lng, vals['radius'],context)['value'])
            gg_map_obj.write(cr, uid, [int(id)], vals, context)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
         
    def write_center(self, cr, uid, id,active_model, vals, context=None):
#         if vals.get('center',False):
#             vals.update({'lat':vals['center']['G'],'lng':vals['center']['K']})#10.793740,106.658763,Diem 1;10.795204,106.659119,Diem 2;10.794135,106.658044,Diem 3
#         self.pool.get(active_model).write(cr, uid, [int(id)], vals, context)
        if vals.get('center',False) and active_model=='rp.google.map':
            gg_map_obj = self.pool.get('rp.google.map')
            line = gg_map_obj.browse(cr, uid, int(id))
            vals.update(gg_map_obj.onchange_toado_bankinh( cr, uid, [], vals['center']['lat'], vals['center']['lng'], line.radius,context)['value'])
            vals.update({'lat':vals['center']['lat'],'lng':vals['center']['lng']})
            gg_map_obj.write(cr, uid, [int(id)], vals, context)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
     
    def haversine(self,lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        km = 6367 * c
        return km
     
res_partner()

