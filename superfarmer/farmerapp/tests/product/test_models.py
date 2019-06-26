from rest_framework.test import APITestCase
from superfarmer.farmerapp.models import Product, ProductCategory


class BaseTestCase(APITestCase):
    def setUp(self):
        self.product_category = ProductCategory.objects.create(category_name="grains")
        self.product = Product.objects.create(
            product_name="groundnuts", product_category=self.product_category, product_default_image="undefined",
            product_category_id=self.product_category.category_id
        )

    def test_product_category_in_product_table_must_be_foreign_key_to_product_category(self):
        self.assertEqual(self.product_category, self.product.product_category)