import logging
import requests
import json
import random
import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResCountryState(models.Model):
    _inherit = "res.country.state"

    smarttship_state_id = fields.Integer(string='Sync Cities')
    smarttship_state_code = fields.Char(string='Smarttship State Code')


class SmarttshipSync(models.Model):
    _name = "smarttship.sync"

    sync_city = fields.Boolean(string='Sync Cities')
    sync_state = fields.Boolean(string='Sync States')
    sync_customer = fields.Boolean(string='Sync Customers')


    def sync_records(self):
        print('testing')
        if self.sync_city:
            self.fetch_cities()
        if self.sync_state:
            self.fetch_states()

    def fetch_cities(self):
        url = "https://api.sandbox.smarttshipping.ca/api/carrierapi/GetCities"
        headers = {
            'apikey': '7474CAE8-35BA-47DE-983D-2DE16EDEB118',
            'Content-Type': 'application/json'
        }
        payload = json.dumps({})
        response = requests.request("GET", url, headers=headers, data=payload)
        response_dict = json.loads(response.text)
        if response_dict.get('Success') == True:
            for city in response_dict.get('Cities'):
                city_available = self.env['res.city.smarttship'].search([('city_id', '=', int(city.get('CityId'))), ('city_name', '=', str(city.get('CityName')))])
                if not city_available:
                    city_rec = self.env['res.city.smarttship'].create({
                        'city_id': int(city.get('CityId')),
                        'city_name': str(city.get('CityName')),
                    })
        print(response)

    def fetch_states(self):
        print('testing state fetch')
        url = "https://api.sandbox.smarttshipping.ca/api/carrierapi/GetStates"
        headers = {
            'apikey': '7474CAE8-35BA-47DE-983D-2DE16EDEB118',
            'Content-Type': 'application/json'
        }
        payload = json.dumps({})
        response = requests.request("GET", url, headers=headers, data=payload)
        response_dict = json.loads(response.text)
        if response_dict.get('Success') == True:
            country = self.env['res.country'].search([('name', '=', 'Canada')])
            if country:
                for state in response_dict.get('States'):
                    available_state = self.env['res.country.state'].search([('name', '=', state.get('StateName').lower().capitalize())])
                    if not available_state:
                        res_state = self.env['res.country.state'].create({
                            'smarttship_state_id': state.get('StateId'),
                            'name': state.get('StateName').lower().capitalize(),
                            'country_id': country.id,
                            'smarttship_state_code': state.get('StateAbb'),
                            'code': ''.join(random.choice(string.ascii_uppercase) for i in range(10))
                        })
                    else:
                        available_state.smarttship_state_code = state.get('StateAbb')
            print('state success')

class ResCitySmartship(models.Model):
    _name = "res.city.smarttship"


    city_id = fields.Integer(string='City ID')
    city_name = fields.Char(string='City Name')



class ResPartner(models.Model):
    _inherit = 'res.partner'

    smarttship_customer_id = fields.Integer(string='Smarttship Customer ID')
    smarttship_customer = fields.Boolean(string='Is Smarttship Customer')
    special_instructions = fields.Char(string='Special Instructions')
    broker_name = fields.Char(string='Broker Name')
    secondary_phone = fields.Char(string='Secondary Phone')
    contact_name = fields.Char(string='Contact Name')
    opening_time = fields.Datetime(string='Opening Time')
    closing_time = fields.Datetime(string='Closing Time')
    account_no = fields.Char(string='Account No')
    primary_contact_position = fields.Char(string='Primary Contact Position')
    primary_contact_phone = fields.Char(string='Primary Contact Phone')
    secondary_contact_name = fields.Char(string='Secondary Contact Name')
    secondary_contact_position = fields.Char(string='Secondary Contact Position')
    is_active = fields.Boolean(string='Is Active')
    notify = fields.Boolean(string='Is Active')
    phone_extenstion = fields.Char(string='Phone Extension')

    @api.model
    def create(self, vals):
        rec = super(ResPartner, self).create(vals)
        print('creating customer')
        if rec.smarttship_customer == True:
            print('development of customer')
            url = "https://api.sandbox.smarttshipping.ca/api/carrierApi/AddOrEditCustomer"
            headers = {
                'apikey': '7474CAE8-35BA-47DE-983D-2DE16EDEB118',
                'Content-Type': 'application/json'
            }
            city_id = self.env['res.city.smarttship'].search([('city_name', '=', rec.city)])
            state_id = rec.state_id.smarttship_state_id
            country_id = rec.country_id.id
            zip_code = rec.zip
            email = rec.email
            primary_phone = rec.phone
            if city_id and state_id and country_id and zip_code and email and primary_phone:
                payload = json.dumps({
                        "CustomerID": 0,
                        "CustomerName": rec.name,
                        "Address": rec.street + ' ' + rec.street2,
                        "CityID": city_id.id,
                        # "StateID": state_id,
                        "StateID": 1,
                        # "CountryID": country_id,
                        "CountryID": 1,
                        "ZipCode": zip_code,
                        "EmailID": email,
                        "PrimaryPhone": primary_phone,
                        "SpecialInstructions": rec.special_instructions if rec.special_instructions else False,
                        "BrokerName": rec.broker_name if rec.broker_name else False,
                        "SecondaryPhone": rec.secondary_phone if rec.secondary_phone else False,
                        "Website": rec.website if rec.website else False,
                        "ContactName": rec.contact_name if rec.contact_name else False,
                        "OpeningTime": str(rec.opening_time.strftime('%Y-%m-%dT%H:%M:%S')) if rec.opening_time else False,
                        "ClosingTime": str(rec.closing_time.strftime('%Y-%m-%dT%H:%M:%S')) if rec.closing_time else False,
                        "AccountNo": rec.account_no if rec.account_no else False,
                        "PrimaryContactPosition": rec.primary_contact_position if rec.primary_contact_position else False,
                        "PrimaryContactPhone": rec.primary_contact_phone if rec.primary_contact_phone else False,
                        "SecondaryContactName": rec.secondary_contact_name if rec.secondary_contact_name else False,
                        "SecondaryContactPosition": rec.secondary_contact_position if rec.secondary_contact_position else False,
                        "AdditionalNotes": rec.comment if rec.comment else False,
                        "IsActive": rec.is_active if rec.is_active else False,
                        "Notify": rec.notify if rec.notify else False,
                        "PhoneExtension": rec.phone_extenstion if rec.phone_extenstion else False
                    })

                response = requests.request("POST", url, headers=headers, data=payload)
                response_dict = json.loads(response.text)
                if response_dict.get('Success') == True:
                    rec.smarttship_customer_id = response_dict.get('Customer').get('CustomerID')
                    print('response successful')
                else:
                    raise ValidationError(_(str(response_dict.get('Message'))))
            else:
                raise ValidationError(_(str('Some required fields in Smarttship are empty.')))
        return rec


    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        print('testing write')
        if self.smarttship_customer_id != 0 and self.smarttship_customer_id != False:
            if self.smarttship_customer == True:
                print('development of customer')
                url = "https://api.sandbox.smarttshipping.ca/api/carrierApi/AddOrEditCustomer"
                headers = {
                    'apikey': '7474CAE8-35BA-47DE-983D-2DE16EDEB118',
                    'Content-Type': 'application/json'
                }
                city_id = self.env['res.city.smarttship'].search([('city_name', '=', self.city)])
                state_id = self.state_id.smarttship_state_id
                country_id = self.country_id.id
                zip_code = self.zip
                email = self.email
                primary_phone = self.phone
                if city_id and state_id and country_id and zip_code and email and primary_phone:
                    payload = json.dumps({
                            "CustomerID": self.smarttship_customer_id,
                            "CustomerName": self.name,
                            "Address": self.street + ' ' + self.street2,
                            "CityID": 1,
                            "StateID": 1,
                            "CountryID": 1,
                            # "CityID": city_id.id,
                            # "StateID": state_id,
                            # "CountryID": country_id,
                            "ZipCode": zip_code,
                            "EmailID": email,
                            "PrimaryPhone": primary_phone,
                            "SpecialInstructions": self.special_instructions if self.special_instructions else False,
                            "BrokerName": self.broker_name if self.broker_name else False,
                            "SecondaryPhone": self.secondary_phone if self.secondary_phone else False,
                            "Website": self.website if self.website else False,
                            "ContactName": self.contact_name if self.contact_name else False,
                            "OpeningTime": str(self.opening_time.strftime('%Y-%m-%dT%H:%M:%S')) if self.opening_time else False,
                            "ClosingTime": str(self.closing_time.strftime('%Y-%m-%dT%H:%M:%S')) if self.closing_time else False,
                            "AccountNo": self.account_no if self.account_no else False,
                            "PrimaryContactPosition": self.primary_contact_position if self.primary_contact_position else False,
                            "PrimaryContactPhone": self.primary_contact_phone if self.primary_contact_phone else False,
                            "SecondaryContactName": self.secondary_contact_name if self.secondary_contact_name else False,
                            "SecondaryContactPosition": self.secondary_contact_position if self.secondary_contact_position else False,
                            "AdditionalNotes": self.comment if self.comment else False,
                            "IsActive": self.is_active if self.is_active else False,
                            "Notify": self.notify if self.notify else False,
                            "PhoneExtension": self.phone_extenstion if self.phone_extenstion else False
                        })

                    response = requests.request("POST", url, headers=headers, data=payload)
                    response_dict = json.loads(response.text)
                    if response_dict.get('Success') == True:
                        print('response successful')
                    else:
                        raise ValidationError(_(str(response_dict.get('Message'))))
                else:
                    raise ValidationError(_(str('Some required fields in Smarttship are empty.')))
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_package = fields.Many2one('product.packaging', string='Delivery Package')