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

class IssuePayment(models.Model):
    _name = "issue.payment"

    name = fields.Char(string='Issue Payment #', readonly=True, default=lambda self: _('New'))
    property = fields.Many2one('property', required =1, readonly=1)
    landlord = fields.Many2one('landlord.details', required =1, readonly=1)
    status = fields.Selection([('draft', 'Draft'),('partial','Partial Paid'), ('paid', 'Paid')],
                              string="Status", default='draft', compute='_compute_status',store=True)
    agent_paid_amount= fields.Float('', required =1, readonly=1)
    remaining_amount_to_send= fields.Float('Remaining Amount To Charge Landlord', required =1, readonly=1)
    outstanding_amount_for_landlord = fields.Float('Landlord To Pay', required =1, readonly=1)
    amount_paid_by_landlord = fields.Float('', readonly=1, compute='_compute_paid_amount', store=True)
    landlord_pay_ids = fields.One2many('landlord.payment','payment_id')
    issue_id = fields.Many2one('issue',readonly=1)

    # @api.one
    @api.depends('outstanding_amount_for_landlord')
    def _compute_status(self):

        if self.outstanding_amount_for_landlord <= 0:
            self.status = 'paid'
        elif self.outstanding_amount_for_landlord > 0 and self.outstanding_amount_for_landlord < self.agent_paid_amount:
            self.status = 'partial'
        else:
            self.status = 'draft'

    # @api.one
    @api.depends('agent_paid_amount','outstanding_amount_for_landlord')
    def _compute_paid_amount(self):
        self.amount_paid_by_landlord = self.agent_paid_amount - self.outstanding_amount_for_landlord

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('issue_pay') or '0'
        return super(IssuePayment, self).create(vals)

class IssuePaymentHistory(models.Model):
    _name = "issue.payment.history"

    issue_payment_history_id = fields.Many2one('account.payment',readonly=1)
    description = fields.Char()
    amount = fields.Float()
    issue_payment_id = fields.Many2one('issue.payment')
