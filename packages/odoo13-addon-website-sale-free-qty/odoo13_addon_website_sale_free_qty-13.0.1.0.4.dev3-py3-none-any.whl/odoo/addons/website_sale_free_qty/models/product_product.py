# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class Product(models.Model):
    _inherit = "product.product"

    def _compute_quantities_dict(
        self, lot_id, owner_id, package_id, from_date=False, to_date=False
    ):
        res = super()._compute_quantities_dict(
            lot_id, owner_id, package_id, from_date, to_date
        )
        if self.env.context.get("website_sale_free_qty"):
            for product in self.with_context(website_sale_free_qty=False):
                res[product.id]["virtual_available"] = res[product.id]["free_qty"]
        return res
