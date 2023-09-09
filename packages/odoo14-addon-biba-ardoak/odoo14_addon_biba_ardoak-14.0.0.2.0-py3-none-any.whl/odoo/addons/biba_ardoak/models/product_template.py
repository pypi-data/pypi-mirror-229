from odoo import api, fields, models


class ProductColor(models.Model):
    _name = "product.color"
    _description = "Color"

    name = fields.Char(string="Color")


class ProductTier(models.Model):
    _name = "product.tier"
    _description = "Product Tier"

    name = fields.Char(string="Product Tier")


class ProductType(models.Model):
    _name = "product.type"
    _description = "Product Type"

    name = fields.Char(string="Product Type")


class ProductZone(models.Model):
    _name = "product.zone"
    _description = "Product Zone"

    name = fields.Char(string="Product Zone")


class ProductClimate(models.Model):
    _name = "product.climate"
    _description = "Product Climate"

    name = fields.Char(string="Product Climate")


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_color = fields.Many2one("product.color", string="Color")
    product_tier = fields.Many2one("product.tier", string="Tier")
    product_type = fields.Many2one("product.type", string="Type")
    product_zone = fields.Many2one("product.zone", string="Zone")
    product_climate = fields.Many2one("product.climate", string="Climate")
