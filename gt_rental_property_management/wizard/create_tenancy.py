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

class CreateTenancy(models.TransientModel):
    _name = "create.tenancy"

    tenant = fields.Many2one('tenant.details', required =1)
    tenancy_start = fields.Date('', required =1)
    tenancy_end = fields.Date('',required =1)
    deposit = fields.Float('',required =1)
    deposit_id = fields.Char('Deposit Id')
    # rent = fields.Float('',required =1)
    payment_day = fields.Integer('', required =1, default=5, help="This will be the day of the month chosen by the tenant to pay the estate agent.")
    landlord_payment_day = fields.Integer('', required =1, default=7, help="This will be the day of the month when estate agent pays landlord.")
    commission_type = fields.Selection([('fix', 'Fix'), ('percent', 'Percentages')], default='fix')
    percent = fields.Float('Percent %')
    fix_amount = fields.Float('Fix Amount')
    commission = fields.Float(compute='_compute_commission', store=True, readonly=True)
    rent = fields.Float(compute='_get_rent', store=True)

    # @api.one
    def _get_rent(self):
        active_ids = self._context.get('active_ids')
        property_obj = self.env['property'].browse(active_ids)
        self.rent = property_obj.rent


    # @api.one
    @api.depends('percent','fix_amount')
    def _compute_commission(self):
        # print ("_compute_commissionnnnnnnn")
        active_ids = self._context.get('active_ids')
        property_obj = self.env['property'].browse(active_ids)
        self.rent = property_obj.rent

        if self.commission_type == 'percent':
            self.commission = self.rent * self.percent / 100
            # print("---------------------- commission in compute -----------------------", self.commission)
        else:
        # if self.commission_type == 'fix':
            self.commission = self.fix_amount
            # print ("fixxxxxxxxelseeeeeeeeeeeeeeeeee",self.commission)

    # @api.one
    def create_tenancy(self):
        # print ("create_tenancyyyyyyyyyyy")
        if self.tenancy_end < self.tenancy_start:
            raise UserError(
                _('You have selected Tenancy End Date earlier than Tenancy Start Date.'))
        active_ids = self._context.get('active_ids')
        property_obj = self.env['property'].browse(active_ids)


        # print('===========================================================',self.tenant.name.id)
        # print('===========================================================',property_obj.name.id)
        # print('===========================================================',property_obj.property_landlord.name.id)

        # line = property_obj.write({'tenancy_ids':[(0,0,{'tenant' : self.tenant.name.id,
        #                                         'property':property_obj.id,
        #                                         'landlord':property_obj.property_landlord.name.id,
        #                                         'tenancy_start' : self.tenancy_start,
        #                                         'tenancy_end' : self.tenancy_end,
        #                                         'deposit' : self.deposit,
        #                                         'payment_day': self.payment_day,
        #                                         'landlord_payment_day': self.landlord_payment_day,
        #                                         })]})
        #


        # print("---------------------- commission -----------------------",self.commission)
        # print("---------------------- rent -----------------------",self.rent)
        # print("---------------------- commission -----------------------",line)

        tenancy_obj = self.env['tenancy']
        tenancy_created = tenancy_obj.sudo().create({'tenant' : self.tenant.id,
                                              'property':property_obj.id,
                                              # 'landlord':property_obj.property_landlord.name.id,
                                              'tenancy_start' : self.tenancy_start,
                                              'tenancy_end' : self.tenancy_end,
                                              'deposit' : self.deposit,
                                              'deposit_id' : self.deposit_id,
                                              'rent' : property_obj.rent,
                                              'payment_day': self.payment_day,
                                              'landlord_payment_day': self.landlord_payment_day,
                                              'commission_type': self.commission_type,
                                              'percent': self.percent,
                                              'commission': self.commission,
                                              })

        property_obj.sudo().write({'tenant':self.tenant.id})

        # property_obj.write({'end': self.tenancy_end})
        start = datetime.strptime(str(self.tenancy_start), "%Y-%m-%d")
        end = datetime.strptime(str(self.tenancy_end), "%Y-%m-%d")

        years = relativedelta(end, start).years
        months = relativedelta(end, start).months
        total_months = years *12 + months

        # print('---------------------------- start =----------------------------', start)
        # print('---------------------------- end =----------------------------', end)
        # print('---------------------------- r.years ------ ----------------------',years)
        # print('---------------------------- r.months ----------------------------',months)
        # print('---------------------------- r.total_months ----------------------------',total_months)
        # print('---------------------------- tenancy_created ----------------------------',tenancy_created)
        # print('---------------------------- tenancy_created ----------------------------',tenancy_created.id)
        # print('---------------------------- tenancy_created ----------------------------',tenancy_created.name)

        for i in range(0, total_months + 1):
            # print ("forrrrrrrrrrrrrrrr",i)
            inv_start_date = start
            inv_end_date = inv_start_date + relativedelta(months=1, days=-1)
            start = inv_end_date + relativedelta(days=1)

            tenancy_created.sudo().write({'invoice_line_ids': [(0, 0,{
                                    'inv_id': tenancy_created.id,
                                    'inv_no': i+1,
                                    'inv_start_date': inv_start_date,
                                    'inv_end_date': inv_end_date,
                                    'inv_amount': property_obj.rent })]
                                  })
        return True