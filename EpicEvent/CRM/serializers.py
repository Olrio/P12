from rest_framework import serializers
from .models import Client
from authentication.validators import Validators
import datetime

class ClientListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = ['pk', 'first_name', 'last_name', 'email', 'phone', 'mobile', 'company_name', 'sales_contact', 'date_created', 'date_updated']
        read_only_fields = ['date_created', 'date_updated']

    def get_fields(self):
        # field 'sales_contact' only used if user is not a sales team group member
        fields = super().get_fields()
        if self.context['request'].user.groups.filter(name="Sales team").exists() \
                and self.context['request'].method == "POST" \
                and not self.context['request'].user.is_superuser:
            del fields['sales_contact']
        return fields

    def validate(self, data):
        Validators.check_letters_hyphen(data['first_name'], "first_name")
        Validators.check_letters_hyphen(data['last_name'], "last_name")
        Validators.check_is_phone_number(data['phone'], "phone")
        Validators.check_is_phone_number(data['mobile'], "mobile")
        return data

    def create(self, validated_data):
        client = Client.objects.create(
            first_name=validated_data["first_name"].title(),
            last_name=validated_data["last_name"].title(),
            email=validated_data["email"],
            phone=validated_data["phone"],
            mobile=validated_data["mobile"],
            company_name=validated_data["company_name"],
            sales_contact=validated_data["sales_contact"],
            date_created=datetime.datetime.now(),
            date_updated = datetime.datetime.now()
        )
        client.save()
        return client

class ClientDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['pk', 'first_name', 'last_name', 'email', 'phone', 'mobile', 'company_name', 'sales_contact', 'date_created', 'date_updated']
        read_only_fields = ['date_created', 'date_updated']
