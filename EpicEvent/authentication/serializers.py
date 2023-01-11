from rest_framework import serializers
from authentication.models import User
from .validators import Validators


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name"]

    def validate(self, data):
        Validators.check_letters_hyphen(data['first_name'], "first_name")
        Validators.check_letters_hyphen(data['last_name'], "last_name")

        if data['password1'] and data['password2'] and data['password1'] != data['password2']:
            raise serializers.ValidationError("Password error : your two entries differ !")
        return data

    def create(self, validated_data, commit=True):
        user = super().save(commit=False)
        user.set_password(validated_data["password1"])
        user.first_name = user.first_name.title()
        user.last_name = user.last_name.title()

        initials = ''.join([name[0] for name in user.first_name.split("-")])
        # let's set the username from first_name and last_name
        # it's the lower first(s) letter(s) of first_name completed with the lower last_name
        # if this username already exists, a number is added, starting from 2
        counter = 2
        if User.objects.filter(username=initials.lower()+user.last_name.lower()).exists():
            while True:
                if User.objects.filter(username=initials.lower()+user.last_name.lower() + str(counter)).exists():
                    counter +=1
                else:
                    break
            user.username = initials.lower()+user.last_name.lower() + str(counter)
        else:
            user.username = initials.lower()+user.last_name.lower()
        if commit:
            user.save()
        return user
