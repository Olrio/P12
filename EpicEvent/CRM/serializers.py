from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Client, Contract, Event
from authentication.models import User
from authentication.validators import Validators
import datetime

import ipdb


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['pk', 'first_name', 'last_name', 'email', 'phone', 'mobile',
                  'company_name', 'sales_contact', 'date_created', 'date_updated']
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
        if self.context['request'].user.groups.filter(name="Management team").exists():
            sales_contact = validated_data["sales_contact"]
        else:
            sales_contact = self.context['request'].user
        # ipdb.set_trace()
        client = Client.objects.create(
            first_name=validated_data["first_name"].title(),
            last_name=validated_data["last_name"].title(),
            email=validated_data["email"],
            phone=validated_data["phone"],
            mobile=validated_data["mobile"],
            company_name=validated_data["company_name"],
            sales_contact=sales_contact,
            date_created=datetime.datetime.now(),
            date_updated=datetime.datetime.now()
        )
        client.save()
        return client

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.date_updated = datetime.datetime.now()
        instance.save()
        return instance


class ContractSerializer(serializers.ModelSerializer):
    sales_contact = serializers.SerializerMethodField()
    payment_due = serializers.DateTimeField(input_formats=['%Y/%m/%d %H:%M'])
    client = serializers.CharField()

    class Meta:
        model = Contract
        fields = ['pk', 'client', 'amount', 'status', 'payment_due',
                  'sales_contact', 'date_created', 'date_updated']
        read_only_fields = ['date_created', 'date_updated']



    @staticmethod
    def get_sales_contact(obj):
        return obj.client.sales_contact.id


    def validate_client(self, value):
        try:
            int(value)
        except ValueError:
            raise ValidationError("Enter an integer for <client> field")
        client = Client.objects.filter(id=value).first()
        request_user = self.context['request'].user
        if not client:
            raise ValidationError(f"Sorry, client {value} doesn't exist")
        if request_user.groups.filter(name="Sales team").exists() and client.sales_contact != request_user:
            raise ValidationError(f"Sorry, you are not the sales contact of this client")
        return client

    def validate_payment_due(self, value):
        if self.context['request'].method == "POST":
            Validators.is_prior_to_created_date(value, datetime.datetime.now())
        elif self.context['request'].method == "PUT":
            Validators.is_prior_to_created_date(value, self.instance.date_created)
        return value


    def create(self, validated_data):
        if "status" in validated_data:
            status = validated_data["status"]
        else:
            status = False
        contract = Contract.objects.create(
            client=validated_data["client"],
            amount=validated_data["amount"],
            status=status,
            payment_due=validated_data["payment_due"],
            date_created=datetime.datetime.now(),
            date_updated = datetime.datetime.now()
        )
        contract.save()
        return contract

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.date_updated = datetime.datetime.now()
        instance.save()
        return instance


class EventSerializer(serializers.ModelSerializer):
    contract = serializers.CharField()
    support_contact = serializers.CharField(required=False)
    event_status = serializers.CharField()
    event_date = serializers.DateTimeField(input_formats=['%Y/%m/%d %H:%M'])

    class Meta:
        model = Event
        fields = ['pk', 'name', 'contract', 'support_contact', 'event_status',
                  'event_date', 'attendees', 'date_created', 'date_updated']
        read_only_fields = ['date_created', 'date_updated']

    def validate_contract(self, value):
        contract = Contract.objects.filter(id=value).first()
        request_user = self.context['request'].user
        if not contract:
            raise ValidationError(f"Sorry, contract {value} doesn't exist")
        if Contract.objects.filter(id=value, event__isnull=False).exists():
            raise ValidationError("Sorry, there's already an event associated with this contract")
        if request_user.groups.filter(name="Sales team").exists() and contract.client.sales_contact != request_user:
            raise ValidationError(f"Sorry, you are not the sales contact of this client")
        if not contract.status:
            raise ValidationError(f"Sorry, this contract isn't signed yet")
        return contract

    def validate_event_status(self, value):
        if value not in ["Incoming", "In progress", "Closed"]:
            raise ValidationError(f"Error in field <Event status>: Must be <Incoming>, <In progress> or <Closed>")
        if value == "Incoming":
            return 1
        elif value == "In progress":
            return 2
        return 3

    def validate_event_date(self, value):
        if value < datetime.datetime.now():
            raise ValidationError(f"Error in field <Event date>: The date you entered is prior to current date")
        return value

    def validate_support_contact(self, value):
        request_user = self.context['request'].user
        if request_user.groups.filter(name="Sales team").exists():
            raise ValidationError("Only users of management team can change/add support_contact. Please dont't use this field.")
        try:
            support_contact = User.objects.get(id=value)
            if not support_contact.groups.filter(name="Support team").exists():
                raise ValidationError(f"Sorry, user {value} isn't member of support team")
        except User.DoesNotExist:
            raise ValidationError(f"Sorry, user {value} doesn't exist")
        return support_contact

    def validate(self, data):
        if data['event_date'] > datetime.datetime.now() and data['event_status'] in [2, 3] :
            raise ValidationError({"Event status" : "This event can't be in progress"
                                                    " or closed since its date is later than the current date"})
        elif data['event_date'] < datetime.datetime.now() and data['event_status'] == 1:
            raise ValidationError({"Event status" : "This event can't be incoming "
                                                    "since its date is earlier than the current date"})
        return data


    def create(self, validated_data):
        event = Event.objects.create(
            name=validated_data["name"],
            contract=validated_data["contract"],
            event_status=validated_data["event_status"],
            event_date=validated_data["event_date"],
            attendees=validated_data['attendees'],
            date_created=datetime.datetime.now(),
            date_updated = datetime.datetime.now()
        )
        event.save()
        return event

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.date_updated = datetime.datetime.now()
        return instance

