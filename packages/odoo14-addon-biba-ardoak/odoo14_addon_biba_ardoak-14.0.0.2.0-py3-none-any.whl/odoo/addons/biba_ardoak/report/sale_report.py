from odoo import fields, models, tools


class SaleReport(models.Model):
    _inherit = "sale.report"

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

    def _from_sale(self, from_clause=""):
        # import ipdb; ipdb.set_trace()
        res = super()._from_sale(from_clause)
        res += """
        left join partner_tier p_tier on (partner.partner_tier=p_tier.id)
        left join partner_type p_type on (partner.partner_type=p_type.id)
        left join partner_zone p_z on (partner.partner_zone=p_z.id)
        left join product_color pr_c on (t.product_color=pr_c.id)
        left join product_tier pr_tier on (t.product_tier=pr_tier.id)
        left join product_type pr_type on (t.product_type=pr_type.id)
        left join product_zone pr_z on (t.product_zone=pr_z.id)
        left join product_climate pr_cl on (t.product_climate=pr_cl.id)
        """
        return res

    def _group_by_sale(self, groupby=""):
        res = super()._group_by_sale(groupby)
        res += """
        , p_tier.id
        , p_type.id
        , p_z.id
        , pr_c.id
        , pr_tier.id
        , pr_type.id
        , pr_z.id
        , pr_cl.id
        """
        return res

    def _select_additional_fields(self, fields):
        fields[
            "partner_tier",
            "partner_type",
            "partner_zone",
            "product_color",
            "product_tier",
            "product_type",
            "product_zone",
            "product_climate",
        ] = ", p_tier.id as partner_tier, p_type.id as partner_type, p_z.id as partner_zone, pr_c.id as product_color, pr_tier.id as product_tier, pr_type.id as product_type, pr_z.id as product_zone, pr_cl.id as product_climate"
        return super()._select_additional_fields(fields)
