import logging
import requests
import json
import random
import string
from odoo import models, fields, api, _


class ResCountryState(models.Model):
    _inherit = "res.country.state"

    smarttship_state_id = fields.Integer(string='Sync Cities')
    smarttship_state_code = fields.Char(string='Smarttship State Code')


class SmarttshipSync(models.Model):
    _name = "smarttship.sync"

    sync_city = fields.Boolean(string='Sync Cities')
    sync_state = fields.Boolean(string='Sync States')


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
            for city in response.get('Cities'):
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


