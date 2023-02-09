from django.test import TestCase
from CRM.models import Client, Contract, Event
from authentication.models import User
from django.contrib.auth.models import Group

import datetime


class DataTest(TestCase):
    def create_dates(self):
        self.date_now = datetime.datetime.now()
        self.date_past = self.date_now - datetime.timedelta(days=30)
        self.date_update_client_100 = self.date_now + datetime.timedelta(days=100)
        self.date_update_client_200 = self.date_now + datetime.timedelta(days=200)
        self.date_update_contract_25 = self.date_now + datetime.timedelta(days=25)
        self.date_update_contract_10 = self.date_now + datetime.timedelta(days=10)
        self.date_due_contract_20 = self.date_now + datetime.timedelta(days=20)
        self.date_due_contract_30 = self.date_now + datetime.timedelta(days=30)
        self.date_event_10 = self.date_now + datetime.timedelta(days=10)
        self.date_event_0 = self.date_now
        self.date_update_event_5 = self.date_now + datetime.timedelta(days=5)

    def create_groups(self, pk, name):
        self.group = Group.objects.create(
            pk=pk,
            name=name
        )
        return self.group


    def create_user(self, pk, username, first_name, last_name, group):
        self.user = User.objects.create(
            pk=pk,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        Group.objects.get(name=group.name).user_set.add(self.user)
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

    def create_contract(self, client, status, amount, payment_due,
                        date_created=datetime.datetime.now(), date_updated=datetime.datetime.now()):
        self.contract = Contract.objects.create(
            client=client,
            status=status,
            amount=amount,
            payment_due=payment_due,
            date_created=date_created,
            date_updated=date_updated
        )
        return self.contract

    def create_event(self, contract, support_contact, event_status, attendees, event_date,
                     date_created=datetime.datetime.now(), date_updated=datetime.datetime.now()):
        self.event = Event.objects.create(
            contract=contract,
            support_contact=support_contact,
            event_status=event_status,
            attendees= attendees,
            event_date=event_date,
            date_created=date_created,
            date_updated=date_updated
        )
        return self.event

    def get_groups(self):
        self.management = self.create_groups(1, "Management")
        self.sales = self.create_groups(2, "Sales")
        self.support = self.create_groups(3, "Support")

    def get_users(self):
        self.user_sales1 = self.create_user(21, "supersaler", "Yves", "Antou", self.sales)
        self.user_sales2 = self.create_user(22, "ellach", "Ella", "Chette", self.sales)
        self.user_manager1 = self.create_user(11, "pacomik", "Pacome", "Hercial", self.management)
        self.user_support1 = self.create_user(31, "technico", "Alex", "Perience", self.support)


    def get_clients(self):
        self.client1 = self.create_client("Michel",
                                          "Bidon",
                                          "pipo@null.com",
                                          "123456789",
                                          "111111111",
                                          "PipoBidon",
                                          self.user_sales1,
                                          date_created=self.date_now,
                                          date_updated=self.date_update_client_100
                                          )
        self.client2 = self.create_client("Marie",
                                          "Golade",
                                          "gag@calembour.com",
                                          "987654321",
                                          "222222222",
                                          "MG inc",
                                          self.user_sales2,
                                          date_created=self.date_now,
                                          date_updated=self.date_update_client_200,
                                          )
        self.client3 = self.create_client("Ray",
                                          "Tro",
                                          "retro@jurassic.com",
                                          "112233445",
                                          "333333333",
                                          "Jurassic Prod",
                                          self.user_sales2,
                                          date_created=self.date_past,
                                          date_updated=self.date_past,

        )

    def get_contracts(self):
        self.contract1 = self.create_contract(self.client1,
                                              False,
                                              10000,
                                              self.date_due_contract_30,
                                              date_created=self.date_now,
                                              date_updated=self.date_update_contract_25,
        )
        self.contract2 = self.create_contract(self.client2,
                                              True,
                                              12345.67,
                                              self.date_due_contract_20,
                                              date_created=self.date_now,
                                              date_updated=self.date_update_contract_10,
                                              )
        self.contract3 = self.create_contract(self.client3,
                                              True,
                                              5432.66,
                                              self.date_past,
                                              date_created=self.date_now,
                                              date_updated=self.date_past,
                                              )

    def get_events(self):
        self.event1 = self.create_event(self.contract1,
                                        self.user_support1,
                                        1,
                                        150,
                                        self.date_event_10,
                                        self.date_now,
                                        self.date_update_event_5,
                                        )
        self.event2 = self.create_event(self.contract2,
                                        self.user_support1,
                                        2,
                                        500,
                                        self.date_event_0,
                                        self.date_now,
                                        self.date_now,
                                        )
        self.event3 = self.create_event(self.contract3,
                                        self.user_support1,
                                        3,
                                        1000,
                                        self.date_past,
                                        self.date_past,
                                        self.date_past,
                                        )


class UserTest(DataTest):
    """Test for User Model """

    def setUp(self):
        self.get_groups()
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
        self.assertTrue(self.user_manager1.groups.filter(name="Management").exists())


class ClientTest(DataTest):
    """ Test for Client model """

    def setUp(self):
        self.create_dates()
        self.get_groups()
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
        self.assertEqual(self.client1.date_updated, self.date_update_client_100)
        self.assertEqual(self.client2.date_updated, self.date_update_client_200)

    def test_client_sales_contact(self):
        self.assertEqual(self.client1.sales_contact.last_name, "Antou")
        self.assertEqual(self.client2.sales_contact.first_name, "Ella")


class ContractTest(DataTest):
    """Test for Contract Model """

    def setUp(self):
        self.create_dates()
        self.get_groups()
        self.get_users()
        self.get_clients()
        self.get_contracts()

    def test_contract_client(self):
        self.assertEqual(self.contract1.client.company_name, "PipoBidon")
        self.assertEqual(self.contract2.client.email, "gag@calembour.com")

    def test_contract_date_created(self):
        self.assertEqual(self.contract1.date_created, self.date_now)
        self.assertEqual(self.contract2.date_created, self.date_now)

    def test_contract_date_updated(self):
        self.assertEqual(self.contract1.date_updated, self.date_update_contract_25)
        self.assertEqual(self.contract2.date_updated, self.date_update_contract_10)

    def test_contract_status(self):
        self.assertEqual(self.contract1.status, False)
        self.assertEqual(self.contract2.status, True)

    def test_contract_amount(self):
        self.assertEqual(self.contract1.amount, 10000)
        self.assertEqual(self.contract2.amount, 12345.67)

    def test_contract_date_due(self):
        self.assertEqual(self.contract1.payment_due, self.date_due_contract_30)
        self.assertEqual(self.contract2.payment_due, self.date_due_contract_20)


class EventTest(DataTest):
    """Test for Event Model """

    def setUp(self):
        self.create_dates()
        self.get_groups()
        self.get_users()
        self.get_clients()
        self.get_contracts()
        self.get_events()

    def test_event_contract(self):
        self.assertEqual(self.event1.contract.client.last_name, "Bidon")
        self.assertEqual(self.event2.contract.amount, 12345.67)
        self.assertEqual(self.event3.contract.status, True)

    def test_event_support_contact(self):
        self.assertEqual(self.event1.support_contact.first_name, "Alex")
        self.assertEqual(self.event2.support_contact.username, "technico")
        self.assertEqual(self.event3.support_contact.last_name, "Perience")

    def test_event_status(self):
        self.assertEqual(self.event1.event_status, 1)
        self.assertEqual(self.event2.event_status, 2)
        status_name = next(status[1] for status in self.event3.STATUS if status[0] == str(self.event3.event_status))
        self.assertEqual(status_name, 'Closed')

    def test_event_attendees(self):
        self.assertEqual(self.event1.attendees, 150)
        self.assertEqual(self.event2.attendees, 500)

    def test_event_date(self):
        self.assertEqual(self.event1.event_date, self.date_event_10)
        self.assertEqual(self.event2.event_date, self.date_event_0)
        self.assertEqual(self.event3.event_date, self.date_past)

    def test_event_date_created(self):
        self.assertEqual(self.event1.date_created, self.date_now)
        self.assertEqual(self.event2.date_created, self.date_now)
        self.assertEqual(self.event3.date_created, self.date_past)

    def test_event_date_updated(self):
        self.assertEqual(self.event1.date_updated, self.date_update_event_5)
        self.assertEqual(self.event2.date_updated, self.date_now)
        self.assertEqual(self.event3.date_updated, self.date_past)
