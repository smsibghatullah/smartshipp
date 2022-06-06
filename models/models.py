import logging
import requests
import json

from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError, UserError

_logger = logging.getLogger("Smartshipping")


class SaleOrder(models.Model):
    _inherit = "sale.order"

    smartship_shipping_charge_ids = fields.One2many("smartship.shipping.charge", "sale_order_id", string="Smartship Rate ")
    smartship_shipping_charge_id = fields.Many2one("smartship.shipping.charge", string="Smartship Service",help="This Method Is Use Full For Generating The Label",copy=False)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[("smartship", "SmartShip")],ondelete={'smartship': 'set default'})
    package_id = fields.Many2one('product.packaging', string="package", help="please select package type")

    def smartship_rate_shipment(self, orders):

        weight = sum(
            [(line.product_id.weight * line.product_uom_qty) for line in orders.order_line if not line.is_delivery])
        shipper_address = orders.warehouse_id and orders.warehouse_id.partner_id
        recipient_address = orders.partner_shipping_id

        # sender_data.attrib["id"] = str(shipper_address.id)
        # sender_data.attrib["company"] = shipper_address.name
        # sender_data.attrib["address1"] = "%s" % (shipper_address.street or "")
        # sender_data.attrib["city"] = "%s" % (shipper_address.city or "")
        # sender_data.attrib["state"] = "%s" % (shipper_address.state_id and shipper_address.state_id.code or "")
        # sender_data.attrib["country"] = "%s" % (shipper_address.country_id and shipper_address.country_id.code or "")
        # sender_data.attrib["zip"] = "%s" % (shipper_address.zip or "")
        # sender_data.attrib["phone"] = "%s" % (shipper_address.phone or "")
        # sender_data.attrib["attention"] = "%s" % (shipper_address.name)
        # sender_data.attrib["email"] = "%s" % (shipper_address.email)


        url = "https://api.sandbox.smarttshipping.ca/api/carrierapi/GetCarrierRates"

        payload = json.dumps({
            "IsImperial": True,
            "ShipmentItems": [
                {
                    "Quantity": 1,
                    "Width": 5,
                    "Length": 5,
                    "Height": 6,
                    "Weight": weight,
                    "PackageId": "85",
                    "ProductId": "3076",
                    "IsStackable": True,
                    "IsDangerous": False,
                    "ShipmentContainsDGItems": []
                }
            ],
            "TermId": "2",
            "ShipmentCustomers": [
                {
                    "CustomerId": 0,
                    "CityId": 24354,
                    "City": shipper_address.city or "",
                    "StateId": "%s" % (shipper_address.state_id and shipper_address.state_id.id or ""),
                    "countryId": "%s" % (shipper_address.country_id and shipper_address.country_id.id or ""),
                    "Name": shipper_address.name,
                    "PostalCode": "%s" % (shipper_address.zip or ""),
                    "IsShipFrom": "false"
                }
            ],
            "Services": [],
            "ShipmentTypeId": "1",
            "IsAllServices": True,
            "Fragile": "false",
            "SaturdayDelivery": "false",
            "NoSignatureRequired": "true",
            "ResidentialSignature": "false",
            "SpecialHandling": "false",
            "IsReturnShipment": "false",
            "DropOff": "false"
        })
        headers = {
            'apikey': '7474CAE8-35BA-47DE-983D-2DE16EDEB118',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response_dicts = json.loads(response.text)
        # print(response_data.text)
        smartship_shipping_charge_obj = self.env['smartship.shipping.charge']

        existing_records = smartship_shipping_charge_obj.search([('sale_order_id', '=', orders and orders.id)])
        existing_records.sudo().unlink()

        if response.status_code in [200, 201]:
            # api = Response(response_data)
            # response_data = api.dict()
            for response_dict in response_dicts['Carriers']:
                smartship_carrier_id = response_dict.get('CarrierId')
                smartship_carrier_name = response_dict.get('CarrierName')
                smartship_service_id = response_dict.get('ServiceCode')
                smartship_service_name = response_dict.get('ServiceName')
                smartship_total_charge = response_dict.get('Price')
                smartship_shipping_charge_obj.sudo().create(
                    {
                        'smartship_carrier_id': smartship_carrier_id,
                        'smartship_carrier_name': smartship_carrier_name,
                        'smartship_service_id': smartship_service_id,
                        'smartship_service_name': smartship_service_name,
                        'smartship_total_charge': smartship_total_charge,
                        'sale_order_id': orders and orders.id
                    }
                )
            smartship_charge_id = smartship_shipping_charge_obj.search(
                    [('sale_order_id', '=', orders and orders.id)], order='smartship_total_charge', limit=1)
            orders.smartship_shipping_charge_id = smartship_charge_id and smartship_charge_id.id
            return {'success': True,
                        'price': smartship_charge_id and smartship_charge_id.smartship_total_charge or 0.0,
                        'error_message': False, 'warning_message': False}
        else:
            return {'success': False, 'price': 0.0, 'error_message': "%s %s" % (response, response.text),
                    'warning_message': False}

        return {'success': True,
                'price': 9.0,
                'error_message': False, 'warning_message': False}

    @api.model
    def smartship_send_shipping(self, pickings):
        """This Method Is Used For Send The Shipping Request To Shipper"""
        response = []
        for picking in pickings:
            total_bulk_weight = picking.weight_bulk
            recipient_address = picking.partner_id
            shipper_address = picking.picking_type_id.warehouse_id.partner_id

            import requests
            import json

            url = "https://api.sandbox.smarttshipping.ca/api/carrierapi/CreateDispatch"

            payload = json.dumps({
                "IsImperial": True,
                "ShipmentItems": [
                    {
                        "Quantity": 1,
                        "Width": 5,
                        "Length": 5,
                        "Height": 6,
                        "Weight": total_bulk_weight,
                        "PackageId": "85",
                        "ProductId": 3076,
                        "IsStackable": True,
                        "IsDangerous": False,
                        "ShipmentContainsDGItems": []
                    }
                ],
                "TermId": "2",
                "ShipmentCustomers": [
                    {
                        "CustomerId": 0,
                        "CityId": 24354,
                        "City": "Hedley",
                        "StateId": 6,
                        "countryId": 1,
                        "Name": "TEST CONSGINEE",
                        "PostalCode": "V0X 1K0",
                        "IsShipFrom": "false",
                        "Address": "123 MAIN STREET",
                        "Phone": "6667778888",
                        "Email": "test@email.com"
                    }
                ],
                "Services": [],
                "ShipmentTypeId": "1",
                "IsAllServices": True,
                "Fragile": "false",
                "SaturdayDelivery": "false",
                "NoSignatureRequired": "true",
                "ResidentialSignature": "false",
                "SpecialHandling": "false",
                "IsReturnShipment": "false",
                "DropOff": "false",
                "SelectedCarrier": {
                    "CarrierId": 2931,
                    "CarrierName": "CANADA POST",
                    "TransitDays": "6",
                    "ServiceName": "Library Materials",
                    "ServiceCode": "DOM.LIB",
                    "Price": 6.33,
                    "CarrierQuoteNumber": "",
                    "APIRatesEnabled": True,
                    "APIDocumentEnabled": True,
                    "APIDispatchEnabled": True,
                    "IsPriceInUsd": False,
                    "PickupAvailableFromDate": "2022-05-26",
                    "Message": None,
                    "Currency": "CAD"
                }
            })
            headers = {
                'apikey': '7474CAE8-35BA-47DE-983D-2DE16EDEB118',
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            print(response.text)

            return [response]



            # freightcom_request = etree.Element("Freightcom")
            # freightcom_request.attrib['xmlns'] = "http://www.freightcom.net/XMLSchema"
            # freightcom_request.attrib['username'] = self.company_id and self.company_id.freightcom_username
            # freightcom_request.attrib['password'] = self.company_id and self.company_id.freightcom_password
            # freightcom_request.attrib['version'] = "3.1.0"
            #
            # shipping_request = etree.SubElement(freightcom_request, "ShippingRequest")
            # shipping_request.attrib['serviceId'] = str(
            #     picking.sale_id.freightcom_shipping_charge_id.freightcom_service_id)
            # shipping_request.attrib['stackable'] = "true"
            #
            # sender_data = etree.SubElement(shipping_request, "From")
            # sender_data.attrib["id"] = str(shipper_address.id or "")
            # sender_data.attrib["company"] = "%s" % (shipper_address.name or "")
            # sender_data.attrib["address1"] = "%s" % (shipper_address.street or "")
            # sender_data.attrib["city"] = "%s" % (shipper_address.city or "")
            # sender_data.attrib["state"] = "%s" % (shipper_address.state_id and shipper_address.state_id.code or "")
            # sender_data.attrib["country"] = "%s" % (
            #         shipper_address.country_id and shipper_address.country_id.code or "")
            # sender_data.attrib["zip"] = "%s" % (shipper_address.zip or "")
            # sender_data.attrib["phone"] = "%s" % (shipper_address.phone or "")
            # sender_data.attrib["attention"] = "%s" % (shipper_address.name or "")
            # sender_data.attrib["email"] = "%s" % (shipper_address.email or "")
            #
            # receiver_data = etree.SubElement(shipping_request, "To")
            # receiver_data.attrib["company"] = "%s" % (recipient_address.name or "")
            # receiver_data.attrib["address1"] = "%s" % (recipient_address.street or "")
            # receiver_data.attrib["city"] = "%s" % (recipient_address.city or "")
            # receiver_data.attrib["state"] = "%s" % (
            #             recipient_address.state_id and recipient_address.state_id.code or "")
            # receiver_data.attrib["country"] = "%s" % (
            #         recipient_address.country_id and recipient_address.country_id.code or "")
            # receiver_data.attrib["zip"] = "%s" % (recipient_address.zip or "")
            # receiver_data.attrib["phone"] = "%s" % (recipient_address.phone or "")
            # receiver_data.attrib["attention"] = "%s" % (recipient_address.name or "")
            # receiver_data.attrib["email"] = "%s" % (recipient_address.email or "")
            #
            # packages_data = etree.SubElement(shipping_request, "Packages")
            # packages_data.attrib["type"] = "Package"
            # for package_id in pickings.package_ids:
            #     package_data = etree.SubElement(packages_data, "Package")
            #     package_data.attrib["length"] = str(package_id.packaging_id and package_id.packaging_id.packaging_length or 0)
            #     package_data.attrib["width"] = str(package_id.packaging_id and package_id.packaging_id.width or 0)
            #     package_data.attrib["height"] = str(package_id.packaging_id and package_id.packaging_id.height or 0)
            #     if package_id.packaging_id.max_weight < package_id.shipping_weight:
            #         raise ValidationError("Shipping Weight Is More Than Max Weight ")
            #     package_data.attrib["weight"] = str(package_id.shipping_weight or 0)
            # if total_bulk_weight:
            #     package_data = etree.SubElement(packages_data, "Package")
            #     package_data.attrib["length"] = str(self.package_id and self.package_id.packaging_length or 0)
            #     package_data.attrib["width"] = str(self.package_id and self.package_id.width or 0)
            #     package_data.attrib["height"] = str(self.package_id and self.package_id.height or 0)
            #     if self.package_id.max_weight < total_bulk_weight:
            #         raise ValidationError("Shipping Weight Is More Than Max Weight ")
            #     package_data.attrib["weight"] = str(total_bulk_weight or 0)
            # if shipper_address.country_id.code != recipient_address.country_id.code:
            #     customs_invoice = etree.SubElement(shipping_request, "CustomsInvoice")
            #     bill_to = etree.SubElement(customs_invoice, "BillTo")
            #     bill_to.attrib['company'] = str(shipper_address.name)
            #     bill_to.attrib['name'] = str(shipper_address.name)
            #     bill_to.attrib['address1'] = str(shipper_address.street)
            #     bill_to.attrib['city'] = str(shipper_address.city)
            #     bill_to.attrib['state'] = str(shipper_address.state_id and shipper_address.state_id.code)
            #     bill_to.attrib['zip'] = str(shipper_address.zip)
            #     bill_to.attrib['country'] = str(shipper_address.country_id and shipper_address.country_id.code)
            #
            #     contact = etree.SubElement(customs_invoice, "Contact")
            #     contact.attrib['name'] = str(shipper_address.name)
            #     contact.attrib['phone'] = str(shipper_address.phone)
            #
            #     # item = etree.SubElement(customs_invoice, "Item")
            #     for order in picking.sale_id.order_line.filtered(lambda order_line : order_line.is_delivery == False):
            #         item = etree.SubElement(customs_invoice, "Item")
            #         item.attrib['code'] = str(order.product_id.hs_code or "")
            #         item.attrib['description'] = str(order.product_id.name or "")
            #         item.attrib['originCountry'] = str(shipper_address.country_id and shipper_address.country_id.code)
            #         item.attrib['quantity'] = str(int(picking.move_lines.product_uom_qty or 0))
            #         item.attrib['unitPrice'] = str(int(order.price_unit or 0))
            #         item.attrib['weight'] = str(int(order.product_id.weight or 0))
            # try:
            #     headers = {'Content-Type': 'application/xml'}
            #     url = self.company_id and self.company_id.freightcom_url
            #     _logger.info("Shipment Request Data::::%s" % etree.tostring(freightcom_request))
            #     response_data = requests.request(method="POST", url=url, headers=headers,
            #                                      data=etree.tostring(freightcom_request))
            #     _logger.info("Shipment Response Data::::%s" % response_data.content)
            #     if response_data.status_code in [200, 201]:
            #         api = Response(response_data)
            #         response_data = api.dict()
            #
            #         order_number = response_data.get('Freightcom') and response_data.get('Freightcom').get(
            #             'ShippingReply') and \
            #                        response_data.get('Freightcom').get('ShippingReply').get('Order') and \
            #                        response_data.get('Freightcom').get('ShippingReply').get('Order').get('_id')
            #         if not order_number:
            #             raise ValidationError("Response Data : %s" % (response_data))
            #         tracking_url = response_data.get('Freightcom') and response_data.get('Freightcom').get(
            #             'ShippingReply') and \
            #                        response_data.get('Freightcom').get('ShippingReply').get('TrackingURL')
            #
            #         package_list = response_data.get('Freightcom').get('ShippingReply').get('Package')
            #         if isinstance(package_list, dict):
            #             package_list = [package_list]
            #         tracking_data = []  # Store single or multiple tracking number
            #         for package in package_list:  # This Loop Is Used For Store Tracking Number in Tracking_Data[]
            #             tracking_data.append(
            #                 package.get('_trackingNumber'))  # append function used for add value in tracking_data[]
            #         label_data = response_data.get('Freightcom') and response_data.get('Freightcom').get(
            #             'ShippingReply') and response_data.get('Freightcom').get('ShippingReply').get('Labels')
            #
            #         picking.freightcom_tracking_url = tracking_url
            #         picking.freightcom_order_id = order_number
            #         binary_data = binascii.a2b_base64(
            #             str(label_data))  # This Function is Used For Convert Base64 Label data in PDF formate
            #         logmessage = ("<b>Tracking Number:</b> %s") % (tracking_data)
            #         picking.message_post(body=logmessage, attachments=[("%s.pdf" % (order_number), binary_data)])
            #
            #         custom_invoice = response_data.get('Freightcom') and response_data.get('Freightcom').get(
            #             'ShippingReply') and response_data.get('Freightcom').get('ShippingReply').get('CustomsInvoice')
            #         if custom_invoice:
            #             picking.freightcom_tracking_url = tracking_url
            #             picking.freightcom_order_id = order_number
            #             binary_data_custom = binascii.a2b_base64(
            #                 str(custom_invoice))  # This Function is Used For Convert Base64 Label data in PDF formate
            #             logmessage = ("<b>Tracking Number:</b> %s") % (tracking_data)
            #             picking.message_post(body=logmessage, attachments=[("%s.pdf" % (order_number), binary_data_custom)])
            #             shipping_data = {'exact_price': 0.0, 'tracking_number': ','.join(tracking_data)}
            #         response += [shipping_data]
            #         return response
            #     else:
            #         raise ValidationError(response_data.content)
            #
            # except Exception as e:
            #     raise ValidationError(e)
            #
