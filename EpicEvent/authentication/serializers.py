from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from authentication.models import User
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["pk", "first_name", "last_name", "email", "role", "password", "password2", "username"]
        read_only_fields = ["username"]

    email = serializers.EmailField(
            validators=[
                UniqueValidator(
                    queryset=User.objects.all(),
                    message="This email address is already registered. "
                    "Please use another one",
                )
            ]
        )
    password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
    )

    @staticmethod
    def check_letters_hyphen(data, field):
        for char in data:
            if not char.isalpha() and char != "-":
                raise serializers.ValidationError({f"error in field <{field}>":
                    "Only letters and hyphen are authorized"}
                )


    def validate(self, data):
        # check last_name and first_name : must have only letters or hyphen
        self.check_letters_hyphen(data['first_name'], 'first name')
        self.check_letters_hyphen(data['last_name'], 'last name')

        if data["email"] != data["email"].lower():
            raise serializers.ValidationError(
                {
                    "Email case error":
                        "Only lowercase characters are allowed in mail address"
                }
            )
        if data["password"] != data["password2"]:
            raise serializers.ValidationError(
                {"password": "your two entries differ !"}
            )
        return data

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data["email"],
            first_name=validated_data["first_name"].title(),
            last_name=validated_data["last_name"].title(),
            role=validated_data["role"],
        )
        user.set_password(validated_data["password"])
        user.username = user.first_name[0] + user.last_name + str(user.pk)
        user.save()
        return user
