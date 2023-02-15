from rest_framework.test import APITestCase
from django.urls import reverse
from authentication.models import User
from django.contrib.auth.models import Group
from CRM.models import Client, Contract, Event
from .data_for_tests import Data

import datetime
import time

import ipdb



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
        self.assertEqual(resp.json()["detail"], 'No active account found with the given credentials')
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
        self.assertEqual(response.json()['detail'], 'Token is invalid or expired')


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

    def test_get_users_list_unauthorized(self):
        url = "/crm/users/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'], "Sorry, only members of the management team can perform this action")

    def test_get_user_detail(self):
        url = f"/crm/users/{self.support_user.id}/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], self.support_user.first_name)

    def test_get_user_detail_unauthorized(self):
        url = f"/crm/users/{self.support_user.id}/"
        token = self.login(self.sales_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'],
                         "Sorry, only members of the management team can perform this action")

    def test_get_user_detail_non_existent(self):
        url = f"/crm/users/0/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'],
                         "Sorry, user 0 doesn't exist")

    def test_create_a_user(self):
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
        self.assertEqual(response.json()['last_name'][0], "<last_name>: Only letters and hyphen are authorized")
        self.assertEqual(response.json()['first_name'][0], "<first_name>: Only letters and hyphen are authorized")
        self.assertEqual(response.json()['password1'][0], "Password error : your password must contain letters and numbers")

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
                         "Sorry, only members of the management team can perform this action")

    def test_update_a_user(self):
        url = f"/crm/users/{self.support_user.id}/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        self.assertEqual(self.support_user.first_name, "Ella")
        response = self.client.put(url, {
            "first_name": "Hella",
            "last_name": self.support_user.last_name,
            "team": "Support",
            "username":"+grg+"
        })
        self.assertEqual(response.status_code, 200)
        updated_user = User.objects.get(id=self.support_user.id)
        self.assertEqual(updated_user.first_name, "Hella")

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
                         "Sorry, only members of the management team can perform this action")

    def test_update_a_user_non_existent(self):
        url = f"/crm/users/0/"
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
                         "Sorry, only members of the management team can perform this action")

    def test_delete_a_user_non_existent(self):
        url = f"/crm/users/0/"
        token = self.login(self.management_user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'],
                         "Sorry, user 0 doesn't exist")

class ClientTest(DataTest):
    def test_get_client_list_management_user(self):
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

    def test_get_client_detail(self):
        url = f"/crm/clients/{self.client1.id}/"
        token = self.login(self.sales_user)
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

    def test_get_client_detail_unauthorized(self):
        url = f"/crm/clients/{self.client1.id}/"
        token = self.login(self.sales_user2)
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
            "sales_contact": self.sales_user.id,
        })
        self.assertEqual(response.status_code, 200)
        updated_client = Client.objects.get(id=self.client1.id)
        self.assertEqual(updated_client.first_name, "Darth")
        self.assertNotEqual(updated_client.date_created, updated_client.date_updated)

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

    def test_update_a_client_unauthorized(self):
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
