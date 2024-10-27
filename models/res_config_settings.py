# -*- coding: utf-8 -*-

from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_auto_invoice = fields.Boolean(string='Generate Invoice Automatically',
                                      config_parameter='pos.auto_invoice', readonly=False,
                                      help="When enabled, POS orders will automatically generate an invoice when the order is processed.")