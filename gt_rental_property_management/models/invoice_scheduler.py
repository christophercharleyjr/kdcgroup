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
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class scheduler_invoice(models.Model):
    _name = 'scheduler.invoice'

    name = fields.Char(required=True)
    numberOfUpdates = fields.Integer('Number of updates', help='The number of times the scheduler has run and updated this field')
    lastModified = fields.Date('Last updated')

    # @api.multi
    def create_scheduled_invoice(self):
        # print ("+++++++++++++++++++++++++++++ Scheduler Called +++++++++++++++++++++++++++++")

        invoice_obj = self.env['account.move']
        inv_fields = invoice_obj.fields_get()
        default_value = invoice_obj.default_get(inv_fields)
        invoice_line = self.env['account.move.line']
        line_f = invoice_line.fields_get()
        default_line = invoice_line.default_get(line_f)
        tenancies = self.env['tenancy'].search([])
        # print("----------------------  tenancies -------------------", tenancies)

        if tenancies:
            for tenancy in tenancies:
                # print("---------------------  tenancy ---------------------",tenancy)
                partner = self.env['res.partner'].search([('id','=',tenancy.tenant.name.id)]).id
                landlord = self.env['landlord.details'].search([('name','=',tenancy.landlord.name.id)])
                salesperson = landlord.name.user_id.id

                origin = tenancy.name
                property = tenancy.property
                product = self.env['product.product'].search([('name', '=', tenancy.property.name)])
                product_id = product.id
                # print("----------------  invoice_line_ids ---------------",tenancy.invoice_line_ids)

                price_unit = product.list_price
                # if property.commission:
                #     price_unit = product.list_price - property.commission
                #     print("------------------ if price_unit ----------------",price_unit)
                # else :
                #     price_unit = product.list_price
                #     print("------------------ else price_unit ----------------",price_unit)

                for line_invoice_id in tenancy.invoice_line_ids:
                    # print("--------------------------  line_invoice_id -------------- ",line_invoice_id)
                    date_inv_start = datetime.strptime(str(line_invoice_id.inv_start_date), '%Y-%m-%d').date()
                    # print ("date_inv_starttttttttttttttttt",date_inv_start,datetime.now().date())

                    if not line_invoice_id.invoice_id and date_inv_start <= datetime.now().date():
                        # print("---------------- if -- line_invoice_id.invoice_id ------------ ", line_invoice_id.invoice_id)

                        date_tenancy_start = datetime.strptime(str(line_invoice_id.inv_start_date), '%Y-%m-%d').date()

                        date_invoice = date_tenancy_start.replace(day=tenancy.payment_day)

                        if date_invoice < date_tenancy_start:
                            date_invoice = date_invoice + relativedelta(months=1)

                        default_value.update({
                                            'partner_id': partner, 
                                            'user_id': salesperson, 
                                            'date_invoice': date_invoice, 
                                            'property_id': property.id, 
                                            'landlord_id': landlord.id,
                                            'tenancy_id':tenancy.id,
                                            'origin': origin
                                            })

                        invoice = invoice_obj.new(default_value)
                        invoice._onchange_partner_id()

                        default_value.update({'account_id': invoice.account_id.id, 'message_follower_ids' : False ,'date_due': invoice.date_due})
                        inv_id = invoice.create(default_value)

                        default_line.update({
                            'invoice_id': inv_id.id,
                            'product_id': product_id,
                            'name': origin,
                            'price_unit': price_unit,
                            # 'invoice_line_tax_ids': [(6, 0, product.taxes_id.ids)]
                        })

                        inv_line = invoice_line.new(default_line)
                        inv_line._onchange_product_id()
                        default_line.update({'invoice_id': inv_id.id,
                                             'account_id': inv_line.with_context(
                                                 {'journal_id': inv_id.journal_id.id})._default_account()})

                        invoice_line.create(default_line)
                        line_invoice_id.write({'invoice_id': inv_id.id})

                        pay_landlord = self.env['res.partner'].search([('id','=',tenancy.landlord.name.id)])
                        journal_obj = self.env['account.journal']
                        journal_id = journal_obj.search([('name', '=', 'Cash')])
                        amount = tenancy.rent - tenancy.commission
                        agent = self.env['agent.details'].search([('name','=',landlord.name.user_id.partner_id.id)])
                        date_landlord_pay = date_tenancy_start.replace(day=tenancy.landlord_payment_day)

                        if date_landlord_pay < date_tenancy_start:
                            date_landlord_pay = date_invoice + relativedelta(months=1)

                        vals = ({'partner_id': pay_landlord.id,
                                 'partner_type': 'supplier',
                                 'payment_type': 'outbound',
                                 'agent_id': agent.id,
                                 'landlord_id': landlord.id,
                                 'tenancy_id': tenancy.id,
                                 'property_id': property.id,
                                 'payment_date': date_landlord_pay,
                                 'rent': tenancy.rent,
                                 'amount': amount,
                                 'agent_commission': tenancy.commission,
                                 'journal_id': journal_id.id,
                                 'payment_source': tenancy.name,
                                 # 'state': 'posted',
                                 'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id})

                        # print ("----------------- vals --------------------", vals)
                        payment_created  = self.env['account.payment'].create(vals)
                        
                        issue_payment_obj = self.env['issue.payment']
                        issue_payments = issue_payment_obj.search([('property','=',property.id)])
                        if issue_payments:
                            deduct_amount = 0
                            # print ('------------ issue_payments --------------', issue_payments)

                            for issue_payment in issue_payments:
                                # print ("1111111111111111")
                                for landlord_pay_id in issue_payment.landlord_pay_ids:
                                    # print ("22222222222")
                                    date_send_pay_due = datetime.strptime(str(landlord_pay_id.charge_date), '%Y-%m-%d').date()
                                    # print ("dateeeeeeeeeee",date_send_pay_due,date_landlord_pay)
                                    if landlord_pay_id.payment_record_created == False and  date_send_pay_due <= date_landlord_pay:
                                        # print ("33333333333333")
                                        deduct_amount = deduct_amount + landlord_pay_id.amount
                                        landlord_pay_id.write({'payment_record_created': True})
                                        # print ('------------ landlord_pay_id --------------',landlord_pay_id)
                                        # print ('------------ deduct_amount --------------',deduct_amount)
                                        payment_created.write({
                                            'issue_payment_ids': [(0, 0, {
                                                'description': issue_payment.issue_id.issue_summary,
                                                'amount': -landlord_pay_id.amount,
                                                'issue_payment_id': issue_payment.id,
                                            })]
                                        })
                                        # print ("payment_createddddddddddd====>>>",payment_created,payment_created.amount,issue_payment.issue_id.issue_summary,landlord_pay_id.amount,issue_payment.id)

                                        # print ("payment_createddddddddddd====>>>",payment_created.amount,deduct_amount)

                            payment_created.write({'amount': payment_created.amount - deduct_amount,
                                                   'issue_deduction':deduct_amount,
                                                   'issue_payment_ids': [(0, 0, {
                                                       'description': 'Agent Commission',
                                                       'amount': -tenancy.commission,
                                                       # 'issue_payment_id': issue_payment.id,
                                                        })]
                                                   })
                            # print ("payment_createddddddddddd222222====>>>",payment_created,-tenancy.commission)
                    else:
                        print("---------------- else -- line_invoice_id.invoice_id ------------ ", line_invoice_id.invoice_id)