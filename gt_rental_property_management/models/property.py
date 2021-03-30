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
from datetime import datetime,date

class Property(models.Model):
    _name = 'property'
    _default = {'country_id':233}

    name = fields.Text()
    image = fields.Binary()

    status = fields.Selection([('free', 'Free'), ('not_available', 'Not Available')],
                             # string="Status", default='free')
                             string="Status", default='free', store=True, compute='_compute_state')
    # end = fields.Date()

    # @api.one
    @api.depends('tenancy_ids')
    def _compute_state(self):
        if self.tenancy_ids:
            if datetime.now() <= datetime.strptime(str(self.tenancy_ids[-1].tenancy_end), "%Y-%m-%d"):
                self.status = 'not_available'
            else :
                self.status = 'free'
        else :
            self.status = 'free'


    @api.model
    def default_get(self, vals):
        res = super(Property, self).default_get(vals)
        country_ids = self.env['res.country'].search([('code', '=', 'GB')])
        if country_ids:
            res.update(
                {
                    'country_id': country_ids[0].id,
                }
            )
        return res


    property_landlord = fields.Many2one('landlord.details','Landlord',required = True)
    # agent = fields.Many2one('agent.details','Agent', readonly=True, default=lambda self: self.env.user.partner_id.id)
    agent = fields.Many2one('agent.details','Agent',readonly=True)
    # default=lambda self: self.env.user
    tenant = fields.Many2one('tenant.details','Tenant', store=True, compute='_compute_tenant',readonly=True)

    # @api.one
    @api.depends('tenancy_ids')
    def _compute_tenant(self):
        print("============_compute_tenant================",self,self.status)
        if self.status == 'not_available':
            # print('-------------- self.tenancy_ids[-1] -------------',self.tenancy_ids[-1].tenant.id)
            self.tenant = self.tenancy_ids[-1].tenant.id
            # print ("tenanttenanttenant",self.tenant)
        else:
            self.tenant = None
            print("===============else===============",self.tenant)


    # type = fields.Many2one('property.type','Property Type',required = True)
    # furnishing = fields.Selection([('Full Furnished','Full Furnished'),('Semi Furnished','Semi Furnished'),('Unfurnished','Unfurnished')])
    street = fields.Char(required = True)
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char(required = True)
    state_id = fields.Many2one("res.country.state", string='State', required = True, ondelete='restrict')
    country_id = fields.Many2one(related='state_id.country_id', relation='res.country', string='Country', store=True,
        readonly=True)
    # country_id = fields.Many2one('res.country', string='Country', required = True, ondelete='restrict')
    num_bed = fields.Integer('Bedrooms', default=1)
    num_bath = fields.Integer('Bathrooms', default=1)
    type = fields.Selection([('terraced','Terraced'),('detached','Detached'),('semi_detached','Semi Detached')])
    gas_safety_exp_date = fields.Date('Gas Safety Expiry Date')
    gas_safety_exp_attch = fields.Binary('Gas Safety Expiry Attachment')
    elect_safety_certy_attch = fields.Binary('Electricity Safety Certificate Attachment')
    epc = fields.Char('Energy Performance (EPC)')
    rent = fields.Float(required=1)
    notes = fields.Text('Additional Notes')
    commission_type = fields.Selection([('fix','Fix'),('percent','Percentages')], default='fix')
    percent = fields.Float('Percent %')
    commission = fields.Float(compute='_compute_commission', store=True)

    # @api.one
    @api.depends('rent','percent')
    def _compute_commission(self):
        if self.commission_type == 'percent':
            self.commission = self.rent * self.percent/100
        # else:
        #     self.commission = self.commission

    # state = fields.
    tenancy_ids = fields.One2many('tenancy','property')
    payment_ids = fields.One2many('account.payment', 'property_id')
    issue_ids = fields.One2many('issue', 'property')
    issue_payment_ids = fields.One2many('issue.payment', 'property')
    move_ids = fields.One2many('account.move', 'property_id')

    @api.model
    def create(self, vals):
        print("---------- create -------------------",self,vals)
        name = self.search([('name', '=', vals['name'])])
        if name:
            print("---------- name -------------------",name)
            raise UserError(_("Property Already Exist."))
            

        product = self.env['product.product'].search([('name', '=', vals['name'])])
        if product:
            # print("---------- prod_name -------------------",product)
            raise UserError(_("Property Already Exist."))
           

        agent_obj = self.env['agent.details'].search([('name', '=', self.env.user.partner_id.id)])
        # print("--------------------------------------------", agent_obj)

        vals['agent'] = agent_obj.id
        category_id = self.env['product.category'].search([('name', '=', 'Property')]).id
        # category_id = self.env['product.category'].search([('name', '=', 'All')]).id

        # print("---------- before product -------------------")
        self.env['product.product'].sudo().create({
            'name': vals['name'],
            'type': 'service',
            'categ_id': category_id,
            'list_price': vals['rent'],
        })
        # print("---------- after product -------------------")

        return super(Property, self).create(vals)

    # @api.multi
    def write(self, vals):
        print("=============write=====================",self,vals)
        if vals:
            if vals.get('name'):
                name = self.search([('name', '=', vals['name'])])
                if name:
                    # print("---------- wwwname -------------------",name)
                    raise UserError(_("Property Already Exist."))
                    

            product = self.env['product.product'].search([('name', '=', self.name)])
            if not product:
                raise UserError(_("This Property is no more exists in Products."))
            # print"--------------------------------", vals.get('charge')

            if vals.get('name'):
                product.name = vals['name']
            if vals.get('rent'):
                product.list_price = vals['rent']
        return super(Property, self).write(vals)


    # @api.multi
    def unlink(self):
        for property in self:
            # print ("------------- properties-------------------", property.name)
            self.env['product.product'].search([('name', '=', property.name)]).unlink()
        return super(Property, self).unlink()