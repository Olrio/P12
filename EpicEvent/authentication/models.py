from django.contrib.auth.models import AbstractBaseUser, \
    PermissionsMixin, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def _create_user(self, username, password,
                     **extra_fields):
        """
        Create and save a user with the given username,
        email, and password.
        """
        if not username:
            raise ValueError(
                'The given username must be set')
        username = self.model.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, password, **extra_fields)


class User(PermissionsMixin, AbstractBaseUser):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    username = models.CharField(
        max_length=20,
        unique=True,
    )
    USERNAME_FIELD = "username"
    is_active = models.BooleanField(
        default=True,
        help_text=(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
