from django.contrib import admin
from .models import User
from CRM.models import Client, Contract, Event
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from django import forms
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from .validators import Validators
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.html import format_html
import datetime

import logging


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username',)

    def clean(self):
        Validators.check_letters_hyphen(self.cleaned_data.get('first_name'), "first_name")
        Validators.check_letters_hyphen(self.cleaned_data.get('last_name'), "last_name")

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Password error : your two entries differ !")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
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


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('username',)


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    readonly_fields = ['username']

    list_display = ('username', 'last_name', 'first_name',
                    'number_of_clients', 'management', 'sales', 'support')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'username')}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'password1', 'password2'),
        }),
        ('Permissions', {'fields': ('groups', )}),
    )
    search_fields = ('username',)
    ordering = ('username',)
    filter_horizontal = ('user_permissions', 'groups')

    def management(self, obj):
        return obj.groups.filter(name="Management team").exists()

    def sales(self, obj):
        return obj.groups.filter(name="Sales team").exists()

    def support(self, obj):
        return obj.groups.filter(name="Support team").exists()

    management.boolean = True
    sales.boolean = True
    support.boolean = True

    def number_of_clients(self, obj):
        if not self.sales(obj):
            return  "N/A"
        else :
            return format_html("<b><i>{}</i></b>", Client.objects.filter(sales_contact=obj).count())
    number_of_clients.short_description = "nb of clients"


class ClientChangeForm(forms.ModelForm):
    def clean(self):
        Validators.check_letters_hyphen(self.cleaned_data.get('first_name'), "first_name")
        Validators.check_letters_hyphen(self.cleaned_data.get('last_name'), "last_name")
        Validators.check_phone_number(self.cleaned_data.get('phone'), "phone")
        Validators.check_phone_number(self.cleaned_data.get('mobile'), "mobile")

    def save(self, commit=True):
        client = super().save(commit=False)
        client.date_updated = datetime.datetime.now()
        client.save()
        return client

class ClientCreationForm(forms.ModelForm):
    def clean(self):
        Validators.check_letters_hyphen(self.cleaned_data.get('first_name'), "first_name")
        Validators.check_letters_hyphen(self.cleaned_data.get('last_name'), "last_name")
        Validators.check_phone_number(self.cleaned_data.get('phone'), "phone")
        Validators.check_phone_number(self.cleaned_data.get('mobile'), "mobile")

    def save(self, commit=True):
        client = super().save(commit=False)
        client.date_created = datetime.datetime.now()
        client.date_updated = datetime.datetime.now()
        client.sales_contact = self.current_user
        client.save()
        return client

class ClientAdmin(admin.ModelAdmin):
    change_form = ClientChangeForm
    add_form = ClientCreationForm

    def get_form(self, request, obj=None, change=False, **kwargs):
        if not obj:
            self.form = self.add_form
        else:
            self.form = self.change_form
        self.form.current_user = request.user
        return super(ClientAdmin, self).get_form(request, **kwargs)

    list_display = ['last_name', 'first_name', 'company_name', 'sales_contact']
    readonly_fields = ['sales_contact_no_link', 'date_created', 'date_updated']

    def has_change_permission(self, request, obj=None):
        if obj:
            if request.user == obj.sales_contact or request.user.is_superuser:
                return True
            else:
                return False

    @admin.display
    def sales_contact_no_link(self, obj):
        return format_html("{}", obj.sales_contact)
    sales_contact_no_link.short_description = "Sales contact"


    def get_fields(self, request, obj=None):
        if not obj:
            return ['first_name', 'last_name', 'email', 'phone', 'mobile', 'company_name', 'date_created', 'date_updated', 'sales_contact_no_link']
        else:
            if request.user.is_superuser:
                return ['first_name', 'last_name', 'email', 'phone', 'mobile', 'company_name', 'date_created', 'date_updated', 'sales_contact']
            else:
                return ['first_name', 'last_name', 'email', 'phone', 'mobile', 'company_name', 'date_created', 'date_updated', 'sales_contact_no_link']


class ContractChangeForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = "__all__"

    def save(self, commit=True):
        contract = super().save(commit=False)
        contract.date_updated = datetime.datetime.now()
        contract.save()
        return contract

class ContractAdmin(admin.ModelAdmin):
    form = ContractChangeForm

    list_display = ['client', 'sales_contact', 'amount', 'my_status']
    readonly_fields = ['client', 'sales_contact_no_link', 'my_status', 'date_created', 'date_updated']

    def has_change_permission(self, request, obj=None):
        if obj:
            if request.user == obj.sales_contact or request.user.is_superuser:
                return True
            else:
                return False

    def my_status(self, obj):
        """ status will be True only if at least one event isn't closed """
        if Event.objects.filter(client=obj.client_id).filter(event_date__gte=str(datetime.datetime.now())).exists():
            obj.status = True
        else:
            obj.status = False
        obj.save()
        return obj.status
    my_status.boolean = True

    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ['client', 'sales_contact', 'my_status', 'amount', 'payment_due', 'date_created', 'date_updated']
        else:
            return ['client', 'sales_contact_no_link', 'my_status', 'amount', 'payment_due', 'date_created', 'date_updated']


    @admin.display
    def sales_contact_no_link(self, obj):
        return format_html("{}", obj.sales_contact)
    sales_contact_no_link.short_description = "Sales contact"

class EventChangeForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = "__all__"

    @staticmethod
    def check_event_status(status, date_event):
        if date_event > datetime.datetime.now() and status in ["2", "3"] :
            raise ValidationError(f"Error in field <Event status>: This event can't be in progress or closed since its date is later than the current date")
        elif date_event < datetime.datetime.now() and status == "1":
            raise ValidationError(f"Error in field <Event status>: This event can't be incoming since its date is earlier than the current date")

    def clean(self):
        self.check_event_status(self.cleaned_data.get('event_status'), self.cleaned_data.get('event_date'))

    def save(self, commit=True):
        event = super().save(commit=False)
        event.date_updated = datetime.datetime.now()
        event.save()
        return event

class EventAdmin(admin.ModelAdmin):
    form = EventChangeForm

    list_display = ['name', 'client', 'support_contact', 'event_status', 'event_date']
    readonly_fields = ['client_no_link', 'support_contact_no_link', 'my_notes', 'date_created', 'date_updated']

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if request.user.is_superuser:
            if db_field.name == "client":
                kwargs["queryset"] = Client.objects.all()
                return super(EventAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
            if db_field.name == "support_contact":
                kwargs["queryset"] = User.objects.all()
                return super(EventAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "client":
            kwargs["queryset"] = Client.objects.filter(sales_contact=request.user)
            return super(EventAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "support_contact":
            kwargs["queryset"] = User.objects.filter(groups__name="Support team")
            return super(EventAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def has_change_permission(self, request, obj=None):
        if obj:
            if request.user == obj.client.sales_contact or request.user.is_superuser or request.user == obj.support_contact:
                return True
            else:
                return False

    @admin.display(empty_value='***Nothing***')
    def my_notes(self, obj):
        return obj.notes

    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ['name', 'client', 'support_contact', 'event_status', 'event_date',
                    'attendees', 'date_created', 'date_updated',  'notes']
        else:
            if request.user == obj.support_contact:
                return ['name', 'client_no_link', 'support_contact_no_link', 'event_status', 'event_date',
                        'attendees', 'date_created', 'date_updated', 'my_notes']
            else:
                return ['name', 'client', 'support_contact_no_link', 'event_status', 'event_date',
                    'attendees', 'date_created', 'date_updated',  'my_notes']

    @admin.display
    def client_no_link(self, obj):
        return format_html("{}", obj.client)
    client_no_link.short_description = "Client"

    @admin.display
    def support_contact_no_link(self, obj):
        return format_html("{}", obj.support_contact)
    support_contact_no_link.short_description = "Support contact"

admin.site.register(User, UserAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Contract, ContractAdmin)
admin.site.register(Event, EventAdmin)