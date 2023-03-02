from django.test import Client as Browser
from rest_framework.test import APITestCase
from CRM.models import (
    Client,
    Contract,
    Event
)
from authentication.models import User
from django.contrib.auth.models import Group
import datetime


class Data(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.browser = Browser()

        cls.date_now = datetime.datetime.now()
        cls.date_p20d = cls.date_now + datetime.timedelta(days=20)
        cls.date_p50d = cls.date_now + datetime.timedelta(days=50)
        cls.date_a30d = cls.date_now - datetime.timedelta(days=30)

        cls.management_group = Group.objects.create(name="Management team")
        cls.sales_group = Group.objects.create(name="Sales team")
        cls.support_group = Group.objects.create(name="Support team")

        cls.management_user = User.objects.create(
            username='egeret',
            first_name='Eva',
            last_name='Geret',
            is_staff=True,
            is_superuser=True)
        cls.management_user.set_password("toto1234")
        cls.management_user.groups.add(cls.management_group)
        cls.management_user.save()
        cls.sales_user = User.objects.create(
            username='yantou',
            first_name='Yves',
            last_name='Antou',
            is_staff=False,
            is_superuser=False)
        cls.sales_user.set_password("toto1234")
        cls.sales_user.groups.add(cls.sales_group)
        cls.sales_user.save()
        cls.sales_user2 = User.objects.create(
            username='supersaler',
            first_name='Max',
            last_name='De Tchatche',
            is_staff=False,
            is_superuser=False)
        cls.sales_user2.set_password("toto1234")
        cls.sales_user2.groups.add(cls.sales_group)
        cls.sales_user2.save()

        cls.support_user = User.objects.create(
            username='ecompagne',
            first_name='Ella',
            last_name='Compagne',
            is_staff=False,
            is_superuser=False)
        cls.support_user.set_password("toto1234")
        cls.support_user.groups.add(cls.support_group)
        cls.support_user.save()
        cls.support_user2 = User.objects.create(
            username='bbrother',
            first_name='Big',
            last_name='Brother',
            is_staff=False,
            is_superuser=False)
        cls.support_user2.set_password("toto1234")
        cls.support_user2.groups.add(cls.support_group)
        cls.support_user2.save()
        cls.user_lambda = User.objects.create(
            username='jbody',
            first_name='Jeannot',
            last_name='Body',
            is_staff=False,
            is_superuser=False)
        cls.user_lambda.set_password("toto1234")
        cls.user_lambda.groups.add(cls.support_group)
        cls.user_lambda.save()

        cls.client1 = Client.objects.create(
            first_name="Dark",
            last_name="Vador",
            email="star@wars.com",
            phone="12345678",
            mobile="888888",
            company_name="L'Empire",
            sales_contact=cls.sales_user,
            date_created=cls.date_now,
            date_updated=cls.date_now,
        )
        cls.client2 = Client.objects.create(
            first_name='Luke',
            last_name='Skywalker',
            email='planet@tatooine.com',
            phone='55555',
            mobile='888888',
            company_name="Les rebelles",
            sales_contact=cls.sales_user,
            date_created=cls.date_now,
            date_updated=cls.date_now,
        )

        cls.contract1 = Contract.objects.create(
            client=cls.client1,
            status=True,
            amount=10000,
            payment_due=cls.date_p20d,
            date_created=cls.date_now,
            date_updated=cls.date_now
        )

        cls.contract2 = Contract.objects.create(
            client=cls.client1,
            status=True,
            amount=2000,
            payment_due=cls.date_p50d,
            date_created=cls.date_now,
            date_updated=cls.date_now
        )

        cls.contract3 = Contract.objects.create(
            client=cls.client1,
            status=True,
            amount=25000,
            payment_due=cls.date_p50d,
            date_created=cls.date_now,
            date_updated=cls.date_now
        )

        cls.contract4 = Contract.objects.create(
            client=cls.client1,
            status=False,
            amount=2500,
            payment_due=cls.date_p50d,
            date_created=cls.date_now,
            date_updated=cls.date_now
        )

        cls.event1 = Event.objects.create(
            name="Death Star",
            contract=cls.contract1,
            support_contact=cls.support_user,
            event_status='1',
            attendees=1000,
            event_date=cls.date_p20d,
            date_created=cls.date_now,
            date_updated=cls.date_now,
        )

        cls.event2 = Event.objects.create(
            name="Wooky",
            contract=cls.contract2,
            support_contact=cls.support_user,
            event_status='1',
            attendees=200,
            event_date=cls.date_p50d,
            date_created=cls.date_now,
            date_updated=cls.date_now,
        )
