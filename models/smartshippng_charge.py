from odoo import models, fields

class SmartshipShippingCharge(models.Model):
    _name = "smartship.shipping.charge"
    _rec_name = "smartship_service_name"

    smartship_carrier_id = fields.Char(string="carrier id",help="smartship carrier id")
    smartship_carrier_name = fields.Char(string="carrier name", help="smartship courier name")
    smartship_service_id = fields.Char(string="service id",help="smartship service id")
    smartship_service_name = fields.Char(string="service name", help="smartship service name")
    smartship_total_charge = fields.Float(string="total charge", help="rate given by smartship")
    sale_order_id = fields.Many2one("sale.order", string="sales order")
    carrier_body = fields.Text(string="Carrier Body")

    def set_service(self):
        self.ensure_one()
        carrier = self.sale_order_id.carrier_id
        # self.sale_order_id._remove_delivery_line()
        self.sale_order_id.smartship_shipping_charge_id = self.id
        # self.sale_order_id.delivery_price = float(self.freightcom_total_charge)
        self.sale_order_id.carrier_id = carrier.id
        self.sale_order_id.set_delivery_line(carrier,self.smartship_total_charge) #this line used for set updated rate in sale order line
