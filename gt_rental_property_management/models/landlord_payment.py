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

class LandlordPayment(models.Model):
    _name = "landlord.payment"

    payment_id = fields.Many2one('issue.payment')
    name = fields.Char(string='Landlord Payment #', readonly=True, default=lambda self: _('New'))
    # status = fields.Selection([('draft', 'Draft'), ('paid', 'Paid')],
    #                           string="Status", default='draft')
    amount = fields.Float()
    # send_date = fields.Date()
    charge_date = fields.Date()
    payment_record_created = fields.Boolean()


    # @api.one
    # def payment_done(self):
    #
    #     issue_pay_obj = self.env['issue.payment'].search([('id','=',self.payment_id.id)])
    #     updated_amount = issue_pay_obj.outstanding_amount_for_landlord - self.amount
    #     issue_pay_obj.write({'outstanding_amount_for_landlord':updated_amount})
    #     self.write({'status':'paid'})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('landlord_pay') or '0'
        return super(LandlordPayment, self).create(vals)