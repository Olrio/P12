from rest_framework import serializers
from authentication.models import User
from django.contrib.auth.models import Group, Permission

from .validators import Validators


class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField()
    password2 = serializers.CharField()
    team = serializers.CharField()

    class Meta:
        model = User
        fields = ["id", "last_name", "first_name", "password1", "password2", "team"]


    def validate(self, data):
        Validators.check_letters_hyphen(data['first_name'], "first_name")
        Validators.check_letters_hyphen(data['last_name'], "last_name")

        if data['team'] not in ['Management', 'Sales', 'Support']:
            raise serializers.ValidationError({"Team error": "Team must be one of these : Management, Sales or Support"})

        if data['password1'] and data['password2'] and data['password1'] != data['password2']:
            raise serializers.ValidationError("Password error : your two entries differ !")
        return data

    def save(self, **kwargs):
        initials = ''.join([name[0] for name in self.validated_data['first_name'].split("-")])
        # let's set the username from first_name and last_name
        # it's the lower first(s) letter(s) of first_name completed with the lower last_name
        # if this username already exists, a number is added, starting from 2
        counter = 2
        if User.objects.filter(username=initials.lower() + self.validated_data['last_name'].lower()).exists():
            while True:
                if User.objects.filter(username=initials.lower() + self.validated_data['last_name'].lower() + str(counter)).exists():
                    counter += 1
                else:
                    break
            username = initials.lower() + self.validated_data['last_name'].lower() + str(counter)
        else:
            username = initials.lower() + self.validated_data['last_name'].lower()
        user = User(
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            username=username
        )
        user.is_staff = True
        user.set_password(self.validated_data["password1"])
        group = Group.objects.get(name=self.validated_data["team"] + " team")
        user.save()
        user.groups.add(group)
        user.save()
        return user
