# Copyright 2019 Digital5 S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import float_is_zero


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("purchase_vendor_bill_id", "purchase_id")
    def _onchange_purchase_auto_complete(self):
        """
        after the creation of the lines, delete the zero qty lines
        if the journal is marked as such
        """
        purchase = self.purchase_id or self.purchase_vendor_bill_id.purchase_order_id
        super()._onchange_purchase_auto_complete()
        if purchase and self.journal_id and self.journal_id.avoid_zero_lines:
            zero_lines = self.invoice_line_ids.filtered(
                lambda x: float_is_zero(
                    x.quantity, precision_rounding=x.product_uom_id.rounding,
                )
                and x.purchase_line_id.order_id == purchase
            )
            # The bellow lines are needed for delete the invoice lines, the first one
            # is used when the invoice is created manually, using the field
            # purchase_vendor_bill_id and the other one when the invoice is created
            # using the button "Create Bill" on the purchase orders.
            self.invoice_line_ids -= zero_lines
            self.line_ids -= zero_lines
