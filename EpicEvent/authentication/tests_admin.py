from django.contrib.auth.hashers import make_password
from CRM.models import (
    Client,
    Contract,
    Event
)
from authentication.models import User
from authentication.admin import (
    CustomUserAdmin,
    ClientAdmin
)
from django.contrib import admin
from CRM.tests.unit_tests.data_for_tests import Data

import logging


class TestLogin(Data):
    def test_valid_login(self):
        response = self.browser.login(
            username=self.management_user.username,
            password='toto1234')
        self.assertTrue(response)

    def test_valid_login_check_log(self):
        with self.assertLogs(
                logger=logging.getLogger("login_security"), level='INFO'
        ) as log:
            response = self.browser.post(
                "/admin/login/",
                {
                    'username': self.management_user.username,
                    'password': 'toto1234'
                }
            )
            self.assertTrue(response)
            self.assertIn(
                f"INFO:login_security:user {self.management_user} "
                "connected to admin site",
                log.output
            )

    def test_invalid_login(self):
        response = self.browser.login(
            username='nobody',
            password='badpassword')
        self.assertFalse(response)

    def test_login_error_message_invalid_credentials(self):
        response = self.browser.post(
            "/admin/login/",
            {'username': 'bidon', 'password': 'bidon'}
        )
        error = response.context['form'].errors.as_data()["__all__"][0]
        self.assertEqual(
            error.message,
            "You must provide both valid username "
            "and password of an active user to access this site"
        )

    def test_login_error_message_not_management_user(self):
        response = self.browser.post(
            "/admin/login/",
            {'username': 'yantou', 'password': 'toto1234'})
        error = response.context['form'].errors.as_data()["__all__"][0]
        self.assertEqual(error.message, "Only members of management team "
                                        "are allowed to use this site.")


class TestLogout(Data):
    def test_valid_logout(self):
        self.browser.login(
            username=self.management_user.username,
            password='toto1234')
        response = self.browser.get("/admin/logout/")
        self.assertTemplateUsed(response, 'registration/logged_out.html')
        self.assertEqual(response.status_code, 200)


class TestUsers(Data):
    def test_main_create_user(self):
        user = User.objects._create_user('usertest', 'passwordtest')
        self.assertTrue(isinstance(user, User))

    def test_main_create_user_no_username(self):
        with self.assertRaises(ValueError):
            User.objects._create_user(username=None, password='passwordtest')

    def test_main_create_superuser(self):
        superuser = User.objects.create_superuser('usertest', 'passwordtest')
        self.assertTrue(isinstance(superuser, User))
        self.assertTrue(superuser.is_superuser)

    def test_main_create_superuser_not_staff(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                'usertest', 'passwordtest', is_staff=False
            )

    def test_main_create_superuser_not_superuser(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                'usertest', 'passwordtest', is_superuser=False
            )

    def test_get_users(self):
        self.browser.login(username='egeret', password='toto1234')
        response = self.browser.get("/admin/authentication/user/")
        self.assertEqual(
            response.context['cl'].result_count, User.objects.count())
        results = list(response.context['cl'].result_list)
        user_admin = CustomUserAdmin(User, admin.site)
        user0 = next(user for user in results if user.username == 'egeret')
        user1 = next(user for user in results if user.username == 'yantou')
        self.assertEqual(user0.last_name, "Geret")
        self.assertTrue(user_admin.management(user0))
        self.assertFalse(user_admin.management(user1))
        self.assertEqual(
            user_admin.number_of_clients(user1),
            f'<b><i>'
            f'{Client.objects.filter(sales_contact=user1).count()}'
            f'</i></b>')

    def test_create_user(self):
        users_count = User.objects.count()
        self.browser.login(username='egeret', password='toto1234')
        password_created = make_password('toto1234')
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
        self.browser.login(username='egeret', password='toto1234')
        password_created = make_password('toto1234')
        response = self.browser.post("/admin/authentication/user/add/", data={
            'first_name': 'lucky',
            'last_name': 'luke',
            'password1': password_created,
            'password2': password_created,
        }, follow=True)
        error_first_name = (
            response.context['adminform'].errors.as_data()["groups"][0]
        )
        self.assertEqual(
            error_first_name.message,
            "Please affect this user to a group")

    def test_created_user_can_not_belong_to_several_groups(self):
        self.browser.login(username='egeret', password='toto1234')
        password_created = make_password('toto1234')
        response = self.browser.post("/admin/authentication/user/add/", data={
            'first_name': 'lucky',
            'last_name': 'luke',
            'password1': password_created,
            'password2': password_created,
            'groups': [self.sales_group.id, self.management_group.id]
        }, follow=True)
        error_first_name = (
            response.context['adminform'].errors.as_data()["groups"][0]
        )
        self.assertEqual(
            error_first_name.message,
            "A user can belong to only one group"
        )

    def test_is_not_staff_created_sales_team_user(self):
        self.browser.login(username='egeret', password='toto1234')
        password_created = make_password('toto1234')
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
        self.browser.login(username='egeret', password='toto1234')
        password_created = make_password('toto1234')
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
        self.browser.login(username='egeret', password='toto1234')
        password_created = make_password('toto1234')
        response = self.browser.post("/admin/authentication/user/add/", data={
            'first_name': 'lucky2',
            'last_name': 'luke2',
            'password1': password_created,
            'password2': password_created,
            'groups': self.sales_group.id
        }, follow=True)
        error_first_name = (
            response.context['adminform'].errors.as_data()["first_name"][0]
        )
        self.assertEqual(
            error_first_name.message,
            "<first_name>: Only letters and hyphen are authorized")
        error_last_name = (
            response.context['adminform'].errors.as_data()["last_name"][0]
        )
        self.assertEqual(
            error_last_name.message,
            "<last_name>: Only letters and hyphen are authorized")


class TestClients(Data):
    def test_get_clients(self):
        self.browser.login(username='egeret', password='toto1234')
        response = self.browser.get("/admin/CRM/client/")
        self.assertEqual(
            response.context['cl'].result_count, Client.objects.count())
        results = list(response.context['cl'].result_list)
        client_admin = ClientAdmin(Client, admin.site)
        client1 = next(
            client for client in results if client.last_name == 'Vador')
        client2 = next(
            client for client in results if client.last_name == 'Skywalker')
        self.assertEqual(client2.company_name, "Les rebelles")
        self.assertEqual(client1.mobile, "888888")
        self.assertEqual(client_admin.status(client2), "prospect")
        self.assertEqual(client_admin.status(client1), "existing")

    def test_user_can_add_client(self):
        self.browser.login(username='egeret', password='toto1234')
        response = self.browser.post(
            "/admin/CRM/client/add/",
            {'user': self.management_user}, follow=True)
        self.assertEqual(
            response.context['request'].path, '/admin/CRM/client/add/')

    def test_user_can_not_add_client(self):
        # user is redirected to login page
        self.browser.login(username='ttournesol', password='toto1234')
        response = self.browser.post(
            "/admin/CRM/client/add/", {'user': self.sales_user}, follow=True)
        self.assertEqual(response.context['request'].path, '/admin/login/')

    def test_create_client(self):
        clients_count = Client.objects.count()
        self.browser.login(username='egeret', password='toto1234')
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


class TestContracts(Data):
    def test_get_contracts(self):
        self.browser.login(username='egeret', password='toto1234')
        response = self.browser.get("/admin/CRM/contract/")
        self.assertEqual(
            response.context['cl'].result_count, Contract.objects.count())

    def test_create_contract(self):
        contracts_count = Contract.objects.count()
        self.browser.login(username='egeret', password='toto1234')
        self.browser.post("/admin/CRM/contract/add/", data={
            "client": self.client1.id,
            "amount": 5000,
            "payment_due_0": self.date_p20d.date(),
            "payment_due_1": self.date_p20d.time(),
        }, follow=True)
        self.assertEqual(Contract.objects.count(), contracts_count + 1)
        self.assertEqual(Contract.objects.last().amount, 5000)

    def test_change_contract(self):
        self.browser.login(username='egeret', password='toto1234')
        contract = Contract.objects.get(id=self.contract1.pk)
        self.assertEqual(contract.amount, 10000)
        self.browser.post(
            f"/admin/CRM/contract/"
            f"{self.contract1.id}/change/",
            data={
                "client": self.client1.id,
                "amount": "20000",
                "status": True,
                "payment_due_0": self.date_p20d.date(),
                "payment_due_1": self.date_p20d.time(),
                }, follow=True)
        contract = Contract.objects.get(id=self.contract1.pk)
        self.assertEqual(contract.amount, 20000)

    def test_cancel_signature_of_contract_with_associated_evenement(self):
        self.browser.login(username='egeret', password='toto1234')
        response = self.browser.post(
            f"/admin/CRM/contract/"
            f"{self.contract1.id}/change/",
            data={
                "client": self.client1.id,
                "amount": "20000",
                "status": False,
                "payment_due_0": self.date_p20d.date(),
                "payment_due_1": self.date_p20d.time(),
                }, follow=True)
        error = response.context['adminform'].errors.as_data()['__all__'][0]
        self.assertEqual(error.message,
                         "There's already an event associated"
                         " with this signed contract. "
                         "You can't cancel signature !")


class TestEvents(Data):
    def test_get_events(self):
        self.browser.login(username='egeret', password='toto1234')
        response = self.browser.get("/admin/CRM/event/")
        self.assertEqual(
            response.context['cl'].result_count, Event.objects.count())

    def test_create_event(self):
        events_count = Event.objects.count()
        self.browser.login(username='egeret', password='toto1234')
        self.browser.post("/admin/CRM/event/add/", data={
            "name": "My event",
            "contract": self.contract3.id,
            "support_contact": self.support_user.id,
            "event_status": "1",
            "attendees": "200",
            "event_date_0": self.date_p50d.date(),
            "event_date_1": self.date_p50d.time(),
        }, follow=True)
        self.assertEqual(Event.objects.count(), events_count + 1)
        self.assertEqual(Event.objects.last().attendees, 200)

    def test_update_event(self):
        self.browser.login(username='egeret', password='toto1234')
        response = self.browser.get(
            f"/admin/CRM/event/{self.event1.id}/change/"
        )
        contract_queryset = (
            response.context['adminform'].fields['contract']._queryset
        )
        # self.event2 associated with self.contract2
        # so self.contract2 is not a valid choice for self.event1.contract
        self.assertTrue(self.contract1 in contract_queryset)
        self.assertFalse(self.contract2 in contract_queryset)

    def test_event_date_vs_event_status(self):
        self.browser.login(username='egeret', password='toto1234')
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
        self.assertEqual(
            error.message,
            "Error in field <Event status>: "
            "This event can't be "
            "in progress or closed since its date"
            " is later than the current date"
        )
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
                         "This event can't be incoming since its date "
                         "is earlier than the current date")
