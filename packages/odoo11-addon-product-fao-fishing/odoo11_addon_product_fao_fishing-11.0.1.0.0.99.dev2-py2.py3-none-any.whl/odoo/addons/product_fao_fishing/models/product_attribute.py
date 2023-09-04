# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductAttributeValue(models.Model):

    _inherit = 'product.attribute.value'

    fao_zone_code = fields.Char(string='Zone Code')
