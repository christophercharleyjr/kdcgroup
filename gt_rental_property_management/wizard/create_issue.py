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

class CreateIssue(models.TransientModel):
    _name = "create.issue"

    issue_summary = fields.Text('',required =1)
    image = fields.Binary("Image")

    # @api.one
    def create_issue(self):
        active_ids = self._context.get('active_ids')
        property_obj = self.env['property'].browse(active_ids)
        issue_obj = self.env['issue']
        tenant = self.env['tenant.details'].search([('name','=',self.env.user.partner_id.id)])
        # print('-------------- tenant ----------------',tenant.name)

        issue_obj.sudo().create({'property': property_obj.id,
                          'tenant': tenant.id,
                          'landlord':property_obj.property_landlord.id,
                          'issue_create_date': date.today(),
                          'issue_summary': self.issue_summary,
                          'image': self.image,
                          })
        # print('-------------- Issue called ----------------')
        return True
