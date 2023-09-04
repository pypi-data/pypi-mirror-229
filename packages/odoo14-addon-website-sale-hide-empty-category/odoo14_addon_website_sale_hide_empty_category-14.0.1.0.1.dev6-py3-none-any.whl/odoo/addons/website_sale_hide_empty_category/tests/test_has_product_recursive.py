from odoo.tests import common


class TestPublicCategory(common.TransactionCase):
    def test_has_product_recursive(self):

        category_1 = self.env["product.public.category"].create({"name": "Category 1"})

        self.assertFalse(category_1.has_product_recursive)

        category_2 = self.env["product.public.category"].create(
            {"name": "Category 2", "parent_id": category_1.id}
        )

        self.assertFalse(category_2.has_product_recursive)

        self.env["product.template"].create(
            {"name": "Product Test", "public_categ_ids": [(4, category_2.id, None)]}
        )

        self.assertTrue(category_1.has_product_recursive)
        self.assertTrue(category_2.has_product_recursive)
