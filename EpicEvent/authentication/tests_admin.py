from django.test import TestCase, Client as browser
from django.contrib.auth.hashers import make_password
from CRM.models import Client, Contract, Event
from authentication.models import User
from authentication.admin import CustomUserAdmin, ClientAdmin, ContractAdmin, EventAdmin
from django.contrib import admin
from django.contrib.auth.models import Group, Permission
import datetime

import ipdb


class MyTests(TestCase):
    def setUp(self):
        self.date_now = datetime.datetime.now()
        self.date_p20d = self.date_now + datetime.timedelta(days=20)
        self.date_p50d = self.date_now + datetime.timedelta(days=50)

        self.browser = browser()

        self.management_group = Group.objects.create(name="Management team")
        self.sales_group = Group.objects.create(name="Sales team")
        self.support_group = Group.objects.create(name="Support team")

        self.management_user = User.objects.create(username='jdalton',
                                              last_name='Dalton',
                                              is_staff=True,
                                              is_superuser=True)
        self.sales_user = User.objects.create(username='ttournesol',
                                         last_name='Tournesol',
                                         is_staff=False,
                                         is_superuser=False)
        self.support_user = User.objects.create(username='bmorane',
                                                first_name='Bob',
                                              last_name='Morane',
                                              is_staff=False,
                                              is_superuser=False)
        self.management_user.set_password('password9999')
        self.management_user.groups.add(self.management_group)
        self.management_user.save()
        self.sales_user.set_password('password9999')
        self.sales_user.groups.add(self.sales_group)
        self.sales_user.save()
        self.support_user.set_password('password9999')
        self.support_user.groups.add(self.support_group)
        self.support_user.save()

        self.client1 = Client.objects.create(
            first_name='Dark',
            last_name='Vador',
            email='star@wars.com',
            phone='123456',
            mobile='654321',
            company_name="L'Empire",
            sales_contact=self.sales_user,
            date_created=self.date_now,
            date_updated=self.date_now,
        )
        self.client2 = Client.objects.create(
            first_name='Luke',
            last_name='Skywalker',
            email='planet@tatooine.com',
            phone='55555',
            mobile='888888',
            company_name="Les rebelles",
            sales_contact=self.sales_user,
            date_created=self.date_now,
            date_updated=self.date_now,
        )

        self.contract1 = Contract.objects.create(
            client=self.client1,
            status = True,
            amount = 10000,
            payment_due = self.date_p20d,
            date_created = self.date_now,
            date_updated = self.date_now
        )

        self.contract2 = Contract.objects.create(
            client=self.client1,
            status=True,
            amount=2000,
            payment_due=self.date_p50d,
            date_created=self.date_now,
            date_updated=self.date_now
        )

        self.contract3 = Contract.objects.create(
            client=self.client1,
            status=True,
            amount=25000,
            payment_due=self.date_p50d,
            date_created=self.date_now,
            date_updated=self.date_now
        )

        self.event1 = Event.objects.create(
            name="Death Star",
            contract = self.contract1,
            support_contact = self.support_user,
            event_status = '1',
            attendees = 1000,
            event_date = self.date_p20d,
            date_created = self.date_now,
            date_updated = self.date_now,
        )

        self.event2 = Event.objects.create(
            name="Wooky",
            contract=self.contract2,
            support_contact=self.support_user,
            event_status='1',
            attendees=200,
            event_date=self.date_p50d,
            date_created=self.date_now,
            date_updated=self.date_now,
        )

class TestLogin(MyTests):
    def test_valid_login(self):
        response = self.browser.login(username='jdalton', password='password9999')
        self.assertTrue(response)

    def test_invalid_login(self):
        response = self.browser.login(username='ttourneso', password='password9999')
        self.assertFalse(response)

    def test_login_error_message_invalid_credentials(self):
        response = self.browser.post("/admin/login/", {'username':'bidon', 'password':'bidon'})
        error = response.context['form'].errors.as_data()["__all__"][0]
        self.assertEqual(error.message, "You must provide both valid username "
                                        "and password of an active user to access this site")

    def test_login_error_message_not_management_user(self):
        response = self.browser.post("/admin/login/", {'username':'ttournesol', 'password':'password9999'})
        error = response.context['form'].errors.as_data()["__all__"][0]
        self.assertEqual(error.message, "Only members of management team "
                                        "are allowed to use this site.")


class TestUsers(MyTests):
    def test_get_users(self):
        self.browser.login(username='jdalton', password='password9999')
        response = self.browser.get("/admin/authentication/user/")
        self.assertEqual(response.context['cl'].result_count, User.objects.count())
        results = list(response.context['cl'].result_list)
        user_admin =CustomUserAdmin(User, admin.site)
        user0 = next(user for user in results if user.username=='jdalton')
        user1 = next(user for user in results if user.username=='ttournesol')
        self.assertEqual(user0.last_name, "Dalton")
        self.assertTrue(user_admin.management(user0))
        self.assertFalse(user_admin.management(user1))
        self.assertEqual(user_admin.number_of_clients(user1), f'<b><i>{Client.objects.filter(sales_contact=user1).count()}</i></b>')


    def test_create_user(self):
        users_count = User.objects.count()
        self.browser.login(username='jdalton', password='password9999')
        password_created = make_password('password9999')
        self.browser.post("/admin/authentication/user/add/", data={
            'first_name': 'lucky',
            'last_name': 'luke',
            'password1': password_created,
            'password2': password_created,
            'groups': self.sales_group.id
        }, follow=True)
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertEqual(User.objects.last().last_name, 'Luke')

    def test_created_user_must_belong_to_a_group(self):
        self.browser.login(username='jdalton', password='password9999')
        password_created = make_password('password9999')
        response = self.browser.post("/admin/authentication/user/add/", data={
            'first_name': 'lucky',
            'last_name': 'luke',
            'password1': password_created,
            'password2': password_created,
        }, follow=True)
        error_first_name = response.context['adminform'].errors.as_data()["groups"][0]
        self.assertEqual(error_first_name.message, "Please affect this user to a group")

    def test_created_user_can_not_belong_to_several_groups(self):
        self.browser.login(username='jdalton', password='password9999')
        password_created = make_password('password9999')
        response = self.browser.post("/admin/authentication/user/add/", data={
            'first_name': 'lucky',
            'last_name': 'luke',
            'password1': password_created,
            'password2': password_created,
            'groups': [self.sales_group.id, self.management_group.id]
        }, follow=True)
        error_first_name = response.context['adminform'].errors.as_data()["groups"][0]
        self.assertEqual(error_first_name.message, "A user can belong to only one group")

    def test_is_not_staff_created_sales_team_user(self):
        self.browser.login(username='jdalton', password='password9999')
        password_created = make_password('password9999')
        self.browser.post("/admin/authentication/user/add/", data={
            'first_name': 'lucky',
            'last_name': 'luke',
            'password1': password_created,
            'password2': password_created,
            'groups': self.sales_group.id
        }, follow=True)
        user = User.objects.get(username='lluke')
        self.assertFalse(user.is_staff)

    def test_is_staff_created_management_team_user(self):
        self.browser.login(username='jdalton', password='password9999')
        password_created = make_password('password9999')
        self.browser.post("/admin/authentication/user/add/", data={
            'first_name': 'lucky',
            'last_name': 'luke',
            'password1': password_created,
            'password2': password_created,
            'groups': self.management_group.id
        }, follow=True)
        user = User.objects.get(username='lluke')
        self.assertTrue(user.is_staff)


    def test_check_created_user_firstname_and_lastname(self):
        self.browser.login(username='jdalton', password='password9999')
        password_created = make_password('password9999')
        response = self.browser.post("/admin/authentication/user/add/", data={
            'first_name': 'lucky2',
            'last_name': 'luke2',
            'password1': password_created,
            'password2': password_created,
            'groups': self.sales_group.id
        }, follow=True)
        error_first_name = response.context['adminform'].errors.as_data()["first_name"][0]
        self.assertEqual(error_first_name.message, "<first_name>: Only letters and hyphen are authorized")
        error_last_name = response.context['adminform'].errors.as_data()["last_name"][0]
        self.assertEqual(error_last_name.message, "<last_name>: Only letters and hyphen are authorized")


class TestClients(MyTests):
    def test_get_clients(self):
        self.browser.login(username='jdalton', password='password9999')
        response = self.browser.get("/admin/CRM/client/")
        self.assertEqual(response.context['cl'].result_count, Client.objects.count())
        results = list(response.context['cl'].result_list)
        client_admin = ClientAdmin(Client, admin.site)
        client1 = next(client for client in results if client.last_name=='Vador')
        client2 = next(client for client in results if client.last_name == 'Skywalker')
        self.assertEqual(client2.company_name, "Les rebelles")
        self.assertEqual(client1.mobile, "654321")
        self.assertEqual(client_admin.status(client2), "prospect")
        self.assertEqual(client_admin.status(client1), "existing")

    def test_user_can_add_client(self):
        self.browser.login(username='jdalton', password='password9999')
        response = self.browser.post("/admin/CRM/client/add/", {'user': self.management_user}, follow=True)
        self.assertEqual(response.context['request'].path, '/admin/CRM/client/add/')


    def test_user_can_not_add_client(self):
        # user is redirected to login page
        self.browser.login(username='ttournesol', password='password9999')
        response = self.browser.post("/admin/CRM/client/add/", {'user': self.sales_user}, follow=True)
        self.assertEqual(response.context['request'].path, '/admin/login/')


    def test_create_client(self):
        clients_count = Client.objects.count()
        self.browser.login(username='jdalton', password='password9999')
        self.browser.post("/admin/CRM/client/add/", data={
            'first_name': 'john',
            'last_name': 'smith',
            'email': 'menin@black.com',
            'phone': '1111111111',
            'mobile': '222222',
            'company_name': 'la septième',
            'sales_contact': self.sales_user.pk,
        })
        self.assertEqual(Client.objects.count(), clients_count + 1)
        self.assertEqual(Client.objects.last().mobile, '222222')

class TestContracts(MyTests):
    def test_get_contracts(self):
        self.browser.login(username='jdalton', password='password9999')
        response = self.browser.get("/admin/CRM/contract/")
        self.assertEqual(response.context['cl'].result_count, Contract.objects.count())

    def test_create_contract(self):
        contracts_count = Contract.objects.count()
        self.browser.login(username='jdalton', password='password9999')
        self.browser.post("/admin/CRM/contract/add/", data={
            "client" : self.client1.id,
            "amount" : 5000,
            "payment_due_0" : self.date_p20d.date(),
            "payment_due_1": self.date_p20d.time(),
        }, follow=True)
        self.assertEqual(Contract.objects.count(), contracts_count + 1)
        self.assertEqual(Contract.objects.last().amount, 5000)

    def test_change_contract(self):
        self.browser.login(username='jdalton', password='password9999')
        contract = Contract.objects.get(id=self.contract1.pk)
        self.assertEqual(contract.amount, 10000)
        self.browser.post(f"/admin/CRM/contract/{self.contract1.id}/change/", data={
            "client": self.client1.id,
            "amount": "20000",
            "status":True,
            "payment_due_0": self.date_p20d.date(),
            "payment_due_1": self.date_p20d.time(),
        }, follow=True)
        contract = Contract.objects.get(id=self.contract1.pk)
        self.assertEqual(contract.amount, 20000)

    def test_cancel_signature_of_contract_with_associated_evenement(self):
        self.browser.login(username='jdalton', password='password9999')
        response = self.browser.post(f"/admin/CRM/contract/{self.contract1.id}/change/", data={
            "client": self.client1.id,
            "amount": "20000",
            "status": False,
            "payment_due_0": self.date_p20d.date(),
            "payment_due_1": self.date_p20d.time(),
        }, follow=True)
        error = response.context['adminform'].errors.as_data()['__all__'][0]
        self.assertEqual(error.message, "There's already an event associated with this signed contract. You can't cancel signature !")


class TestEvents(MyTests):
    def test_get_events(self):
        self.browser.login(username='jdalton', password='password9999')
        response = self.browser.get("/admin/CRM/event/")
        self.assertEqual(response.context['cl'].result_count, Event.objects.count())

    def test_create_event(self):
        events_count = Event.objects.count()
        self.browser.login(username='jdalton', password='password9999')
        self.browser.post("/admin/CRM/event/add/", data={
            "name" : "My event",
            "contract" : self.contract3.id,
            "support_contact" : self.support_user.id,
            "event_status": "1",
            "attendees": "200",
            "event_date_0": self.date_p50d.date(),
            "event_date_1": self.date_p50d.time(),
        }, follow=True)
        self.assertEqual(Event.objects.count(), events_count + 1)
        self.assertEqual(Event.objects.last().attendees, 200)

    def test_event_date_vs_event_status(self):
        self.browser.login(username='jdalton', password='password9999')
        response = self.browser.post("/admin/CRM/event/add/", data={
            "name": "My event",
            "contract": self.contract3.id,
            "support_contact": self.support_user.id,
            "event_status": "2",
            "attendees": "200",
            "event_date_0": self.date_p50d.date(),
            "event_date_1": self.date_p50d.time(),
        }, follow=True)
        error = response.context['adminform'].errors.as_data()["__all__"][0]
        self.assertEqual(error.message,"Error in field <Event status>: This event can't be "
                                       "in progress or closed since its date is later than the current date" )
        response = self.browser.post("/admin/CRM/event/add/", data={
            "name": "My event",
            "contract": self.contract3.id,
            "support_contact": self.support_user.id,
            "event_status": "1",
            "attendees": "200",
            "event_date_0": self.date_now.date(),
            "event_date_1": self.date_now.time(),
        }, follow=True)
        error = response.context['adminform'].errors.as_data()["__all__"][0]
        self.assertEqual(error.message,
                         "Error in field <Event status>: "
                         "This event can't be incoming since its date is earlier than the current date")
