from django.test import TestCase
from CRM.models import Client
from authentication.models import User

import datetime


class DataTest(TestCase):
    def create_dates(self):
        self.date_now = datetime.datetime.now()
        self.date_update100 = self.date_now + datetime.timedelta(days=100)
        self.date_update200 = self.date_now + datetime.timedelta(days=200)

    def create_user(self, pk, username, first_name, last_name, role):
        self.user = User.objects.create(
            pk=pk,
            username=username,
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        return self.user

    def create_client(self, first_name, last_name, email, phone, mobile, company_name,
                      sales_contact, date_created=datetime.datetime.now(),
                      date_updated=datetime.datetime.now()):
        self.client = Client.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            mobile=mobile,
            company_name=company_name,
            date_created=date_created,
            date_updated=date_updated,
            sales_contact=sales_contact,
        )
        return self.client

    def get_users(self):
        self.user_sales1 = self.create_user(21, "supersaler", "Yves", "Antou", 2)
        self.user_sales2 = self.create_user(22, "ellach", "Ella", "Chette", 2)
        self.user_manager1 = self.create_user(11, "pacomik", "Pacome", "Hercial", 1)
        self.user_support1 = self.create_user(31, "technico", "Alex", "Perience", 3)


    def get_clients(self):
        self.client1 = self.create_client("Michel",
                                          "Bidon",
                                          "pipo@null.com",
                                          "123456789",
                                          "111111111",
                                          "PipoBidon",
                                          self.user_sales1,
                                          date_created=self.date_now,
                                          date_updated=self.date_update100
                                          )
        self.client2 = self.create_client("Marie",
                                          "Golade",
                                          "gag@calembour.com",
                                          "987654321",
                                          "222222222",
                                          "MG inc",
                                          self.user_sales2,
                                          date_created=self.date_now,
                                          date_updated=self.date_update200,
                                          )


class UserTest(DataTest):
    """Test for User Model """

    def setUp(self):
        self.get_users()

    def test_user_username(self):
        self.assertEqual(self.user_sales1.username, "supersaler")
        self.assertEqual(self.user_manager1.username, "pacomik")
        self.assertEqual(self.user_support1.username, "technico")

    def test_user_first_name(self):
        self.assertEqual(self.user_sales1.first_name, "Yves")

    def test_user_last_name(self):
        self.assertEqual(self.user_sales2.last_name, "Chette")

    def test_user_role(self):
        self.assertEqual(self.user_manager1.role, 1)
        role_name = next(role[1] for role in self.user_support1.ROLES if role[0]==str(self.user_support1.role))
        self.assertEqual(role_name, 'Support')


class ClientTest(DataTest):
    """ Test for Client model """

    def setUp(self):
        self.create_dates()
        self.get_users()
        self.get_clients()

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
        self.assertEqual(self.client1.date_updated, self.date_update100)
        self.assertEqual(self.client2.date_updated, self.date_update200)

    def test_client_sales_contact(self):
        self.assertEqual(self.client1.sales_contact.last_name, "Antou")
        self.assertEqual(self.client2.sales_contact.first_name, "Ella")
