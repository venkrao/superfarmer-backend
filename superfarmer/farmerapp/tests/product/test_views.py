from rest_framework.test import APITestCase
from django.urls import reverse
from superfarmer.farmerapp.models import Product, ProductCategory
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
import json
from superfarmer.farmerapp.serializer import ProductSerializer
import ast

class ProductViewTestCase(APITestCase, ):
    url = reverse('product-list')
    expected_data = [{'product_name': 'groundnuts',
                     'product_category': 10,
                     'product_default_image': 'undefined',
                     'product_category_id': 10}]

    def setUp(self):
        self.product_category = ProductCategory.objects.create(category_name="grains", category_id=10)
        self.product = Product.objects.create(
            product_name="groundnuts", product_category=self.product_category, product_default_image="undefined",
            product_category_id=self.product_category.category_id
        )
        self.username = "john"
        self.email = "john@snow.com"
        self.password = "you_know_nothing"
        self.user = User.objects.create_user(self.username, self.email, self.password)
        self.client.login(username=self.username, password=self.password)

    def test_product_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertEqual(response_data, self.expected_data)


