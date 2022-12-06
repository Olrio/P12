from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        max_length=20,
        unique=True,
    )
    USERNAME_FIELD = "username"
    ROLES = [
        ("1", "Management"),
        ("2", "Sales"),
        ("3", "Support"),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLES,
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
