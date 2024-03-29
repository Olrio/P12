from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import (
    Client,
    Contract,
    Event
)
from authentication.models import User
from authentication.serializers import UserListSerializer
from authentication.validators import Validators
import datetime


class ClientListSerializer(serializers.ModelSerializer):
    sales_contact = serializers.SerializerMethodField()

    @staticmethod
    def get_sales_contact(instance):
        queryset = User.objects.filter(id=instance.sales_contact.id)
        serializer = UserListSerializer(queryset, many=True)
        # we only need sales_contact id, first_name and last_name
        for saler in serializer.data:
            del (saler['username'])
            del (saler['groups'])
        return serializer.data

    class Meta:
        model = Client
        fields = [
            'pk',
            'first_name',
            'last_name',
            'email',
            'company_name',
            'sales_contact',
        ]


class ClientDetailSerializer(serializers.ModelSerializer):
    sales_contact = serializers.SerializerMethodField()
    contact = serializers.IntegerField(required=False)

    @staticmethod
    def get_sales_contact(instance):
        queryset = User.objects.filter(id=instance.sales_contact.id)
        serializer = UserListSerializer(queryset, many=True)
        # we only need sales_contact id, first_name and last_name
        for saler in serializer.data:
            del (saler['username'])
            del (saler['groups'])
        return serializer.data

    class Meta:
        model = Client
        fields = [
            'pk',
            'first_name',
            'last_name',
            'email',
            'phone',
            'mobile',
            'company_name',
            'contact',
            'sales_contact',
            'date_created',
            'date_updated'
        ]
        read_only_fields = ['date_created', 'date_updated']

    def validate(self, data):
        Validators.check_letters_hyphen(data['first_name'], "first_name")
        Validators.check_letters_hyphen(data['last_name'], "last_name")
        Validators.check_is_phone_number(data['phone'], "phone")
        Validators.check_is_phone_number(data['mobile'], "mobile")
        return data

    def create(self, validated_data):
        if self.context['request'].user.groups.filter(
                name="Management team").exists():
            if "contact" not in validated_data:
                raise serializers.ValidationError(
                    {
                        "sales_contact error": "Please fill 'contact' field"
                    }
                )
            try:
                sales_contact = User.objects.get(id=validated_data["contact"])
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        "sales_contact error": "This user doesn't exist."
                    }
                )
            if not sales_contact.groups.filter(name="Sales team").exists():
                raise serializers.ValidationError(
                    {
                        "sales_contact error":
                            "Please choose a user belonging to Sales team"
                    }
                )
        else:
            sales_contact = self.context['request'].user
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
        if self.context['request'].user.groups.filter(
                name="Management team").exists():
            if "contact" in validated_data:
                try:
                    sales_contact = User.objects.get(
                        id=validated_data["contact"]
                    )
                except User.DoesNotExist:
                    raise serializers.ValidationError(
                        {
                            "sales_contact error": "This user doesn't exist."
                        }
                    )
                if not sales_contact.groups.filter(name="Sales team").exists():
                    raise serializers.ValidationError(
                        {
                            "sales_contact error":
                                "Please choose a user belonging to Sales team"
                        }
                    )
                instance.sales_contact = sales_contact
        instance.date_updated = datetime.datetime.now()
        instance.save()
        return instance


class ContractListSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()

    @staticmethod
    def get_client(instance):
        queryset = Client.objects.filter(id=instance.client.id)
        serializer = ClientListSerializer(queryset, many=True)
        return serializer.data

    class Meta:
        model = Contract
        fields = [
            'pk',
            'client',
            'amount',
            'status',
            'payment_due',
        ]


class ContractDetailSerializer(serializers.ModelSerializer):
    payment_due = serializers.DateTimeField(input_formats=['%Y/%m/%d %H:%M'])
    client = serializers.SerializerMethodField()
    id_client = serializers.IntegerField(required=False)

    class Meta:
        model = Contract
        fields = [
            'pk',
            'client',
            'id_client',
            'amount',
            'status',
            'payment_due',
            'date_created',
            'date_updated'
        ]
        read_only_fields = ['date_created', 'date_updated']

    @staticmethod
    def get_client(instance):
        queryset = Client.objects.filter(id=instance.client.id)
        serializer = ClientListSerializer(queryset, many=True)
        return serializer.data

    def validate_id_client(self, value):
        client = Client.objects.filter(id=value).first()
        request_user = self.context['request'].user
        if not client:
            raise ValidationError(f"Sorry, client {value} doesn't exist")
        if request_user.groups.filter(
                name="Sales team").exists() \
                and client.sales_contact != request_user:
            raise ValidationError(
                "Sorry, you are not the sales contact of this client")
        if self.context['request'].method == "POST":
            return client
        elif self.context['request'].method == "PUT":
            return client.id

    def validate_payment_due(self, value):
        if self.context['request'].method == "POST":
            Validators.is_prior_to_created_date(value, datetime.datetime.now())
        elif self.context['request'].method == "PUT":
            Validators.is_prior_to_created_date(
                value, self.instance.date_created)
        return value

    def validate(self, data):
        if "id_client" not in data:
            raise serializers.ValidationError(
                {
                    "id_client": "Please enter id of client"
                }
            )
        return data

    def create(self, validated_data):
        if "status" in validated_data:
            status = validated_data["status"]
        else:
            status = False
        contract = Contract.objects.create(
            client=validated_data["id_client"],
            amount=validated_data["amount"],
            status=status,
            payment_due=validated_data["payment_due"],
            date_created=datetime.datetime.now(),
            date_updated=datetime.datetime.now()
        )
        contract.save()
        return contract

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.date_updated = datetime.datetime.now()
        instance.client = Client.objects.get(id=validated_data['id_client'])
        instance.save()
        return instance


class EventListSerializer(serializers.ModelSerializer):
    contract = serializers.CharField()
    support_contact = serializers.CharField(required=False)
    status = serializers.CharField(source='get_event_status_display')
    event_status = serializers.CharField()
    event_date = serializers.DateTimeField(input_formats=['%Y/%m/%d %H:%M'])

    class Meta:
        model = Event
        fields = [
            'pk',
            'name',
            'contract',
            'support_contact',
            'event_status',
            'status',
            'event_date',
            'attendees'
        ]
        read_only_fields = ['date_created', 'date_updated', 'status']


class EventDetailSerializer(serializers.ModelSerializer):
    contract = serializers.CharField()
    support_contact = serializers.CharField(required=False)
    event_date = serializers.DateTimeField(input_formats=['%Y/%m/%d %H:%M'])
    status = serializers.CharField(
        source='get_event_status_display', required=False
    )
    event_status = serializers.CharField()

    class Meta:
        model = Event
        fields = [
            'pk',
            'name',
            'contract',
            'support_contact',
            'event_status',
            'status',
            'event_date',
            'attendees',
            'notes',
            'date_created',
            'date_updated'
        ]
        read_only_fields = ['date_created', 'date_updated', 'status']

    def validate_contract(self, value):
        contract = Contract.objects.filter(id=value).first()
        request_user = self.context['request'].user
        if not contract:
            raise ValidationError(f"Sorry, contract {value} doesn't exist")
        if self.context['request'].method == "POST":
            if Contract.objects.filter(id=value, event__isnull=False).exists():
                raise ValidationError(
                    "Sorry, there's already an event "
                    "associated with this contract")
        if self.context['request'].method == "PUT":
            if Contract.objects.filter(
                    id=value, event__isnull=False).exclude(
                    event__id=self.instance.id).exists():
                raise ValidationError(
                    "Sorry, there's already an event "
                    "associated with this contract")
        if request_user.groups.filter(
                name="Sales team"
        ).exists() and contract.client.sales_contact != request_user:
            raise ValidationError(
                "Sorry, you are not the sales contact of this client")
        if not contract.status:
            raise ValidationError("Sorry, this contract isn't signed yet")
        return contract

    @staticmethod
    def validate_event_status(value):
        if value not in ["Incoming", "In progress", "Closed"]:
            raise ValidationError(
                "Error in field <Event status>: "
                "Must be <Incoming>, <In progress> or <Closed>")
        if value == "Incoming":
            return 1
        elif value == "In progress":
            return 2
        return 3

    def validate_support_contact(self, value):
        request_user = self.context['request'].user
        if request_user.groups.filter(name="Sales team").exists():
            raise ValidationError(
                "Only users of management team "
                "can change/add support_contact. "
                "Please dont't use this field."
            )
        try:
            support_contact = User.objects.get(id=value)
            if not support_contact.groups.filter(name="Support team").exists():
                raise ValidationError(
                    f"Sorry, user {value} isn't member of support team")
        except User.DoesNotExist:
            raise ValidationError(f"Sorry, user {value} doesn't exist")
        return support_contact

    def validate(self, data):
        if (data['event_date'] > datetime.datetime.now()
                and data['event_status'] in [2, 3]):
            raise ValidationError(
                {"event_status": "This event can't be in progress"
                                 " or closed since its date "
                                 "is later than the current date"})
        elif (data['event_date'] < datetime.datetime.now()
              and data['event_status'] == 1):
            raise ValidationError(
                {"event_status": "This event can't be incoming "
                                 "since its date is earlier "
                                 "than the current date"})
        return data

    def create(self, validated_data):
        event = Event.objects.create(
            name=validated_data["name"],
            contract=validated_data["contract"],
            event_status=validated_data["event_status"],
            event_date=validated_data["event_date"],
            attendees=validated_data['attendees'],
            date_created=datetime.datetime.now(),
            date_updated=datetime.datetime.now()
        )
        if "support_contact" in validated_data:
            event.support_contact = validated_data['support_contact']
        if "notes" in validated_data:
            event.notes = validated_data['notes']
        event.save()
        return event

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.date_updated = datetime.datetime.now()
        instance.save()
        return instance
