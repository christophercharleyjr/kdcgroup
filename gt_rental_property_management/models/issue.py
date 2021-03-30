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

class Issue(models.Model):
    _name = "issue"

    name = fields.Char(string='Issue #', readonly=True, default=lambda self: _('New'))
    tenant = fields.Many2one('tenant.details', required =1, readonly=1)
    landlord = fields.Many2one('landlord.details', required =1, readonly=1)
    property = fields.Many2one('property', required =1)
    issue_create_date = fields.Date('', required =1, readonly=1)
    issue_summary = fields.Text('',required =1)
    image = fields.Binary('')
    status = fields.Selection([('draft', 'Draft'), ('processing', 'Processing'), ('done', 'Done')],
                              string="Status", default='draft')
    cost = fields.Float('')
    handy_man = fields.Many2one('res.partner')
    handy_man_docs = fields.Binary('Attachment')
    paid = fields.Boolean(compute="_compute_paid")
    is_tenant = fields.Boolean(compute="_check_user_group")
    issue_payment_ids = fields.One2many('issue.payment','issue_id')


    # @api.one
    def _check_user_group(self):
        self.is_tenant = self.env.user.has_group('gt_rental_property_management.group_tenant')
        # print("=============self.is_tenant===============",self.is_tenant)

    # @api.one
    def _compute_paid(self):
        ip = self.env['issue.payment'].search([('issue_id','=',self.id)])
        # print("===========_compute_paid===============",ip,self.id)
        if ip and ip.status =='paid':
            self.paid= True
        else:
            self.paid = False

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('issue') or '0'
        return super(Issue, self).create(vals)

    # @api.multi
    def set_to_processing(self):
        self.write({'status': 'processing'})

    # @api.multi
    def set_to_done(self):

        if self.cost <= 0:
            raise UserError(_("Please Enter the Cost first."))
        else:
            self.env['issue.payment'].create({'issue_id':self.id,
                                              'property':self.property.id,
                                              'landlord':self.landlord.id,
                                              'agent_paid_amount':self.cost,
                                              'outstanding_amount_for_landlord':self.cost,
                                              'remaining_amount_to_send':self.cost,
                                              })
            self.write({'status': 'done'})


        # else:
        #     move_obj = self.env['account.move']
        #     inv_fields = move_obj.fields_get()
        #     default_value = move_obj.default_get(inv_fields)
        #
        #     print ("-------------- default_value ----------------", default_value)
        #     # move_line = self.env['account.move.line']
        #     # line_f = move_line.fields_get()
        #     # default_line = move_line.default_get(line_f)
        #
        #     journal_obj = self.env['account.journal']
        #     journal_id = journal_obj.search([('name', '=', 'Vendor Bills')])
        #
        #     debit_vals = {
        #         # 'name': account_id.default_debit_account_id.name,
        #         'debit': self.cost,
        #         'credit': 0.0,
        #         'account_id': self.landlord.name.property_account_payable_id.id,
        #         'partner_id': self.landlord.name.id,
        #     }
        #     credit_vals = {
        #         # 'name': sale_person.name,
        #         'debit': 0.0,
        #         'credit': self.cost,
        #         'account_id': self.property.agent.name.property_account_receivable_id.id,
        #         'partner_id': self.property.agent.name.id,
        #     }
        #
        #     now = datetime.now()
        #     default_value.update({
        #         'property_id': self.property.id,
        #         'journal_id': journal_id.id,
        #         'date': now.strftime('%Y-%m-%d'),
        #         'state': 'draft',
        #         'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)],
        #         'ref': self.name,
        #         'partner_id': self.landlord.name.id,
        #     })
        #
        #     print ("-------------- default_value ----------------", default_value)
        #
        #     move = self.env['account.move'].create(default_value)
        #     move.write({'partner_id':self.landlord.name.id})
        #     # move.post()
        #     self.write({'status': 'done'})




        # else:
        #     invoice_obj = self.env['account.invoice']
        #     inv_fields = invoice_obj.fields_get()
        #     default_value = invoice_obj.default_get(inv_fields)
        #
        #     invoice_line = self.env['account.invoice.line']
        #     line_f = invoice_line.fields_get()
        #     default_line = invoice_line.default_get(line_f)
        #
        #     salesperson = self.property.property_landlord.name.user_id.id
        #     default_value.update(
        #         {'partner_id': self.landlord.name.id, 'user_id': salesperson, 'date_invoice': date.today(), 'property_id': self.property.id, 'landlord_id': self.landlord.id,
        #          'origin': self.name})
        #
        #     invoice = invoice_obj.new(default_value)
        #     invoice._onchange_partner_id()
        #     default_value.update(
        #         {'account_id': invoice.account_id.id, 'message_follower_ids': False, 'date_due': invoice.date_due})
        #     inv_id = invoice.create(default_value)
        #     product = self.env['product.product'].search([('name', '=', self.property.name)])
        #
        #     default_line.update({
        #         'invoice_id': inv_id.id,
        #         'product_id': product.id,
        #         'name': self.issue_summary,
        #         'price_unit': self.cost,
        #         # 'invoice_line_tax_ids': [(6, 0, product.taxes_id.ids)]
        #     })
        #
        #     inv_line = invoice_line.new(default_line)
        #     inv_line._onchange_product_id()
        #     default_line.update({'invoice_id': inv_id.id,
        #                          'account_id': inv_line.with_context(
        #                              {'journal_id': inv_id.journal_id.id})._default_account()})
        #     invoice_line.create(default_line)