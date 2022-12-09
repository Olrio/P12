from django.db import models
from authentication.models import User


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
    )

    def __str__(self):
        return self.first_name, self.last_name


class Contract(models.Model):
    client = models.ForeignKey(
        to=Client,
        on_delete=models.CASCADE,
    )
    sales_contact = models.ForeignKey(
        to=User,
        on_delete=models.PROTECT,
    )

    status = models.BooleanField()
    amount = models.FloatField()
    payment_due = models.DateTimeField()
    date_created = models.DateTimeField()
    date_updated = models.DateTimeField()


class Event(models.Model):
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
