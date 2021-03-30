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

from odoo import api, fields, models, _
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    agent_id = fields.Many2one('agent.details', string='Agent', readonly=True)
    landlord_id = fields.Many2one('landlord.details', string='Landlord', readonly=True)
    property_id = fields.Many2one('property', string='Property', readonly=True)
    tenancy_id = fields.Many2one('tenancy', string='Tenancy', readonly=True)
    # payment_source = fields.Many2one('issue.payment',readonly=1)
    payment_source = fields.Char(readonly=1)
    issue_payment_ids = fields.One2many('issue.payment.history','issue_payment_history_id')
    agent_commission = fields.Float()
    issue_deduction = fields.Float()
    rent = fields.Float()

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        res = super(AccountPayment, self).search(args)

        if self.env.user.has_group('base.group_system') and self.env.user.has_group('gt_rental_property_management.group_agent'):
            domain_admin = (1,'=',1)
            args.append(domain_admin)

        elif self.env.user.has_group('gt_rental_property_management.group_agent') :
            domain = ('agent_id.name','=',self.env.user.partner_id.id)
            args.append(domain)

        res = self._search(args, offset=offset, limit=limit, order=order, count=count)
        return res if count else self.browse(res)


    # @api.multi
    def action_post(self):
        # print ("popsttttttttttttttttttttttt")
        post = super(AccountPayment, self).action_post()

        if self.issue_payment_ids:
            for payment_line in self.issue_payment_ids:
                if payment_line.issue_payment_id:
                    ip =payment_line.issue_payment_id
                    ip.write({
                        'outstanding_amount_for_landlord': ip.outstanding_amount_for_landlord + payment_line.amount})

        # print ("----------- after main ---------------",a)


    # def _create_payment_entry(self, amount):
    #     move = super(AccountPayment,self)._create_payment_entry(amount)
    #
    #     print ("----------------- move --------------------",move)
    #     print ("----------------- self --------------------",self)
    #
    #     inv_fields = self.fields_get()
    #     default_value = self.default_get(inv_fields)
    #
    #     journal_obj = self.env['account.journal']
    #     journal_id = journal_obj.search([('name', '=', 'Cash')])
    #
    #     # default_value.update({'partner_id':self.landlord_id.name.id,
    #     #                       'partner_type':'supplier',
    #     #                       'payment_type':'outbound',
    #     #                       'amount':self.property_id.commission,
    #     #                       'journal_id': journal_id.id,
    #     #                       # 'state': 'posted',
    #     #                       'payment_method_id':self.env.ref('account.account_payment_method_manual_in').id})
    #
    #
    #     vals = ({'partner_id': self.landlord_id.name.id,
    #                           'partner_type': 'supplier',
    #                           'payment_type': 'outbound',
    #                           'amount': self.property_id.commission,
    #                           'journal_id': journal_id.id,
    #                           # 'state': 'posted',
    #                           'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id})
    #
    #     print ("----------------- vals --------------------",vals)
    #     print("-----------------------------", self.create(vals))
    #     # self.create(default_value)
    #     return move



    # def action_validate_invoice_payment(self):
    #     """
    #     Agent commission against landlord
    #     Posts a payment used to pay an invoice. This function only posts the
    #     payment by default but can be overridden to apply specific post or pre-processing.
    #     It is called by the "validate" button of the popup window
    #     triggered on invoice form by the "Register Payment" button.
    #     """
    #     print ("11111111111111111111111111111111111111")
    #     if any(len(record.invoice_ids) != 1 for record in self):
    #         # For multiple invoices, there is account.register.payments wizard
    #         raise UserError(_("This method should only be called to process a single invoice's payment."))
    
    
    #     journal_obj = self.env['account.journal']
    #     journal_id = journal_obj.search([('name', '=', 'Cash')])
    
    #     tenancy_obj = self.env['tenancy']
    #     tenancy_id = tenancy_obj.search([('name', '=' , self.invoice_ids.origin)])
    
    #     vals = ({'partner_id': self.landlord_id.name.id,
    #              'partner_type': 'supplier',
    #              'payment_type': 'outbound',
    #              'amount': tenancy_id.commission,
    #              'journal_id': journal_id.id,
    #              # 'state': 'posted',
    #              'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id})
    
    #     print ("----------------- vals --------------------", vals)
    #     self.create(vals)
    
    #     return self.post()


    @api.model
    def create(self, vals):
        result = super(AccountPayment,self).create(vals)
        # print ('resultsssssssssssssss',result)
        # print ('result.communicationssssssssssssss',result.communication)
        # if result.partner_type == 'customer':
        if result.ref :
            invoice = self.env['account.move'].search([('number', "=", result.communication)])
            agent = self.env['agent.details'].search([('name', '=', invoice.user_id.partner_id.id)])
            result.write({
                            'landlord_id': invoice.landlord_id.id,
                            'property_id': invoice.property_id.id,
                            'agent_id': agent.id,
                            })
        return result


class AccountInvoice(models.Model):
    _inherit = "account.move"

    landlord_id = fields.Many2one('landlord.details')
    property_id = fields.Many2one('property')
    tenancy_id = fields.Many2one('tenancy')


class AccountMove(models.Model):
    _inherit = "account.move"

    # landlord_id = fields.Many2one('landlord.details')
    property_id = fields.Many2one('property', readonly=True)