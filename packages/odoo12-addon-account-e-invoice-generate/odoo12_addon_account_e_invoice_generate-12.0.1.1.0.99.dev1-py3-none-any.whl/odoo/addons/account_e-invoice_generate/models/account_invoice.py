# Copyright 2018 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def get_payment_identifier(self):
        """This method is designed to be inherited in localization modules"""
        self.ensure_one()
        return None

    @api.model
    def _get_invoice_report_names(self):
        return [
            'account.report_invoice',
            'account.report_invoice_with_payments']
