from odoo import models, fields,_,api
from odoo.exceptions import ValidationError
import logging
import requests
import json

# class SmartshipShippingPackage(models.Model):
#     _name = "smartship.shipping.package"
#
#     smarship_package_name = fields.Char(string="Package Name")
#     smart_date_aaded = fields.Datetime(string="Date Added")
#     smart_date_edited = fields.Datetime(string="Date Edited")
#     width = fields.Char(string="Width")
#     height = fields.Char(string="Height")
#     is_default_pkg_type = fields.Boolean()
#     max_weight = fields.Char()
#     is_courier = fields.Boolean()
#     shipper_id = fields.Char()

class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    package_carrier_type = fields.Selection(selection_add=[("smartship", "SmartShip")])
    carrier_record_id = fields.Integer()
    smart_date_aaded = fields.Datetime(string="Date Added")
    smart_date_edited = fields.Datetime(string="Date Edited")
    is_courier = fields.Boolean()
    shipper_id = fields.Integer()
    pkg_id = fields.Integer()
    is_active = fields.Boolean()
    is_default_type = fields.Boolean()


    @api.model
    def create(self, vals):
        rec = super(ProductPackaging, self).create(vals)
        if rec.package_carrier_type == 'smartship':
            headers = {
                'apikey': '7474CAE8-35BA-47DE-983D-2DE16EDEB118',
                'Content-Type': 'application/json'
            }
            url = "https://api.sandbox.smarttshipping.ca/api/carrierApi/AddOrEditPackage"
            payload = json.dumps({
                    "PackageId": 0,
                    "PackageName": str(rec.name),
                    # "PackageTypeName": "Baljeet",
                    # "DateAdded": "2016-09-29T10:31:53.297",
                    # "DateEdited": "2018-04-12T00:00:00",
                    # "IsActive": True,
                    # "IsDefaultPackageType": False,
                    # "CarrierId": 4,
                    # "Width":3,
                    # "Height": 1,
                    # "Length": 2,
                    # "IsCourier": True
                })

            response = requests.request("POST", url, headers=headers, data=payload)
            response_dict = json.loads(response.text)
            if response_dict.get('Success') == True:
                rec.pkg_id = response_dict.get('Package').get('PackageID')
                rec.shipper_id = response_dict.get('Package').get('ShipperID')
            else:
                raise ValidationError(_(str(response_dict.get('Message'))))
        return rec



