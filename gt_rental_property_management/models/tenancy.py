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
from dateutil.relativedelta import relativedelta
from datetime import datetime,date

class Tenancy(models.Model):
    _name = "tenancy"

    name = fields.Char(string='Tenancy #',readonly=True, default=lambda self: _('New'))
    tenant = fields.Many2one('tenant.details',string='Tenant', required=1)
    property = fields.Many2one('property',string='Property', required=1)
    landlord = fields.Many2one(related='property.property_landlord', store=True, string='Landlord', readonly=True, relation='landlord.details')
    tenancy_start = fields.Date('', required=1)
    tenancy_end = fields.Date('', required=1)
    deposit = fields.Float('', required=1)
    deposit_id = fields.Char('Deposit ID')
    rent = fields.Float(related='property.rent', store=True, string='Rent', readonly=True, relation='property')
    payment_day = fields.Integer('', required=1)
    landlord_payment_day = fields.Integer('', required=1)
    invoice_line_ids = fields.One2many('invoice','inv_id')
    commission_type = fields.Selection([('fix', 'Fix'), ('percent', 'Percentages')], default='fix')
    percent = fields.Float('Percent %')
    commission = fields.Float()
    invoice_ids=fields.One2many('account.move','tenancy_id', readonly=True)
    payment_ids=fields.One2many('account.payment','tenancy_id')
    is_agent = fields.Boolean(compute="_check_user_group")

    # @api.one
    def _check_user_group(self):
        self.is_tenant = self.env.user.has_group('gt_rental_property_management.group_agent')

    # commission = fields.Float(compute='_compute_commission', store=True)

    # @api.one
    # @api.depends('rent', 'percent')
    # def _compute_commission(self):
    #
    #     if self.commission_type == 'percent':
    #         self.commission = self.rent * self.percent / 100
    #         # else:
    #         #     self.commission = self.commission


    @api.model
    def create(self, vals):
        if vals['tenancy_end'] < vals['tenancy_start']:
            raise UserError(
                _('You have selected Tenancy End Date earlier than Tenancy Start Date.'))
        # if vals.get('name', '0') == '0':
        vals['name'] = self.env['ir.sequence'].next_by_code('tenancy') or '0'
        # print("---------------------------------------",self.invoice_line_ids)
        return super(Tenancy, self).create(vals)


class Invoice(models.Model):
    _name = "invoice"

    # invoice_id = fields.Many2one('tenancy')
    # name=fields.Char()
    # date=fields.Date()
    inv_id = fields.Many2one('tenancy', string='Tenancy Id')
    inv_no = fields.Integer(string='Invoice No', readonly=True)
    inv_start_date = fields.Date(string='From Date', readonly=True)
    inv_end_date = fields.Date(string='To Date', readonly=True)
    inv_amount = fields.Float(digits=(5, 2), readonly=True)
    # emi_payment_date = fields.Date(string='Payment Date')
    invoice_id = fields.Many2one('account.move')
    # invoice_id_state = fields.Char(string='Invoice State')
    # invoice_id_state = fields.Selection(related='invoice_id.state', store=True, string='Invoice State')