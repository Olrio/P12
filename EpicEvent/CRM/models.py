from django.db import models
from authentication.models import User
import datetime


class Client(models.Model):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20)
    company_name = models.CharField(max_length=250)
    date_created = models.DateTimeField()
    date_updated = models.DateTimeField()
    sales_contact = models.ForeignKey(
        to=User,
        on_delete=models.PROTECT,
        limit_choices_to={'groups__name': "Sales team"}
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Contract(models.Model):
    client = models.ForeignKey(
        to=Client,
        on_delete=models.CASCADE,
    )
    sales_contact = models.ForeignKey(
            to=User,
            on_delete=models.PROTECT,
            limit_choices_to={'groups__name': "Sales team"}
        )
    status = models.BooleanField(default=False)
    amount = models.FloatField()
    payment_due = models.DateTimeField()
    date_created = models.DateTimeField()
    date_updated = models.DateTimeField()

    def __str__(self):
        return f"{self.client} from {self.client.company_name}"


class Event(models.Model):
    name = models.CharField(max_length=250)
    client = models.ForeignKey(
        to=Client,
        on_delete=models.CASCADE,
    )
    support_contact = models.ForeignKey(
        to=User,
        on_delete=models.PROTECT,
    )
    STATUS = [
        ("1", "Incoming"),
        ("2", "In progress"),
        ("3", "Closed"),
    ]
    event_status = models.CharField(
        max_length=1,
        choices=STATUS,)
    attendees = models.IntegerField()
    event_date = models.DateTimeField()
    date_created = models.DateTimeField()
    date_updated = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.client}) "
