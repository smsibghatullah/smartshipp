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



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    smarttship_product_id = fields.Integer(string='Smarttship Product ID')
    shipper_id = fields.Integer(string='Shipper ID')
    is_smarttship_product = fields.Boolean(string='Is Smarttship Product')
    is_dg_product = fields.Boolean(string='Is DG Product')
    is_dangerous = fields.Boolean(string='Is Dangerous')
    is_ship_to_from_usa = fields.Boolean(string='Is Ship to from USA')
    dg_class = fields.Char(string='DG Class')
    dg_class_suffix = fields.Char(string='DG Class Suffix')
    dg_group = fields.Char(string='DG Group')
    dg_number = fields.Char(string='DG Number')
    emergency_phone_number = fields.Char(string='Emergency Phone Number')
    subsidiary_class = fields.Char(string='Subsidiary Class')

    @api.model
    def create(self, vals):
        rec = super(ProductTemplate, self).create(vals)
        if rec.is_smarttship_product == True:
            headers = {
                'apikey': '7474CAE8-35BA-47DE-983D-2DE16EDEB118',
                'Content-Type': 'application/json'
            }
            url = "https://api.sandbox.smarttshipping.ca/api/carrierApi/AddOrEditProduct"
            payload = json.dumps({
                "ProductID": 0,
                "ProductName": rec.name,
                "IsDangerous": rec.is_dangerous,
                "IsShipToFromUSA": rec.is_ship_to_from_usa,
                "DGClass": rec.dg_class,
                "DGClassSuffix": rec.dg_class_suffix,
                "DGGroup": rec.dg_group,
                "DGNumber": rec.dg_number,
                "EmergencyPhoneNumber": rec.emergency_phone_number,
                "SubsidiaryClass": rec.subsidiary_class,
            })
            response = requests.request("POST", url, headers=headers, data=payload)
            response_dict = json.loads(response.text)
            if response_dict.get('Success') == True:
                rec.smarttship_product_id = response_dict.get('Data').get('ProductID')
                rec.shipper_id = response_dict.get('Data').get('ShipperID')
            else:
                raise ValidationError(_(str(response_dict.get('Message'))))
        return rec