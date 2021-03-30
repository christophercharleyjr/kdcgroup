# -*- coding: utf-8 -*-
##############################################################################
#
#    Globalteckz Software Solutions
#    Copyright (C) 2004-2010 Globalteckz (<http:www.globalteckz.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError
class Partner(models.Model):
    _inherit = "res.partner"

    login = fields.Char(required=1)
    password = fields.Char(required=1)
    is_agent = fields.Boolean('Is Agent ?')
    is_tenant = fields.Boolean('Is Tenant ?')
    is_landlord = fields.Boolean('Is Landlord ?')


    @api.model
    def create(self, vals):
        # print ("cccccccccccccccccccc")
        name = self.search([('name', '=', vals['name'])])
        if name:
            raise UserError(_("User Already Exist With The Same Name."))
        
        partner = super(Partner, self).create(vals)
        user_obj = self.env['res.users']
        user_fields = user_obj.fields_get()
        default_value = user_obj.default_get(user_fields)

        # if self._context.get('agent'):
        #     default_value['groups_id'][0][2].append(self.env.ref('gt_rental_property_management.group_agent').id)
        #     partner.is_agent = True

        if not (self._context.get('worker') or self._context.get('default_customer')):
            # print ("11111111111111111111")
            if self._context.get('agent'):
                # print ("agenttttttttttttttt=========>>>>")
                agent = self.env.ref('gt_rental_property_management.group_agent').id
                employee = self.env.ref('base.group_user').id
                default_value['groups_id']=[(6, 0,[agent, employee])]
                partner.is_agent = True

            elif self._context.get('tenant'):
                # print ("tenantttttttttttttttt=========>>>>")
                tenant = self.env.ref('gt_rental_property_management.group_tenant').id
                employee = self.env.ref('base.group_user').id
                default_value['groups_id']=[(6, 0,[tenant, employee])]
                partner.is_tenant = True

            elif self._context.get('landlord'):
                # print ("landlordddddddddddddd=========>>>>")
                landlord = self.env.ref('gt_rental_property_management.group_landlord').id
                employee = self.env.ref('base.group_user').id
                default_value['groups_id'] = [(6, 0, [landlord, employee])]
                partner.is_landlord = True
                # partner.supplier = True
                

            default_value.update({'name':partner.name,
                                  'partner_id':partner.id,
                                  'login':partner.login,
                                  'password':partner.password,
                                  'user_id':self.env.user.id,
                                  # 'groups_id': [(6, 0, [group_user.id])]
                                  })
# 
            # print ("aaaalllllllllll11111111",default_value)
            user = user_obj.new(default_value)
            # print ("aaaalllllllllll22222222",user)
            user.sudo().create(default_value)


        if (self._context.get('worker') or self._context.get('default_customer')) :
            # print ("22222222222222222222222222222222222") 
            partner.update({
                              'name':partner.name,
                              })
            # print ("workerrrrrrrrrrrrrrrrrr",partner)
        return partner

    # @api.model
    # def create(self, vals):
    #     partner = super(Partner, self).create(vals)
    #     user_obj = self.env['res.users']
    #     user_fields = user_obj.fields_get()
    #     default_value = user_obj.default_get(user_fields)

    #     # if self._context.get('agent'):
    #     #     print ("agenttttttttttttt")
    #     #     default_value['groups_id'][0][2].append(self.env.ref('gt_rental_property_management.group_agent').id)
    #     #     partner.is_agent = True

    #     if self._context.get('agent'):
    #         # print ("agenttttttttttttttt=========>>>>")
    #         agent = self.env.ref('gt_rental_property_management.group_agent').id
    #         employee = self.env.ref('base.group_user').id
    #         default_value['groups_id']=[(6, 0,[agent, employee])]
    #         partner.is_agent = True

    #     elif self._context.get('tenant'):
    #         tenant = self.env.ref('gt_rental_property_management.group_tenant').id
    #         employee = self.env.ref('base.group_user').id
    #         default_value['groups_id']=[(6, 0,[tenant, employee])]
    #         partner.is_tenant = True

    #     elif self._context.get('landlord'):
    #         landlord = self.env.ref('gt_rental_property_management.group_landlord').id
    #         employee = self.env.ref('base.group_user').id
    #         default_value['groups_id'] = [(6, 0, [landlord, employee])]
    #         partner.is_landlord = True
    #         partner.supplier = True

    #     else:
    #         # print ("wwwwwwwwwwwwwwwwwwww") 
    #         employee = self.env.ref('base.group_user').id
    #         default_value['groups_id'] = [(6, 0, [employee])]

    #     default_value.update({'name':partner.name,
    #                           'partner_id':partner.id,
    #                           'login':partner.login,
    #                           'password':partner.password,
    #                           'user_id':self.env.user.id,
    #                           # 'groups_id': [(6, 0, [group_user.id])]
    #                           })
    #     user = user_obj.new(default_value)
    #     user.sudo().create(default_value)
    #     return partner


    @api.model
    def default_get(self, vals):
        res = super(Partner, self).default_get(vals)
        for rec in self.env.user:
            if rec.has_group('base.group_system'):
                # print ("adminnnnnnnnnnnnnDDDDDDDDDDDDD==========>>>>")
                continue

            if rec.has_group('gt_rental_property_management.group_agent') and self.env.context.get('agent')==True:
                # print ("agentTTTTTTTTTTTT==========>>>>")
                raise UserError(_("Only Administrator Is Allowed To Create Agents."))
        return res


    # @api.multi
    def write(self, vals):
        # print ("ResPart_wwwwwwwwwwwwwwwwwwwwwww",vals)
        # if vals:
        #     print ("valssssssResPart_wwwwwwwwwwwwww",vals)
        #     if vals.get('name'):
        #         print ("ifffffffffvals.get('name')",vals.get('name'))
        #         name = self.search([('name', '=', vals['name'])])
        #         if name:
        #             print ("NAMEEEEEEEEE",name)
        #             raise UserError(_("User Already Exist With The Same Name....."))

        result = super(Partner, self.sudo()).write(vals)
        if 'login' or 'password' in vals:
            # print ("VVVVVVVVVVVVVVVVVVVVVVVVVV",vals)
            user_object = self.env['res.users'].search([('partner_id', '=', self.id)])

            if vals.get('login'):
                user_object.sudo().write({'login':vals['login']})
            if vals.get('password'):
                user_object.sudo().write({'password':vals['password']})

        result = result and super(Partner, self.sudo()).write(vals)
        return result

    # access_res_partner_agent, access_res_partner_agent, model_res_partner, group_agent, 1, 1, 1, 1
    # access_res_partner_landlord, access_res_partner_landlord, model_res_partner, group_landlord, 1, 0, 0, 0
    # access_res_partner_tenant, access_res_partner_tenant, model_res_partner, group_tenant, 1, 0, 0, 0