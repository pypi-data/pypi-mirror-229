from odoo import fields, models
from odoo.tools import float_compare, float_round


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Fields used on sale reports pivot view
    partner_tier = fields.Many2one("partner.tier", string="Partner Tier", readonly=True)
    partner_type = fields.Many2one("partner.type", string="Partner Type", readonly=True)
    partner_zone = fields.Many2one("partner.zone", string="Partner Zone", readonly=True)
    product_color = fields.Many2one(
        "product.color", string="Product Color", readonly=True
    )
    product_tier = fields.Many2one("product.tier", string="Product Tier", readonly=True)
    product_type = fields.Many2one("product.type", string="Product Type", readonly=True)
    product_zone = fields.Many2one("product.zone", string="Product Zone", readonly=True)
    product_climate = fields.Many2one(
        "product.climate", string="Product Climate", readonly=True
    )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _check_package(self):
        default_uom = self.product_id.uom_id
        pack = self.product_packaging
        qty = self.product_uom_qty
        q = default_uom._compute_quantity(pack.qty, self.product_uom)
        # We do not use the modulo operator to check if qty is a
        # mltiple of q. Indeed the quantity
        # per package might be a float, leading to incorrect results.
        # For example:
        # 8 % 1.6 = 1.5999999999999996
        # 5.4 % 1.8 = 2.220446049250313e-16
        if (
            qty
            and q
            and float_compare(
                qty / q,
                float_round(qty / q, precision_rounding=1.0),
                precision_rounding=0.001,
            )
            != 0
        ):
            newqty = qty - (qty % q) + q
            self.product_uom_qty = newqty
        return {}
