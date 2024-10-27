# -*- coding: utf-8 -*-

from odoo import models, api, fields
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


def should_generate_invoice(order):
    return order.partner_id


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def create_from_ui(self, orders, draft=False):
        _logger.info('Creating POS order from UI')

        # Retrieve the auto_invoice setting from the configuration
        auto_invoice_enabled = self._get_auto_invoice_enabled()

        _logger.info('Auto invoice enabled: %s', auto_invoice_enabled)

        if not auto_invoice_enabled:
            return super(PosOrder, self).create_from_ui(orders, draft)

        # Before process order in parent model, check if the order has a customer and if it does, generate invoice
        for order in orders:
            if not order['data']['partner_id']:
                _logger.warning('The order does not have a customer')
                raise UserError('The order does not have a customer')

            order['data']['to_invoice'] = True

        order_result = super(PosOrder, self).create_from_ui(orders, draft)

        _logger.info('POS order created from UI with invoice')

        return order_result

    def cron_generate_invoices_for_pos_orders(self):
        _logger.info('Cron job to generate invoices for POS orders started')

        auto_invoice_enabled = self._get_auto_invoice_enabled()

        _logger.info('Auto invoice enabled: %s', auto_invoice_enabled)

        if not auto_invoice_enabled:
            return

        # Retrieve all POS orders that are paid or done but not yet invoiced
        pos_orders = self.search([('state', 'in', ['paid', 'done']), ('account_move', '=', False)])

        _logger.info('Found %s POS orders to generate invoices for', len(pos_orders))

        for order in pos_orders:
            # Check if the invoice generation method exists
            if hasattr(order, '_generate_pos_order_invoice'):

                if not order.partner_id:
                    _logger.warning('The order %s does not have a customer', order.name)
                    continue

                _logger.info('Generating invoice for POS order %s', order.name)
                order.action_pos_order_invoice()
            else:
                _logger.warning('POS order %s does not have the method to generate an invoice', order.name)

    def _get_auto_invoice_enabled(self):
        return self.env['ir.config_parameter'].sudo().get_param('pos.auto_invoice', default=False)

    def cron_adjust_posted_orders_for_invoicing(self):
        _logger.info('Adjusting posted orders for potential invoicing')

        posted_orders = self.search([('state', '=', 'done'), ('account_move', '=', False)])
        _logger.info('Found %s posted orders without invoices', len(posted_orders))

        for order in posted_orders:
            try:

                if should_generate_invoice(order):
                    order.write({'state': 'paid'})
                    _logger.info('Order %s adjusted to allow invoicing', order.name)
                    invoice_result = order.action_pos_order_invoice()
                    if invoice_result:
                        account_move = self.env['account.move'].browse(invoice_result['res_id'])
                        account_move.write({'state': 'draft'})
                        account_move.action_post()
                else:
                    _logger.info('Order %s does not meet criteria for invoicing', order.name)
            except Exception as e:
                _logger.error('Failed to adjust order %s for invoicing: %s', order.name, str(e))

