from rest_framework.test import APITestCase
from django.urls import reverse
from authentication.models import User
from django.contrib.auth.models import Group
from CRM.models import Client, Contract, Event


class DataTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.management_group = Group.objects.create(name="Management team")
        cls.sales_group = Group.objects.create(name="Sales team")
        cls.support_group = Group.objects.create(name="Support team")
        cls.management_user = User.objects.create(username='egeret',
                                                  first_name='Eva',
                                                  last_name='Geret',
                                                  is_staff=True,
                                                  is_superuser=True)
        cls.management_user.set_password("toto1234")
        cls.management_user.groups.add(cls.management_group)
        cls.management_user.save()
        cls.sales_user = User.objects.create(username='yantou',
                                                  first_name='Yves',
                                                  last_name='Antou',
                                                  is_staff=False,
                                                  is_superuser=False)
        cls.sales_user.set_password("toto1234")
        cls.sales_user.groups.add(cls.sales_group)
        cls.sales_user.save()
        cls.support_user = User.objects.create(username='ecompagne',
                                             first_name='Ella',
                                             last_name='Compagne',
                                             is_staff=False,
                                             is_superuser=False)
        cls.support_user.set_password("toto1234")
        cls.support_user.groups.add(cls.support_group)
        cls.support_user.save()

    def login(self, user):
        url = reverse("login")
        resp = self.client.post(
            url,
            {
                "username": user.username,
                "password": "toto1234",
            },
            format="json",
        )
        return resp.json()

class LoginTest(DataTest):
    def test_login_succes(self):
        url = reverse("login")
        resp = self.client.post(
            url,
            {
                "username": self.management_user.username,
                "password": "toto1234",
            },
            format="json",
        )
        # verify that given a valid username and
        # password of a user, request returns two tokens
        self.assertTrue(resp.json()["refresh"] is not None)
        self.assertTrue(resp.json()["access"] is not None)
        return resp.json()

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
        url = f"/crm/users/{self.support_user.id}/"
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
