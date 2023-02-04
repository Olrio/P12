from rest_framework import serializers
from authentication.models import User
from django.contrib.auth.models import Group

from .validators import Validators

import ipdb, logging


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    @staticmethod
    def get_groups(self, obj):
        return obj.groups.values_list('name', flat=True)

    class Meta:
        model = User
        fields = ["id", "last_name", "first_name", "username", "groups"]


class RegisterUserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField()
    password2 = serializers.CharField()
    team = serializers.CharField()

    class Meta:
        model = User
        fields = ["id", "last_name", "first_name", "username", "password1", "password2", "team"]
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
        username = Validators.is_valid_username(self.validated_data['first_name'], self.validated_data['last_name'])
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
    team = serializers.CharField(required=False)
    username = serializers.CharField(
        max_length=20,
        required=False
    )

    class Meta:
        model = User
        fields = ["id", "last_name", "first_name", "username", "password1", "password2", "team"]


    def validate(self, data):
        Validators.check_letters_hyphen(data['first_name'], "first_name")
        data['first_name'] = data['first_name'].title()
        Validators.check_letters_hyphen(data['last_name'], "last_name")
        data['last_name'] = data['last_name'].title()
        try:
            Validators.is_valid_password(data['password1'])
            Validators.two_entries_differ(data['password1'], data['password2'])
        except KeyError as k:
            pass
        try:
            if data['team'] not in ['Management', 'Sales', 'Support']:
                raise serializers.ValidationError({"Team error": "Team must be one of these : Management, Sales or Support"})
        except KeyError:
            raise serializers.ValidationError({"Team error": "A user must be affected to a team : Management, Sales or Support"})
        initials = ''.join([name[0] for name in data['first_name'].split("-")])
        counter = 2
        # check if this username already exists in users, excluding current user
        if User.objects.filter(username=initials.lower() + data['last_name'].lower()).exclude(id=getattr(self, 'instance').pk).exists():
            while True:
                if User.objects.filter(username=initials.lower() + data['last_name'].lower() + str(counter)).exists():
                    counter += 1
                else:
                    break
            data['username'] = initials.lower() + data['last_name'].lower() + str(counter)
        else:
            data['username'] = initials.lower() + data['last_name'].lower()
        return data

    def update(self, instance, validated_data):
        # remove user from all groups then add to the specified group
        instance.groups.clear()
        group = Group.objects.get(name=self.validated_data["team"] + " team")
        if self.validated_data["team"] == "Management":
                instance.is_staff = True
        else:
            instance.is_staff = False
        instance.groups.add(group)
        instance = super().update(instance, validated_data)
        return instance
