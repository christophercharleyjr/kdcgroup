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

{
    "name": "Property Management - Lease / Rental / Tenancy",
    "version": "1.2.0",
    "author": "Globalteckz",
    "summary":"This Module can be used to Manage Property Lease/Rental/Tenancy Management",
    "category": "Sales",
    "price": "119.00",
    "currency": "EUR",
    'website': 'https://www.globalteckz.com/shop/odoo-apps/odoo-sale-of-property-rental-property-management-software-odoo-apps/',
    "license" : "Other proprietary",
    'images': ['static/description/Banner.png'],
    "live_test_url" : "https://www.globalteckz.com/shop/odoo-apps/odoo-sale-of-property-rental-property-management-software-odoo-apps/",
    "description": """
            It is a tenancy management system allowing Estate Agent to manage all the properties and
            landlords can access their properties and details about each property,
            like what payments he has received. Estate Agent will be the main user of the system who will manage everything within the system.
property
property management
lease
lease management
rental
rental management
properties
properties management
tenant
tenant management
tenancy
tenancy management
manage property
manage properties
manage lease
manage rental
manage tenant
manage property management
manage properties management
manage lease management
manage rental management
manage tenant management
estate management
estate
manage estate
manage estate management
agent
agent management
manage agent
landlord
manage landlord
landlord management
building
building management
manage building
manage building management
bunglow
manage bunglow
manage bunglow management
sale of real estate
real estate
real estate management
shop management
shop
commission
agent commission
manage commuission
agreement
construction
odoo property
odoo property management
rental property management
property software
property management software
landlord software
real estate software
real estate management software
rental property management software
online property management software
rental property software
property management accounting software
best property management software
apartment management software
rental management software
building management software
commercial property management software
residential property management software
real estate property management software
estate agent software
property management app
simple property management software
tenant management software
property accounting software
property development software
property management software programs
estate management software
rental property accounting software
property management portfolio software
condominium management software
landlord management software
property management software for landlordsletting agent software
real estate agent software
pms software
real estate database software
condo management software
apartment software
real estate accounting software
property portfolio software
real estate broker software
real estate software programs
landlord accounting software
best rental property software
best landlord software
property management system software
web based property management software
small property management software
apartment rental software
investment property management software
on site property management software
cloud based property management software
top property management software


    """,
    "init_xml": [],
    'depends': ['stock','account'],
    "data" :[
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/rules.xml',
        'data/schuduler_action.xml',
        'data/property_category.xml',
        'data/ir_sequence_data.xml',
        'wizard/create_tenancy.xml',
        'wizard/create_issue.xml',
        'wizard/send_payment.xml',
        'views/property.xml',
        'views/issue.xml',
        'views/tenancy.xml',
        'views/menu.xml',
        'views/payments.xml',
        'views/invoice_scheduler.xml',
        'views/landlord.xml',
        'views/partner.xml',
        'views/account_move.xml',
        'views/account_payment.xml',
        'views/issue_payment.xml',
        'views/tenant.xml',
        'views/agent.xml',

    ],
    'demo': [
        # 'demo/product.xml',
    ],

    'update_xml': [ ],
    'demo_xml': [],
    'js':[],
    'qweb':[],
    'css':[],
    'img':['static/src/img/*'],
    'installable': True,
    'active': False,
    #    'certificate': 'certificate',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
