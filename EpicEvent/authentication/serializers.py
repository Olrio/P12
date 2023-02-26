from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from authentication.models import User
from django.contrib.auth.models import Group
from .validators import Validators
import logging

login_logger = logging.getLogger("login_security")

class LoginUserSerializer(TokenObtainPairSerializer):
    """
    enable to follow connexions to API
    """
    def validate(self, attrs):
        if User.objects.filter(username=attrs['username']).exists():
            user = User.objects.get(username=attrs['username'])
            login_logger.info("user %s connected to API", user)
        else:
            login_logger.warning("someone with username %s "
                                 "tried to connect to API", attrs['username'])
        data = super().validate(attrs)
        return data


class UserListSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name")

    @staticmethod
    def get_groups(obj):
        return obj.groups.values_list('name', flat=True)

    class Meta:
        model = User
        fields = [
            "id",
            "last_name",
            "first_name",
            "username",
            "groups"
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name")

    @staticmethod
    def get_groups(obj):
        return obj.groups.values_list('name', flat=True)

    class Meta:
        model = User
        fields = [
            "id",
            "last_name",
            "first_name",
            "username",
            "groups",
            "is_staff",
            "is_superuser"
        ]


class RegisterUserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField()
    password2 = serializers.CharField()
    team = serializers.CharField()

    class Meta:
        model = User
        fields = [
            "id",
            "last_name",
            "first_name",
            "username",
            "password1",
            "password2",
            "team"
        ]
        read_only_fields = ["username"]

    @staticmethod
    def validate_first_name(value):
        Validators.check_letters_hyphen(value, "first_name")
        return value

    @staticmethod
    def validate_last_name(value):
        Validators.check_letters_hyphen(value, "last_name")
        return value

    @staticmethod
    def validate_password1(value):
        Validators.is_valid_password(value)
        return value

    @staticmethod
    def validate_team(value):
        Validators.is_valid_team(value)
        return value

    def validate(self, data):
        if data['password1'] and data['password2']:
            Validators.two_entries_differ(data['password1'], data['password2'])
        return data

    def save(self, **kwargs):
        username = Validators.is_valid_username(
            self.validated_data['first_name'],
            self.validated_data['last_name'])
        user = User(
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            username=username
        )
        user.set_password(self.validated_data["password1"])
        group = Group.objects.get(name=self.validated_data["team"] + " team")
        if self.validated_data["team"] == "Management":
            user.is_staff = True
        user.first_name = user.first_name.title()
        user.last_name = user.last_name.title()
        user.save()
        user.groups.add(group)
        user.save()
        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(required=False)
    password2 = serializers.CharField(required=False)
    team = serializers.CharField(required=True)
    username = serializers.CharField(
        max_length=20,
        required=False
    )
    is_staff = serializers.BooleanField(
        allow_null=True,
        default=None,
        required=None
    )
    is_superuser = serializers.BooleanField(
        allow_null=True,
        default=None,
        required=None
    )

    class Meta:
        model = User
        fields = [
            "id",
            "last_name",
            "first_name",
            "username",
            "password1",
            "password2",
            "team",
            "is_superuser",
            "is_staff"
        ]

    def validate(self, data):
        Validators.check_letters_hyphen(data['first_name'], "first_name")
        data['first_name'] = data['first_name'].title()
        Validators.check_letters_hyphen(data['last_name'], "last_name")
        data['last_name'] = data['last_name'].title()
        if "password1" in data:
            Validators.is_valid_password(data['password1'])
            Validators.two_entries_differ(data['password1'], data['password2'])
        if "team" in data:
            Validators.is_valid_team(data['team'])
        # is_superuser and is_staff are optional fields
        # if is_superuser not provided, we keep instance values
        # if is_staff not provided, is_staff is true only for management team
        if data['is_superuser'] is None:
            data['is_superuser'] = self.instance.is_superuser
        if data['is_staff'] is None and data['team'] == 'Management':
            data['is_staff'] = True
        elif data['is_staff'] is None and data['team'] != 'Management':
            data['is_staff'] = False
        return data

    def update(self, instance, validated_data):
        # remove user from all groups then add to the specified group
        instance.groups.clear()
        group = Group.objects.get(name=self.validated_data["team"] + " team")
        instance.groups.add(group)
        instance = super().update(instance, validated_data)
        return instance
