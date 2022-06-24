from odoo import fields, models, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    smartship_tracking_url = fields.Char(string="SmartShip Tracking Url", help="Tracking URL")
    smartship_order_id = fields.Char(string="SmartShip Order Id")
