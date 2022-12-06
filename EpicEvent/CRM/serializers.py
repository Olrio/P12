from rest_framework import serializers
from .models import Client
import datetime

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['pk', 'first_name', 'last_name', 'email', 'phone', 'mobile', 'company_name', 'sales_contact', 'date_created', 'date_updated']
        read_only_fields = ['date_created', 'date_updated']

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
