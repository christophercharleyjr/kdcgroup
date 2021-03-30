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

class SendPayment(models.TransientModel):
    _name = "send.payment"

    @api.model
    # @api.depends('percent')
    def _get_default_amount(self):
        active_ids = self._context.get('active_ids')
        issue_payment_obj = self.env['issue.payment'].browse(active_ids)

        # ctx = self._context
        # if ctx.get('active_model') == 'issue.payment':
        #     return self.env['issue.payment'].browse(ctx.get('active_ids')[0]).outstanding_amount_for_landlord
        amount = issue_payment_obj.remaining_amount_to_send
        return amount

    amount = fields.Float(default=_get_default_amount, required = 1)
    # send_date = fields.Date(required = 1)
    charge_date = fields.Date("Charge Date",required =1)

    # @api.one
    def send_payment(self):
        active_ids = self._context.get('active_ids')
        issue_payment_obj = self.env['issue.payment'].browse(active_ids)

        if self.amount > issue_payment_obj.remaining_amount_to_send:
            raise UserError(
                _('You have entered amount more then Outstanding Amount.'))

        self.env['landlord.payment'].create({
                            'amount':self.amount,
                            # 'send_date':self.send_date,
                            'charge_date':self.charge_date,
                            'payment_id':issue_payment_obj.id,
                          })
        # print('-------------- Payment called ----------------')

        issue_payment_obj.write({'remaining_amount_to_send' : issue_payment_obj.remaining_amount_to_send - self.amount})
        journal_obj = self.env['account.journal']
        journal_id = journal_obj.search([('name', '=', 'Cash')])
        # print('-------------- journal_id ----------------',journal_id)
        payment_obj = self.env['account.payment']

        vals = ({'partner_id': issue_payment_obj.issue_id.tenant.name.user_id.partner_id.id,
                 'partner_type': 'customer',
                 'payment_type': 'inbound',
                 'amount': self.amount,
                 'date': self.charge_date,
                 'journal_id': journal_id.id,
                 'landlord_id': issue_payment_obj.landlord.id,
                 'property_id': issue_payment_obj.property.id,
                 'agent_id': issue_payment_obj.property.agent.id,
                 'payment_source': issue_payment_obj.name,
                 # 'state': 'posted',
                 'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id})

        # print('-------------- vals ----------------',vals)
        pay = payment_obj.create(vals)
        pay.action_post()

        # payment_records = payment_obj.search(['&','&',('property_id','=',issue_payment_obj.property.id),('payment_type','=','outbound'),('state','=','draft')])
        # for pay_record in payment_records:
        #     due = datetime.strptime(self.charge_date, "%Y-%m-%d")
        #     pay = datetime.strptime(pay_record.payment_date, "%Y-%m-%d")
        #
        #     # if due.month == pay.month and due.year == pay.year and due.date <= pay.date:
        #     #     pay_record.write({'amount': pay_record.amount - self.amount})
        #     #     break
        #     # elif due.month == pay.month and due.year == pay.year and due.date > pay.date:
        #     #     pay_record.write({'amount': pay_record.amount - self.amount})
        #     #     break
        #     if self.charge_date <= pay_record.payment_date:
        #         pay_record.write({'amount': pay_record.amount - self.amount})
        #         break
        #     # else
        #
        #     # print(':::::::::::::::payment_record;:::::::::;:::::',pay_record)
        #     print('::::::::::::::: due ::::::::::::::',due)
        #     print('::::::::::::::: pay ::::::::::::::',pay)
        #     print('::::::::::::::: diff::::::::::::::',pay-due)
        # print(':::::::::::::::payment_record;:::::::::;:::::',a)
        # print ("::::::::::::",self.env['account.payment'].browse(issue_payment_obj.property.tenancy_ids.payment_ids))

        return True