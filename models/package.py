from odoo import models, fields,_,api
import logging
# import request
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

        # url = "https://api.smarttshipping.ca/api/carrierApi/GetAllPackages"
        #
        # payload = json.dumps({
        # "Packages": [
        #     {
        #         "PackageID": 3127,
        #         "ShipperID": 313,
        #         "PackageTypeName": "Baljeet",
        #         # "DateAdded": "2016-09-29T10:31:53.297",
        #         # "DateEdited": "2018-04-12T00:00:00",
        #         "IsActive": True,
        #         "IsDefaultPackageType": False,
        #         "CarrierId": 0,
        #         "width":0,
        #         "height": 0,
        #         "length": 0,
        #         "is"
        #     }
        # ]
        # }
        # )




        return rec



