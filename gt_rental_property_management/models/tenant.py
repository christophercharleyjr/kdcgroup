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

from odoo import api, models, fields, _
from odoo.exceptions import UserError

class TenantDetails(models.Model):
    _name = "tenant.details"

    @api.model
    def _get_partner(self):
        partners = self.env['res.partner'].sudo().search([])
        list_partner = []

        for partner in partners:
            if partner.user_id.id == self.env.user.id and partner.is_tenant == True:
                list_partner.append(partner.id)

        if len(list_partner) > 1:
            return [('id', 'in', list_partner)]
        elif len(list_partner) == 1:
            return [('id', '=', list_partner[0])]
        elif len(list_partner) == 0:
            return [('id', '=', -1)]


    # @api.model
    # def _get_user(self):
    #
    #     users = self.env['res.users'].sudo().search([])
    #     list_user = []
    #
    #     for user in users:
    #         if user.has_group('gt_rental_property_management.group_tenant'):
    #             list_user.append(user.id)
    #
    #     if len(list_user) > 1:
    #         return [('id', 'in', list_user)]
    #     elif len(list_user) == 1:
    #         return [('id', '=', list_user[0])]
    #     elif len(list_user) == 0:
    #         return [('id', '=', -1)]


    # name = fields.Many2one('res.partner',required = True,help='Choose Tenant. If not showing any then create User and assign group of Tenant.')
    name = fields.Many2one('res.partner', required= True ,domain=_get_partner,help='Choose Tenant. If not showing any then create User and assign group of Tenant.')
    # name = fields.Many2one('res.users',required = True, domain=_get_user,help='Choose Tenant. If not showing any then create User and assign group of Tenant.')
    gender = fields.Selection([('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], string="Gender")
    bdate = fields.Date("Date of Birth")
    # marital_status = fields.Selection([('s','Single'),('m','Married')],string="Marital Status")
    occupation = fields.Char()
    attchment = fields.Binary('Attachmen Document')
    phone_number = fields.Char(related='name.mobile', relation='res.partner', string='Phone Number', store=True,
                                 readonly=True)
    email_id = fields.Char(related='name.email', relation='res.partner', string='Email ID', store=True,
                                 readonly=True)
    street = fields.Char(related='name.street', relation='res.partner', string='Street', store=True, readonly=True)
    street2 = fields.Char(related='name.street2', relation='res.partner', string='Street2', store=True, readonly=True)
    zip = fields.Char(related='name.zip', relation='res.partner', string='ZIP', store=True, readonly=True)
    city = fields.Char(related='name.city', relation='res.partner', string='City', store=True, readonly=True)
    state_id = fields.Many2one(related='name.state_id', relation='res.partner', string='State', store=True,
                               readonly=True)
    country_id = fields.Many2one(related='name.country_id', relation='res.partner', string='Country', store=True,
                                 readonly=True)
    notes = fields.Text('Additional Notes')
    tenancy_ids = fields.One2many('tenancy', 'tenant')
    # payment_term_id = fields.Many2one('account.payment.term', 'Payment Terms')
    # tenant_detail_ids = fields.One2many('tenant.lines', 'tanent_line_id')


    @api.model
    def create(self, vals):
        name = self.search([('name', '=', vals['name'])])
        if name:
            raise UserError(_("Tenant Already Exist."))
        return super(TenantDetails, self).create(vals)

    # @api.multi
    def write(self, vals):
        if vals:
            if vals.get('name'):
                name = self.search([('name', '=', vals['name'])])
                if name:
                    raise UserError(_("Tenant Already Exist."))
        return super(TenantDetails, self).write(vals)