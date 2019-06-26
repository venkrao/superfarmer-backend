from rest_framework.test import APITestCase
from superfarmer.farmerapp.models import RegistrationStatus


class BaseTestCase(APITestCase):
    status = "registered"
    status_id = 1

    def setUp(self):
        self.registration_status = RegistrationStatus.objects.create(status="registered", status_id=1)

    def test_registrationstatus_table_must_have_status_and_status_id(self):
        self.assertEqual(self.registration_status.status, self.status)
        self.assertEqual(self.registration_status.status_id, self.status_id)