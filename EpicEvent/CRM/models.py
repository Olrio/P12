from django.db import models
from authentication.models import User


class Client(models.Model):
    first_name = models.CharField("Client First Name",
                                  max_length=25,
                                  )
    last_name = models.CharField("Client Last Name", max_length=25)
    email = models.EmailField("Email", max_length=100)
    phone = models.CharField("Phone", max_length=20)
    mobile = models.CharField("Mobile", max_length=20)
    company_name = models.CharField("Company", max_length=250)
    date_created = models.DateTimeField("Client Date Created")
    date_updated = models.DateTimeField("Client Date Updated")
    sales_contact = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.first_name, self.last_name
