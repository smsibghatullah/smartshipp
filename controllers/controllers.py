# -*- coding: utf-8 -*-
# from odoo import http


# class SmartShippingIntegration(http.Controller):
#     @http.route('/smart_shipping_integration/smart_shipping_integration/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/smart_shipping_integration/smart_shipping_integration/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('smart_shipping_integration.listing', {
#             'root': '/smart_shipping_integration/smart_shipping_integration',
#             'objects': http.request.env['smart_shipping_integration.smart_shipping_integration'].search([]),
#         })

#     @http.route('/smart_shipping_integration/smart_shipping_integration/objects/<model("smart_shipping_integration.smart_shipping_integration"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('smart_shipping_integration.object', {
#             'object': obj
#         })
