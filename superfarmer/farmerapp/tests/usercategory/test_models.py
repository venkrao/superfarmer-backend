from rest_framework.test import APITestCase
from superfarmer.farmerapp.models import UserCategory


class BaseTestCase(APITestCase):
    category_name = "buyer"
    category_id = 1

    def setUp(self):
        self.user_category = UserCategory.objects.create(category_name="buyer", category_id=1)

    def test_user_category_table_must_have_category_name_and_category_id(self):
        self.assertEqual(self.user_category.category_name, self.category_name)
        self.assertEqual(self.user_category.category_id, self.category_id)