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

class AgentDetails(models.Model):
    _name = "agent.details"

    # @api.model
    # def _get_partner(self):
    #     # print ("111111111111111111111" )

    #     partners = self.env['res.partner'].sudo().search([])
    #     list_partner = []

    #     for partner in partners:
    #         # print ("pppppppppppppppppppp",partner)
    #         if partner.user_id.id == self.env.user.id and partner.is_agent == True:
    #             list_partner.append(partner.id)
    #             print ("list_partnerrrrrrrrrrrrrrtttt",list_partner)

    #     if len(list_partner) > 1:
    #         print ("aaaaaaaaaaaaaaa") 
    #         return [('id', 'in', list_partner)]
    #     elif len(list_partner) == 1:
    #         print ("bbbbbbbbbbbbbbb") 
    #         return [('id', '=', list_partner[0])]
    #     elif len(list_partner) == 0:
    #         print ("ccccccccccccccc") 
    #         return [('id', '=', -1)]


    name = fields.Many2one('res.partner',required = True, help='Choose Agent. If not showing any then create User and assign group of Agent.')
    # name = fields.Many2one('res.users',required = True, domain=_get_partner,help='Choose Tenant. If not showing any then create User and assign group of Tenant.')
    gender = fields.Selection([('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], string="Gender")
    bdate = fields.Date("Date of Birth")
    phone_number = fields.Char(related='name.mobile', relation='res.partner', string='Phone Number', store=True,readonly=True)
    email_id = fields.Char(related='name.email', relation='res.partner', string='Email ID', store=True,readonly=True)
    street = fields.Char(related='name.street', relation='res.partner', string='Email ID', store=True, readonly=True)
    street2 = fields.Char(related='name.street2', relation='res.partner', string='Email ID', store=True, readonly=True)
    zip = fields.Char(related='name.zip', relation='res.partner', string='Email ID', store=True, readonly=True)
    city = fields.Char(related='name.city', relation='res.partner', string='Email ID', store=True, readonly=True)
    state_id = fields.Many2one(related='name.state_id', relation='res.partner', string='Email ID', store=True,
                               readonly=True)
    country_id = fields.Many2one(related='name.country_id', relation='res.partner', string='Email ID', store=True,readonly=True)
    notes = fields.Text('Additional Notes')
    payment_ids = fields.One2many('account.payment', 'agent_id')
    # tenancy_ids = fields.One2many('tenancy', 'tenant')
    # payment_term_id = fields.Many2one('account.payment.term', 'Payment Terms')
    # tenant_detail_ids = fields.One2many('tenant.lines', 'tanent_line_id')


    @api.model
    def create(self, vals):
        name = self.search([('name', '=', vals['name'])])
        if name:
            raise UserError(_("Agent Already Exist."))
        print("==========agent===========",self,vals)
        return super(AgentDetails, self).create(vals)

    # @api.multi
    def write(self, vals):
        if vals:
            if vals.get('name'):
                name = self.search([('name', '=', vals['name'])])
                if name:
                    raise UserError(_("Agent Already Exist."))
        return super(AgentDetails, self).write(vals)