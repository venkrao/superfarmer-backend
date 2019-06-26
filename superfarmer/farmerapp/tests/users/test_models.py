from rest_framework.test import APITestCase
from superfarmer.farmerapp.models import RegistrationStatus, UserStatus, Users
from django.utils.timezone import now

class BaseTestCase(APITestCase):
    user_id = 1001
    user_status_id = 1001
    user_status_expected = "unverified"
    email_address = "blah@blah.com"
    name = "mrx"
    member_since = now()
    registration_status = "verification_pending"
    registration_status_id = 1001

    def setUp(self):
        self.user_staus = UserStatus.objects.create(status_id=self.user_status_id, status=self.user_status_expected)
        self.registration_status = RegistrationStatus.objects.create(status=self.registration_status,
                                                                     status_id=self.registration_status_id)

        self.user = Users.objects.create(user_id=self.user_id, user_status=self.user_staus,
                                         email_address=self.email_address, name=self.name,
                                         registration_status=self.registration_status,
                                         member_since=self.member_since)

    def test_users_table_must_have_predefined_columns(self):
        self.assertEqual(self.user.user_id, self.user_id)
        self.assertEqual(self.user.user_status.status, self.user_status_expected)
        self.assertEqual(self.user.email_address, self.email_address)
        self.assertEqual(self.user.name, self.name)
        self.assertEqual(self.user.member_since, self.member_since)