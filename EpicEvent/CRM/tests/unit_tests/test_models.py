from django.test import TestCase
from CRM.models import Client
from authentication.models import User

import datetime

class ClientTest(TestCase):
    """ Test for Client model """

    def setUp(self):
        self.user_sales1 = User.objects.create(
            pk=20,
            username="supersaler",
            first_name="Yves",
            last_name="Antou",
            role=2,
        )
        self.user_sales2 = User.objects.create(
            pk=21,
            username="pacomik",
            first_name="Pacome",
            last_name="Hercial",
            role=2,
        )
        self.date_now = datetime.datetime.now()
        self.date_update1 = self.date_now + datetime.timedelta(days=100)
        self.date_update2 = self.date_now + datetime.timedelta(days=200)

        self.client1 = Client.objects.create(
            first_name="Michel",
            last_name="Bidon",
            email="pipo@null.com",
            phone="123456789",
            mobile="111111111",
            company_name="PipoBidon",
            date_created=self.date_now,
            date_updated=self.date_update1,
            sales_contact=self.user_sales1,
        )
        self.client2 = Client.objects.create(
            first_name="Marie",
            last_name="Golade",
            email="gag@calembour.com",
            phone="987654321",
            mobile="222222222",
            company_name="MG inc",
            date_created=self.date_now,
            date_updated=self.date_update2,
            sales_contact=self.user_sales2,
        )

    def test_client_firstname(self):
        self.assertEqual(self.client1.first_name, "Michel")
        self.assertEqual(self.client2.first_name, "Marie")

    def test_client_lastname(self):
        self.assertEqual(self.client1.last_name, "Bidon")
        self.assertEqual(self.client2.last_name, "Golade")

    def test_client_email(self):
        self.assertEqual(self.client1.email, "pipo@null.com")
        self.assertEqual(self.client2.email, "gag@calembour.com")

    def test_client_phone(self):
        self.assertEqual(self.client1.phone, "123456789")
        self.assertEqual(self.client2.phone, "987654321")

    def test_client_mobile(self):
        self.assertEqual(self.client1.mobile, "111111111")
        self.assertEqual(self.client2.mobile, "222222222")

    def test_client_company(self):
        self.assertEqual(self.client1.company_name, "PipoBidon")
        self.assertEqual(self.client2.company_name, "MG inc")

    def test_client_date_created(self):
        self.assertEqual(self.client1.date_created, self.date_now)
        self.assertEqual(self.client2.date_created, self.date_now)

    def test_client_date_updated(self):
        self.assertEqual(self.client1.date_updated, self.date_update1)
        self.assertEqual(self.client2.date_updated, self.date_update2)

    def test_client_sales_contact(self):
        self.assertEqual(self.client1.sales_contact.last_name, "Antou")
        self.assertEqual(self.client2.sales_contact.first_name, "Pacome")
