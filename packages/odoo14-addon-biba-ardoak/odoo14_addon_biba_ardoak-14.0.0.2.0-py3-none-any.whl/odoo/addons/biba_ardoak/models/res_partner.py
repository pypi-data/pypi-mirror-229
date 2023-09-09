from odoo import fields, models


class PartnerZone(models.Model):
    _name = "partner.zone"
    _description = "Zone"

    name = fields.Char(string="Zone")


class PartnerType(models.Model):
    _name = "partner.type"
    _description = "Type"

    name = fields.Char(string="Type")


class PartnerTier(models.Model):
    _name = "partner.tier"
    _description = "Tier"

    name = fields.Char(string="Tier")


class ResPartner(models.Model):
    _inherit = "res.partner"

    partner_zone = fields.Many2one("partner.zone", string="Zone")
    partner_type = fields.Many2one("partner.type", string="Type")
    partner_tier = fields.Many2one("partner.tier", string="Tier")
