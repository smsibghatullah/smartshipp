import logging
import requests
import json

from odoo import models, fields, api, _



class SmarttshipSync(models.Model):
    _name = "smarttship.sync"

    sync_city = fields.Boolean(string='Sync Cities')


    def sync_records(self):
        print('testing')
        if self.sync_city:
            self.fetch_cities()

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

class ResCitySmartship(models.Model):
    _name = "res.city.smarttship"

    city_id = fields.Integer(string='City ID')
    city_name = fields.Char(string='City Name')


