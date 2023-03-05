from django.urls import reverse
from authentication.models import User
from CRM.models import (
    Client,
    Contract,
    Event
)
from .data_for_tests import Data
from authentication.serializers import (
    UserListSerializer,
    UserDetailSerializer,
)


class DataTest(Data):
    def login(self, user):
        url = reverse("login")
        response = self.client.post(
            url,
            {
                "username": user.username,
                "password": "toto1234",
            },
            format="json",
        )
        return response.json()


class LoginTest(DataTest):
    def test_login_succes(self):
        url = reverse("login")
        response = self.client.post(
            url,
            {
                "username": self.management_user.username,
                "password": "toto1234",
            },
            format="json",
        )
        # verify that given a valid username and
        # password of a user, request returns two tokens
        self.assertTrue(response.json()["refresh"] is not None)
        self.assertTrue(response.json()["access"] is not None)
        return response.json()

    def test_login_fail(self):
        url = reverse("login")
        resp = self.client.post(
            url,
            {
                "username": "nobody",
                "password": "badpassword",
            },
            format="json",
        )
        self.assertEqual(
            resp.json()["detail"],
            'No active account found with the given credentials')
        return resp.json()

    def test_token_refresh(self):
        url = "/crm/token/refresh/"
        token = self.login(self.management_user)
        response = self.client.post(
            url,
            {
                "refresh": token['refresh'],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("access" in response.json())

    def test_invalid_token_refresh(self):
        url = "/crm/token/refresh/"
        response = self.client.post(
            url,
            {
                "refresh": "this_is_not_a_token",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json()['detail'],
            'Token is invalid or expired')


class UserTest(DataTest):
    def test_get_users_list(self):
        url = "/crm/users/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), User.objects.count())
        list_usernames = [data['username'] for data in response.data]
        list_last_names = [data['last_name'] for data in response.data]
        self.assertTrue(self.management_user.username in list_usernames)
        self.assertTrue(self.sales_user.last_name in list_last_names)
        self.assertTrue(
            "Sales team" in UserListSerializer().get_groups(
                self.sales_user
            )
        )

    def test_get_users_list_unauthorized(self):
        url = "/crm/users/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()['detail'],
            "Sorry, only members of the management team"
            " can perform this action")

    def test_get_user_detail(self):
        url = f"/crm/users/{self.support_user.id}/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['first_name'],
            self.support_user.first_name)
        self.assertTrue(
            "Support team" in UserDetailSerializer().get_groups(
                self.support_user
            )
        )

    def test_get_user_detail_unauthorized(self):
        url = f"/crm/users/{self.support_user.id}/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'],
                         "Sorry, only members of the management team "
                         "can perform this action")

    def test_get_user_detail_non_existent(self):
        url = "/crm/users/0/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'],
                         "Sorry, user 0 doesn't exist")

    def test_create_a_support_user(self):
        url = "/crm/users/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        users_count = User.objects.count()
        response = self.client.post(url, {
            'last_name': 'bond',
            'first_name': 'james',
            'password1': 'toto1234',
            'password2': 'toto1234',
            'team': 'Support'
        }, format="json")
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.last().is_staff)

    def test_create_a_user_with_duplicatet_first_and_last_names(self):
        url = "/crm/users/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            'last_name': self.sales_user.last_name,
            'first_name': self.sales_user.first_name,
            'password1': 'toto1234',
            'password2': 'toto1234',
            'team': 'Support'
        }, format="json")
        self.assertEqual(response.status_code, 200)
        created_user1 = User.objects.last()
        self.assertNotEqual(created_user1.username,
                            self.sales_user.username)
        response = self.client.post(url, {
            'last_name': self.sales_user.last_name,
            'first_name': self.sales_user.first_name,
            'password1': 'toto1234',
            'password2': 'toto1234',
            'team': 'Support'
        }, format="json")
        self.assertEqual(response.status_code, 200)
        created_user2 = User.objects.last()
        self.assertNotEqual(created_user1.username,
                            created_user2.username)

    def test_create_a_management_user(self):
        url = "/crm/users/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        users_count = User.objects.count()
        response = self.client.post(url, {
            'last_name': 'bond',
            'first_name': 'james',
            'password1': 'toto1234',
            'password2': 'toto1234',
            'team': 'Management'
        }, format="json")
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.last().is_staff)

    def test_create_a_user_bad_data(self):
        url = "/crm/users/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            'last_name': 'bond007',
            'first_name': 'james8',
            'password1': 'toto',
            'password2': '1234',
            'team': 'support'
        }, format="json")
        self.assertEqual(
            response.json()['last_name'][0],
            "<last_name>: Only letters and hyphen are authorized")
        self.assertEqual(
            response.json()['first_name'][0],
            "<first_name>: Only letters and hyphen are authorized")
        self.assertEqual(
            response.json()['password1'][0],
            "Password error : your password must contain letters and numbers")

    def test_create_a_user_unauthorized(self):
        url = "/crm/users/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            'last_name': 'bond',
            'first_name': 'james',
            'password1': 'toto1234',
            'password2': 'toto1234',
            'team': 'Support'
        }, format="json")
        self.assertEqual(response.json()['detail'],
                         "Sorry, only members of the management team"
                         " can perform this action")

    def test_update_a_user(self):
        url = f"/crm/users/{self.support_user.id}/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        self.assertEqual(self.support_user.first_name, "Ella")
        response = self.client.put(url, {
            "first_name": "Hella",
            "last_name": self.support_user.last_name,
            "team": "Support",
            "username": "+grg+",
            "password1": "",
            "password2": "",
        })
        self.assertEqual(response.status_code, 200)
        updated_user = User.objects.get(id=self.support_user.id)
        self.assertEqual(updated_user.first_name, "Hella")

    def test_update_a_user_change_password(self):
        url = f"/crm/users/{self.support_user.id}/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        self.assertEqual(self.support_user.first_name, "Ella")
        response = self.client.put(url, {
            "first_name": "Hella",
            "last_name": self.support_user.last_name,
            "team": "Management",
            "username": "+grg+",
            "password1": "newpassword99",
            "password2": "newpassword99",
        })
        self.assertEqual(response.status_code, 200)
        updated_user = User.objects.get(id=self.support_user.id)
        self.assertEqual(updated_user.first_name, "Hella")
        self.assertTrue(User.objects.get(username="+grg+").is_staff)

    def test_update_a_user_missing_password(self):
        url = f"/crm/users/{self.support_user.id}/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        self.assertEqual(self.support_user.first_name, "Ella")
        response = self.client.put(url, {
            "first_name": "Hella",
            "last_name": self.support_user.last_name,
            "team": "Management",
            "username": "+grg+",
            "password2": "newpassword99",
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['non_field_errors'][0],
                         "Password error : You must supply "
                         "both password1 and password2 !")

    def test_update_a_user_two_passwords_different(self):
        url = f"/crm/users/{self.support_user.id}/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        self.assertEqual(self.support_user.first_name, "Ella")
        response = self.client.put(url, {
            "first_name": "Hella",
            "last_name": self.support_user.last_name,
            "team": "Management",
            "username": "+grg+",
            "password1": "newpassword9",
            "password2": "newpassword99",
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['non_field_errors'][0],
                         "Password error : Your two entries "
                         "for password differ !")

    def test_update_a_user_unauthorized(self):
        url = f"/crm/users/{self.support_user.id}/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.put(url, {
            "first_name": "Hella",
            "last_name": self.support_user.last_name,
            "team": "Support",
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'],
                         "Sorry, only members of the management team "
                         "can perform this action")

    def test_update_a_user_non_existent(self):
        url = "/crm/users/0/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.put(url, {
            "first_name": "Hella",
            "last_name": self.support_user.last_name,
            "team": "Support",
        })
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'],
                         "Sorry, user 0 doesn't exist")

    def test_delete_a_user(self):
        url = f"/crm/users/{self.user_lambda.id}/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        users_count = User.objects.count()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(User.objects.count(), users_count - 1)

    def test_delete_a_user_unauthorized(self):
        url = f"/crm/users/{self.support_user.id}/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'],
                         "Sorry, only members of the management team"
                         " can perform this action")

    def test_delete_a_user_non_existent(self):
        url = "/crm/users/0/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'],
                         "Sorry, user 0 doesn't exist")

    def test_delete_a_user_client_sales_contact(self):
        url = f"/crm/users/{self.sales_user.id}/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 400)
        clients = Client.objects.filter(sales_contact=self.sales_user)
        self.assertEqual(response.json()['Unauthorized delete'],
                         "This user is sales contact "
                         "for the following clients :"
                         f" {[client for client in clients]}. "
                         f"You must change these clients sales contact "
                         f"prior to delete this user.")

    def test_delete_a_user_event_support_contact(self):
        url = f"/crm/users/{self.support_user.id}/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 400)
        events = Event.objects.filter(support_contact=self.support_user)
        self.assertEqual(response.json()['Unauthorized delete'],
                         "This user is support for the following events :"
                         f" {[event for event in events]}. "
                         f"You must change these events support contact "
                         "prior to delete this user.")


class ClientTest(DataTest):
    def test_get_client_list(self):
        url = "/crm/clients/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), Client.objects.count())
        list_last_names = [data['last_name'] for data in response.data]
        list_companies = [data['company_name'] for data in response.data]
        self.assertTrue(self.client1.last_name in list_last_names)
        self.assertTrue(self.client2.company_name in list_companies)

    def test_get_client_list_with_incorrect_filter(self):
        url = "/crm/clients/?xzk=2"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'],
                         "Sorry, looks like you search for inexistent fields. "
                         "Please ensure you correctly entered searched fields."
                         )

    def test_get_client_detail_sales_user(self):
        url = f"/crm/clients/{self.client1.id}/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], self.client1.first_name)

    def test_get_client_detail_support_user(self):
        url = f"/crm/clients/{self.client1.id}/"
        token = self.login(self.support_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], self.client1.first_name)

    def test_get_client_detail_non_existent(self):
        url = "/crm/clients/0/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'],
                         "Sorry, client 0 doesn't exist")

    def test_get_client_detail_unauthorized_sales_user(self):
        url = f"/crm/clients/{self.client1.id}/"
        token = self.login(self.sales_user2)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'],
                         "You do not have permission to perform this action.")

    def test_get_client_detail_unauthorized_support_user(self):
        url = f"/crm/clients/{self.client1.id}/"
        token = self.login(self.support_user2)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'],
                         "You do not have permission to perform this action.")

    def test_create_a_client(self):
        url = "/crm/clients/"
        token = self.login(self.sales_user2)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        clients_count = Client.objects.count()
        response = self.client.post(url, {
            'first_name': 'john',
            'last_name': 'smith',
            'email': 'menin@black.com',
            'phone': '1111111111',
            'mobile': '222222',
            'company_name': 'la septième',
        }, format="json")
        self.assertEqual(Client.objects.count(), clients_count + 1)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Client.objects.last().sales_contact, self.sales_user2)

    def test_create_a_client_invalid_phone(self):
        url = "/crm/clients/"
        token = self.login(self.sales_user2)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            'first_name': 'john',
            'last_name': 'smith',
            'email': 'menin@black.com',
            'phone': '11111bad',
            'mobile': '222222',
            'company_name': 'la septième',
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['non_field_errors'][0],
                         "<phone>: A phone number can contain only numbers !")

    def test_create_a_client_management_user_not_providing_contact_user(self):
        url = "/crm/clients/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            'first_name': 'john',
            'last_name': 'smith',
            'email': 'menin@black.com',
            'phone': '1111111111',
            'mobile': '222222',
            'company_name': 'la septième',
        }, format="json")
        self.assertEqual(response.json()['sales_contact error'],
                         "Please fill 'contact' field")

    def test_create_a_client_providing_inexistent_contact_user(self):
        url = "/crm/clients/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            'first_name': 'john',
            'last_name': 'smith',
            'contact': 0,
            'email': 'menin@black.com',
            'phone': '1111111111',
            'mobile': '222222',
            'company_name': 'la septième',
        }, format="json")
        self.assertEqual(response.json()['sales_contact error'],
                         "This user doesn't exist.")

    def test_create_a_client_providing_contact_user_not_sales_member(self):
        url = "/crm/clients/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            'first_name': 'john',
            'last_name': 'smith',
            'contact': self.support_user2.id,
            'email': 'menin@black.com',
            'phone': '1111111111',
            'mobile': '222222',
            'company_name': 'la septième',
        }, format="json")
        self.assertEqual(response.json()['sales_contact error'],
                         "Please choose a user belonging to Sales team")

    def test_create_a_client_unauthorized(self):
        url = "/crm/clients/"
        token = self.login(self.support_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            'first_name': 'john',
            'last_name': 'smith',
            'email': 'menin@black.com',
            'phone': '1111111111',
            'mobile': '222222',
            'company_name': 'la septième',
        }, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'],
                         "You do not have permission to perform this action.")

    def test_update_a_client(self):
        url = f"/crm/clients/{self.client1.id}/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        self.assertEqual(self.client1.first_name, "Dark")
        response = self.client.put(url, {
            "first_name": "Darth",
            "last_name": "Vador",
            "email": "star@wars.com",
            "phone": "12345678",
            "mobile": "888888",
            "company_name": "L'Empire",
        })
        self.assertEqual(response.status_code, 200)
        updated_client = Client.objects.get(id=self.client1.id)
        self.assertEqual(updated_client.first_name, "Darth")
        self.assertNotEqual(
            updated_client.date_created,
            updated_client.date_updated)

    def test_update_a_client_management_user(self):
        url = f"/crm/clients/{self.client1.id}/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        self.assertEqual(self.client1.sales_contact, self.sales_user)
        response = self.client.put(url, {
            "first_name": "Darth",
            "last_name": "Vador",
            "email": "star@wars.com",
            "phone": "12345678",
            "mobile": "888888",
            "company_name": "L'Empire",
            "contact": self.sales_user2.id
        })
        self.assertEqual(response.status_code, 200)
        updated_client = Client.objects.get(id=self.client1.id)
        self.assertEqual(updated_client.sales_contact, self.sales_user2)

    def test_update_a_client_providing_inexistent_contact_user(self):
        url = f"/crm/clients/{self.client1.id}/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.put(url, {
            "first_name": "Darth",
            "last_name": "Vador",
            "email": "star@wars.com",
            "phone": "12345678",
            "mobile": "888888",
            "company_name": "L'Empire",
            "contact": 0,
        })
        self.assertEqual(response.json()['sales_contact error'],
                         "This user doesn't exist.")

    def test_update_a_client_with_user_contact_being_not_sales_member(self):
        url = f"/crm/clients/{self.client1.id}/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.put(url, {
            "first_name": "Darth",
            "last_name": "Vador",
            "email": "star@wars.com",
            "phone": "12345678",
            "mobile": "888888",
            "company_name": "L'Empire",
            "contact": self.support_user.id,
        })
        self.assertEqual(response.json()['sales_contact error'],
                         "Please choose a user belonging to Sales team")

    def test_update_a_client_non_existent(self):
        url = "/crm/clients/0/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.put(url, {
            "first_name": "Darth",
            "last_name": "Vador",
            "email": "star@wars.com",
            "phone": "12345678",
            "mobile": "888888",
            "company_name": "L'Empire",
            "sales_contact": self.sales_user.id,
        })
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'],
                         "Sorry, client 0 doesn't exist")

    def test_update_a_client_unauthorized_support_user(self):
        url = f"/crm/clients/{self.client1.id}/"
        token = self.login(self.support_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.put(url, {
            "first_name": "Darth",
            "last_name": "Vador",
            "email": "star@wars.com",
            "phone": "12345678",
            "mobile": "888888",
            "company_name": "L'Empire",
            "sales_contact": self.sales_user.id,
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'],
                         "You do not have permission to perform this action.")

    def test_update_a_client_unauthorized_sales_user(self):
        url = f"/crm/clients/{self.client1.id}/"
        token = self.login(self.sales_user2)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.put(url, {
            "first_name": "Darth",
            "last_name": "Vador",
            "email": "star@wars.com",
            "phone": "12345678",
            "mobile": "888888",
            "company_name": "L'Empire",
            "sales_contact": self.sales_user.id,
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'],
                         "You do not have permission to perform this action.")

    def test_delete_a_client(self):
        url = f"/crm/clients/{self.client2.id}/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        clients_count = Client.objects.count()
        response = self.client.delete(url, format="json")
        self.assertEqual(Client.objects.count(), clients_count - 1)
        self.assertEqual(response.status_code, 204)

    def test_delete_a_client_non_existent(self):
        url = "/crm/clients/0/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'],
                         "Sorry, client 0 doesn't exist")

    def test_delete_a_client_unauthorized(self):
        url = f"/crm/clients/{self.client1.id}/"
        token = self.login(self.sales_user2)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'],
                         "You do not have permission to perform this action.")


class ContractTest(DataTest):
    def test_get_contract_list(self):
        url = "/crm/contracts/"
        token = self.login(self.support_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), Contract.objects.count())

    def test_get_contract_list_with_incorrect_filter(self):
        url = "/crm/contracts/?xzk=2"
        token = self.login(self.support_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'],
                         "Sorry, looks like you search for inexistent fields. "
                         "Please ensure you correctly entered searched fields."
                         )

    def test_get_contract_detail(self):
        url = f"/crm/contracts/{self.contract1.id}/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['amount'], self.contract1.amount)
        self.assertEqual(
            response.data['payment_due'],
            self.contract1.payment_due.strftime("%Y/%m/%d %H:%M"))

    def test_get_contract_detail_non_existent(self):
        url = "/crm/contracts/0/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'],
                         "Sorry, contract 0 doesn't exist")

    def test_get_contract_detail_unauthorized_sales_user(self):
        url = f"/crm/contracts/{self.contract1.id}/"
        token = self.login(self.sales_user2)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'],
                         "You do not have permission to perform this action.")

    def test_get_contract_detail_unauthorized_support_user(self):
        url = f"/crm/contracts/{self.contract1.id}/"
        token = self.login(self.support_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'],
                         "You do not have permission to perform this action.")

    def test_create_a_contract(self):
        url = "/crm/contracts/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        contracts_count = Contract.objects.count()
        response = self.client.post(url, {
            'id_client': self.client2.id,
            'payment_due': self.date_p50d.strftime("%Y/%m/%d %H:%M"),
            'amount': 2500,
        }, format="json")
        self.assertEqual(Contract.objects.count(), contracts_count + 1)
        self.assertEqual(response.status_code, 201)
        contract = Contract.objects.last()
        self.assertEqual(contract.client.sales_contact, self.sales_user)
        self.assertEqual(contract.status, False)

    def test_create_a_contract_status_provided(self):
        url = "/crm/contracts/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            'id_client': self.client2.id,
            'payment_due': self.date_p50d.strftime("%Y/%m/%d %H:%M"),
            'amount': 2500,
            'status': True
        }, format="json")
        self.assertEqual(response.status_code, 201)
        contract = Contract.objects.last()
        self.assertEqual(contract.status, True)

    def test_create_a_contract_unauthorized(self):
        url = "/crm/contracts/"
        token = self.login(self.support_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            'id_client': self.client2.id,
            'payment_due': self.date_p50d.strftime("%Y/%m/%d %H:%M"),
            'amount': 2500,
        }, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'],
                         "You do not have permission to perform this action.")

    def test_create_a_contract_sales_user_not_client_sales_contact(self):
        url = "/crm/contracts/"
        token = self.login(self.sales_user2)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            'id_client': self.client1.id,
            'payment_due': self.date_p50d.strftime("%Y/%m/%d %H:%M"),
            'amount': 2500,
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['id_client'][0],
                         "Sorry, you are not the sales contact of this client")

    def test_create_a_contract_client_non_existent(self):
        url = "/crm/contracts/"
        token = self.login(self.sales_user2)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            'id_client': 0,
            'payment_due': self.date_p50d.strftime("%Y/%m/%d %H:%M"),
            'amount': 2500,
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['id_client'][0],
                         "Sorry, client 0 doesn't exist")

    def test_create_a_contract_id_client_non_provided(self):
        url = "/crm/contracts/"
        token = self.login(self.sales_user2)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            'payment_due': self.date_p50d.strftime("%Y/%m/%d %H:%M"),
            'amount': 2500,
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['id_client'][0],
                         "Please enter id of client")

    def test_create_a_contract_payment_due_prior_to_current_date(self):
        url = "/crm/contracts/"
        token = self.login(self.sales_user2)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            'payment_due': self.date_a30d.strftime("%Y/%m/%d %H:%M"),
            'amount': 2500,
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['payment_due'][0],
                         "Payment due date can't be prior to creation date")

    def test_update_a_contract(self):
        url = f"/crm/contracts/{self.contract1.id}/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        self.assertEqual(self.contract1.amount, 10000)
        response = self.client.put(url, {
            "id_client": self.client1.id,
            "payment_due": self.date_p20d.strftime("%Y/%m/%d %H:%M"),
            "amount": 15000,
        })
        self.assertEqual(response.status_code, 200)
        updated_contract = Contract.objects.get(id=self.contract1.id)
        self.assertEqual(updated_contract.amount, 15000)
        self.assertNotEqual(
            updated_contract.date_created,
            updated_contract.date_updated)

    def test_update_a_contract_client_non_existent(self):
        url = f"/crm/contracts/{self.contract1.id}/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.put(url, {
            "id_client": 0,
            "payment_due": self.date_p20d.strftime("%Y/%m/%d %H:%M"),
            "amount": 15000,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['id_client'][0],
                         "Sorry, client 0 doesn't exist")

    def test_update_a_contract_unauthorized_sales_user(self):
        url = f"/crm/contracts/{self.contract1.id}/"
        token = self.login(self.sales_user2)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.put(url, {
            "id_client": 0,
            "payment_due": self.date_p20d.strftime("%Y/%m/%d %H:%M"),
            "amount": 15000,
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'],
                         "You do not have permission to perform this action.")

    def test_update_a_contract_unauthorized_support_user(self):
        url = f"/crm/contracts/{self.contract1.id}/"
        token = self.login(self.support_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.put(url, {
            "id_client": 0,
            "payment_due": self.date_p20d.strftime("%Y/%m/%d %H:%M"),
            "amount": 15000,
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'],
                         "You do not have permission to perform this action.")

    def test_delete_a_contract(self):
        url = f"/crm/contracts/{self.contract2.id}/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        contracts_count = Contract.objects.count()
        response = self.client.delete(url, format="json")
        self.assertEqual(Contract.objects.count(), contracts_count - 1)
        self.assertEqual(response.status_code, 204)

    def test_delete_a_contract_non_existent(self):
        url = "/crm/contracts/0/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'],
                         "Sorry, contract 0 doesn't exist")

    def test_delete_a_contract_unauthorized(self):
        url = f"/crm/contracts/{self.contract2.id}/"
        token = self.login(self.sales_user2)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'],
                         "You do not have permission to perform this action.")


class EventTest(DataTest):
    def test_get_event_list(self):
        url = "/crm/events/"
        token = self.login(self.support_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), Event.objects.count())

    def test_get_event_list_with_incorrect_filter(self):
        url = "/crm/events/?xzk=2"
        token = self.login(self.support_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'],
                         "Sorry, looks like you search for inexistent fields. "
                         "Please ensure you correctly entered searched fields."
                         )

    def test_get_event_detail(self):
        url = f"/crm/events/{self.event1.id}/"
        token = self.login(self.support_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], self.event1.name)
        self.assertEqual(response.data['attendees'], self.event1.attendees)

    def test_get_event_detail_unauthorized_sales_user(self):
        url = f"/crm/events/{self.event1.id}/"
        token = self.login(self.sales_user2)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'],
                         "You do not have permission to perform this action.")

    def test_get_event_detail_unauthorized_support_user(self):
        url = f"/crm/events/{self.event1.id}/"
        token = self.login(self.support_user2)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'],
                         "You do not have permission to perform this action.")

    def test_get_event_detail_non_existent(self):
        url = "/crm/events/0/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'],
                         "Sorry, event 0 doesn't exist")

    def test_create_an_event(self):
        url = "/crm/events/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        events_count = Event.objects.count()
        response = self.client.post(url, {
            "name": "Event zero",
            "contract": self.contract3.id,
            "event_status": 'Incoming',
            "attendees": 50,
            "notes": "Beware of dogs !",
            "event_date": self.date_p20d.strftime("%Y/%m/%d %H:%M"),
        }, format="json")
        self.assertEqual(Event.objects.count(), events_count + 1)
        self.assertEqual(response.status_code, 201)
        event = Event.objects.last()
        self.assertEqual(event.contract.client.sales_contact, self.sales_user)
        self.assertEqual(event.notes, "Beware of dogs !")

    def test_create_an_event_unauthorized_support_user(self):
        url = "/crm/events/"
        token = self.login(self.support_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            "name": "Event zero",
            "contract": self.contract3.id,
            "event_status": 'Incoming',
            "attendees": 50,
            "event_date": self.date_p20d.strftime("%Y/%m/%d %H:%M"),
        }, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'],
                         "You do not have permission to perform this action.")

    def test_create_an_event_user_is_not_sales_contact(self):
        url = "/crm/events/"
        token = self.login(self.sales_user2)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            "name": "Event zero",
            "contract": self.contract3.id,
            "event_status": 'Incoming',
            "attendees": 50,
            "event_date": self.date_p20d.strftime("%Y/%m/%d %H:%M"),
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['contract'][0],
                         "Sorry, you are not the sales contact of this client")

    def test_create_an_event_contract_non_existent(self):
        url = "/crm/events/"
        token = self.login(self.sales_user2)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            "name": "Event zero",
            "contract": 0,
            "event_status": 'Incoming',
            "attendees": 50,
            "event_date": self.date_p20d.strftime("%Y/%m/%d %H:%M"),
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['contract'][0],
                         "Sorry, contract 0 doesn't exist")

    def test_create_an_event_existent_event_with_same_contract(self):
        url = "/crm/events/"
        token = self.login(self.sales_user2)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            "name": "Event zero",
            "contract": self.contract1.id,
            "event_status": 'Incoming',
            "attendees": 50,
            "event_date": self.date_p20d.strftime("%Y/%m/%d %H:%M"),
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['contract'][0],
                         "Sorry, there's already an event "
                         "associated with this contract")

    def test_create_an_event_for_non_signed_contract(self):
        url = "/crm/events/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            "name": "Event zero",
            "contract": self.contract4.id,
            "event_status": 'Incoming',
            "attendees": 50,
            "event_date": self.date_p20d.strftime("%Y/%m/%d %H:%M"),
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['contract'][0],
                         "Sorry, this contract isn't signed yet")

    def test_create_an_event_error_on_event_status(self):
        url = "/crm/events/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            "name": "Event zero",
            "contract": self.contract3.id,
            "event_status": 'Incomin',
            "attendees": 50,
            "event_date": self.date_p20d.strftime("%Y/%m/%d %H:%M"),
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['event_status'][0],
                         "Error in field <Event status>: "
                         "Must be <Incoming>, <In progress> or <Closed>")

    def test_create_an_event_with_event_status_in_progress(self):
        url = "/crm/events/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            "name": "Event zero",
            "contract": self.contract3.id,
            "support_contact": self.support_user.id,
            "event_status": 'In progress',
            "attendees": 50,
            "event_date": self.date_now.strftime("%Y/%m/%d %H:%M"),
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            Event.objects.last().support_contact,
            self.support_user
        )

    def test_create_an_event_with_event_status_closed(self):
        url = "/crm/events/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            "name": "Event zero",
            "contract": self.contract3.id,
            "event_status": 'Closed',
            "attendees": 50,
            "event_date": self.date_now.strftime("%Y/%m/%d %H:%M"),
        }, format="json")
        self.assertEqual(response.status_code, 201)

    def test_create_an_event_sales_user_cant_set_support_contact(self):
        url = "/crm/events/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            "name": "Event zero",
            "contract": self.contract3.id,
            'support_contact': self.support_user.id,
            "event_status": 'Closed',
            "attendees": 50,
            "event_date": self.date_now.strftime("%Y/%m/%d %H:%M"),
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['support_contact'][0],
                         "Only users of management team "
                         "can change/add support_contact. "
                         "Please dont't use this field.")

    def test_create_an_event_support_contact_not_support_member(self):
        url = "/crm/events/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            "name": "Event zero",
            "contract": self.contract3.id,
            'support_contact': self.sales_user2.id,
            "event_status": 'Closed',
            "attendees": 50,
            "event_date": self.date_now.strftime("%Y/%m/%d %H:%M"),
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['support_contact'][0],
                         f"Sorry, user {self.sales_user2.id} "
                         f"isn't member of support team")

    def test_create_an_event_non_existent_support_contact(self):
        url = "/crm/events/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            "name": "Event zero",
            "contract": self.contract3.id,
            'support_contact': 0,
            "event_status": 'Closed',
            "attendees": 50,
            "event_date": self.date_now.strftime("%Y/%m/%d %H:%M"),
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['support_contact'][0],
                         "Sorry, user 0 doesn't exist")

    def test_create_an_event_in_progress_but_event_date_is_incoming(self):
        url = "/crm/events/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            "name": "Event zero",
            "contract": self.contract3.id,
            "event_status": 'In progress',
            "attendees": 50,
            "event_date": self.date_p20d.strftime("%Y/%m/%d %H:%M"),
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['event_status'][0],
                         "This event can't be in progress or closed since "
                         "its date is later than the current date")

    def test_create_an_event_incoming_but_event_date_is_passed(self):
        url = "/crm/events/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.post(url, {
            "name": "Event zero",
            "contract": self.contract3.id,
            "event_status": 'Incoming',
            "attendees": 50,
            "event_date": self.date_a30d.strftime("%Y/%m/%d %H:%M"),
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['event_status'][0],
                         "This event can't be incoming since "
                         "its date is earlier than the current date")

    def test_update_an_event(self):
        url = f"/crm/events/{self.event1.id}/"
        token = self.login(self.support_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        self.assertEqual(self.event1.attendees, 1000)
        response = self.client.put(url, {
            "name": "Death Star",
            "contract": self.contract1.id,
            "support_contact": self.support_user.id,
            "event_status": 'Incoming',
            "attendees": 2000,
            "event_date": self.date_p20d.strftime("%Y/%m/%d %H:%M"),
        })
        self.assertEqual(response.status_code, 200)
        updated_event = Event.objects.get(id=self.event1.id)
        self.assertEqual(updated_event.attendees, 2000)
        self.assertNotEqual(
            updated_event.date_created,
            updated_event.date_updated)

    def test_update_an_event_unauthorized_sales_user(self):
        url = f"/crm/events/{self.event1.id}/"
        token = self.login(self.sales_user2)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.put(url, {
            "name": "Death Star",
            "contract": self.contract1.id,
            "event_status": 'Incoming',
            "attendees": 2000,
            "event_date": self.date_p20d.strftime("%Y/%m/%d %H:%M"),
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'],
                         "You do not have permission to perform this action.")

    def test_update_an_event_unauthorized_support_user(self):
        url = f"/crm/events/{self.event1.id}/"
        token = self.login(self.support_user2)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.put(url, {
            "name": "Death Star",
            "contract": self.contract1.id,
            "event_status": 'Incoming',
            "attendees": 2000,
            "event_date": self.date_p20d.strftime("%Y/%m/%d %H:%M"),
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'],
                         "You do not have permission to perform this action.")

    def test_update_an_event_non_existent(self):
        url = "/crm/events/0/"
        token = self.login(self.support_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.put(url, {
            "name": "Death Star",
            "contract": self.contract1.id,
            "event_status": 'Incoming',
            "attendees": 2000,
            "event_date": self.date_p20d.strftime("%Y/%m/%d %H:%M"),
        })
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'],
                         "Sorry, event 0 doesn't exist")

    def test_update_an_event_existent_event_with_same_contract(self):
        url = f"/crm/events/{self.event2.id}/"
        token = self.login(self.support_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.put(url, {
            "name": "Wooky",
            "contract": self.contract1.id,
            "event_status": 'Incoming',
            "attendees": 200,
            "event_date": self.date_p20d.strftime("%Y/%m/%d %H:%M"),
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['contract'][0],
                         "Sorry, there's already an event "
                         "associated with this contract")

    def test_delete_an_event(self):
        url = f"/crm/events/{self.event2.id}/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        events_count = Event.objects.count()
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Event.objects.count(), events_count - 1)

    def test_delete_an_event_non_existent(self):
        url = "/crm/events/0/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'],
                         "Sorry, event 0 doesn't exist")

    def test_delete_an_event_unauthorized(self):
        url = f"/crm/events/{self.event2.id}/"
        token = self.login(self.support_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'],
                         "You do not have permission to perform this action.")
