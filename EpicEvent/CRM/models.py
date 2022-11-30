from django.db import models


class Client(models.Model):
    first_name = models.CharField("First Name", max_length=25)
    last_name = models.CharField("Last Name", max_length=25)
    email = models.EmailField("Email", max_length=100)
    phone = models.CharField("Phone", max_length=20)
    mobile = models.CharField("Mobile", max_length=20)

    def __str__(self):
        return self.first_name, self.last_name
