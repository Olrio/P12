from django.contrib import admin
from django.urls import resolve
from django.db.models import Q
from .models import User
from CRM.models import Client, Contract, Event
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from django.core.exceptions import ValidationError
from .validators import Validators
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
import datetime

import logging


class MyAuthForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_staff:
            raise ValidationError(_("Only members of management team are allowed to use this site."), code="not staff")


class MyLoginView(LoginView):
    authentication_form = MyAuthForm

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username',)

    def clean_first_name(self):
        Validators.check_letters_hyphen(self.cleaned_data['first_name'], "first_name")
        return self.cleaned_data['first_name']

    def clean_last_name(self):
        Validators.check_letters_hyphen(self.cleaned_data['last_name'], "last_name")
        return self.cleaned_data['last_name']

    def clean_groups(self):
        if not self.cleaned_data['groups']:
            raise ValidationError("Please affect this user to a group")
        return self.cleaned_data['groups']

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        Validators.has_8_length(password1)
        Validators.contains_letters_and_numbers(password1)
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        Validators.two_entries_differ(password1, password2)
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

        if self.cleaned_data['groups'].first().name=="Management team":
            user.is_staff = True

        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ('username',)

    def clean_first_name(self):
        Validators.check_letters_hyphen(self.cleaned_data['first_name'], "first_name")
        return self.cleaned_data['first_name']

    def clean_last_name(self):
        Validators.check_letters_hyphen(self.cleaned_data['last_name'], "last_name")
        return self.cleaned_data['last_name']

    def clean_groups(self):
        if not self.cleaned_data['groups']:
            raise ValidationError("Please affect this user to a group")
        return self.cleaned_data['groups']

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if password1:
            Validators.has_8_length(password1)
            Validators.contains_letters_and_numbers(password1)
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2:
            Validators.two_entries_differ(password1, password2)
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = user.first_name.title()
        user.last_name = user.last_name.title()
        if self.cleaned_data['password1']:
            user.set_password(self.cleaned_data["password1"])
        if self.cleaned_data['groups'].filter(name='Management team').exists():
            user.is_staff = True
        else:
            user.is_staff = False
        user.save()
        return user



class CustomUserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('username', 'last_name', 'first_name',
                    'number_of_clients', 'management', 'sales', 'support')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'username')}),
        ('Change password', {
            'classes': ('collapse',),
            'fields': ('password1', 'password2'),
        }),
        ('Permissions', {'fields': ('groups',)}),
    )

    add_fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'password1', 'password2'),
        }),
        ('Permissions', {'fields': ('groups',)}),
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
        Validators.check_is_phone_number(self.cleaned_data.get('phone'), "phone")
        Validators.check_is_phone_number(self.cleaned_data.get('mobile'), "mobile")

    def save(self, commit=True):
        client = super().save(commit=False)
        client.date_updated = datetime.datetime.now()
        client.save()
        return client

class ClientCreationForm(forms.ModelForm):
    def clean(self):
        Validators.check_letters_hyphen(self.cleaned_data.get('first_name'), "first_name")
        Validators.check_letters_hyphen(self.cleaned_data.get('last_name'), "last_name")
        Validators.check_is_phone_number(self.cleaned_data.get('phone'), "phone")
        Validators.check_is_phone_number(self.cleaned_data.get('mobile'), "mobile")

    def save(self, commit=True):
        client = super().save(commit=False)
        client.date_created = datetime.datetime.now()
        client.date_updated = datetime.datetime.now()
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
        return super(ClientAdmin, self).get_form(request, **kwargs)

    list_display = ['last_name', 'first_name', 'company_name', 'status', 'sales_contact']
    readonly_fields = ['date_created', 'date_updated']


    @admin.display
    def status(self, obj):
        if Contract.objects.filter(client=obj).filter(status=True).exists():
            return "existing"
        else:
            return "prospect"


class ContractForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        """
        If form is change form, an instance of contract exists and has a date created
        If form is an add form, there's no instance yet, so no created date. Created date is current datetime
        """
        try:
            self.date_created = kwargs['instance'].date_created
        except (AttributeError, KeyError):
            self.date_created = datetime.datetime.now()
        super(ContractForm, self).__init__(*args, **kwargs)
        self.fields['client'].error_messages = {'required': ''}
        self.fields['amount'].error_messages = {'required': ''}
        self.fields['payment_due'].error_messages = {'required': ''}

    def clean(self):
        errors = dict()
        """
        Validation of payment_due date
        This field is required so if it is empty, a keyerror is catched and an error is raised
        If payment_due date exists, it is compared with created date which is current date or existing created date
        """
        try:
            if self.cleaned_data['payment_due'] < self.date_created:
                errors['payment_due'] = "Payment due date can't be prior to creation date"
        except KeyError:
            errors['payment_due'] = "You must specify a date and a time for the payment due !"
        try:
            self.cleaned_data['client']
        except KeyError:
            errors['client'] = "Any contract needs to be related to a client !"
        try:
            self.cleaned_data['amount']
        except KeyError:
            errors['amount'] = "Amount field is required and must be filled with a float or integer !"
        try:
            if self.cleaned_data['status'] == False\
                    and  self.initial['status'] == True \
                    and Event.objects.filter(contract=self.instance).exists():
                errors['status'] = "There's already an event associated with this signed contract. You can't cancel signature !"
        except KeyError:
            # it's a create form, without status field
            pass
        if errors:
                raise ValidationError(errors)

    def save(self, commit=True):
        contract = super().save(commit=False)
        if contract.pk is None:
            contract.date_created = datetime.datetime.now()
        contract.date_updated = datetime.datetime.now()
        contract.save()
        return contract


class ContractAdmin(admin.ModelAdmin):
    form = ContractForm

    list_display = ['pk', 'client', 'amount', 'status', 'sales_contact']
    readonly_fields = ['sales_contact', 'date_created', 'date_updated']


    def get_fields(self, request, obj=None):
        if not obj:
            self.readonly_fields = ['sales_contact', 'date_created', 'date_updated']
            self.fields = ['client', 'amount', 'payment_due', 'sales_contact', 'date_created',
                           'date_updated']
            return self.fields
        else:
            self.readonly_fields = ['sales_contact', 'date_created', 'date_updated']
            self.fields = ['client', 'status', 'amount', 'payment_due', 'sales_contact', 'date_created',
                           'date_updated']
            return self.fields



    @admin.display
    def sales_contact(self, obj):
        return format_html("{}", obj.client.sales_contact)


class EventCreationForm(forms.ModelForm):
    @staticmethod
    def check_event_status(status, date_event):
        if date_event and date_event > datetime.datetime.now() and status in ["2", "3"]:
            raise ValidationError(
                f"Error in field <Event status>: This event can't be in progress or closed since its date is later than the current date")
        elif date_event and date_event < datetime.datetime.now() and status == "1":
            raise ValidationError(
                f"Error in field <Event status>: This event can't be incoming since its date is earlier than the current date")


    def clean(self):
        self.check_event_status(self.cleaned_data.get('event_status'), self.cleaned_data.get('event_date'))


    def save(self, commit=True):
        event = super().save(commit=False)
        event.date_created = datetime.datetime.now()
        event.date_updated = datetime.datetime.now()
        event.save()
        return event

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
    change_form = EventChangeForm
    add_form = EventCreationForm

    list_display = ['name', 'contract', 'support_contact', 'event_status', 'event_date']
    readonly_fields = ['my_notes', 'date_created', 'date_updated']

    def get_form(self, request, obj=None, change=False, **kwargs):
        if not obj:
            self.form = self.add_form
        else:
            self.form = self.change_form
        self.form.user = request.user
        return super(EventAdmin, self).get_form(request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "contract":
            if resolve(request.path)[2]:
                event_id = resolve(request.path)[2]['object_id']
                kwargs["queryset"] = Contract.objects.filter(status=True).filter(Q(event__contract__isnull=True)|Q(event__id=event_id))
                return super(EventAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
            else:
                kwargs["queryset"] = Contract.objects.filter(status=True).exclude(event__contract__isnull=False)
                return super(EventAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "support_contact":
            kwargs["queryset"] = User.objects.filter(groups__name="Support team")
            return super(EventAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


    @admin.display(empty_value='***Nothing***')
    def my_notes(self, obj):
        return obj.notes

    def get_fields(self, request, obj=None):
        if obj:
            self.fields = ['name', 'contract', 'support_contact', 'event_status', 'event_date',
                        'attendees', 'date_created', 'date_updated',  'notes']
        else:
            self.fields =  ['name', 'contract', 'support_contact', 'event_status', 'event_date',
                        'attendees', 'date_created', 'date_updated', 'notes']
        return self.fields


admin.site.register(User, CustomUserAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Contract, ContractAdmin)
admin.site.register(Event, EventAdmin)