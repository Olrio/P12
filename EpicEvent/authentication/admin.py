from django.contrib import admin
from django.db.models import Q
from .models import User
from CRM.models import Client, Contract, Event
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, Permission
from django import forms
from django.db import IntegrityError
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from .validators import Validators
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AuthenticationForm
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



class CustomUserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('username', 'last_name', 'first_name',
                    'number_of_clients', 'management', 'sales', 'support')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'username')}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
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
        if self.current_user:
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
        if request.user.groups.filter(name="Sales team").exists():
            self.form.current_user = request.user
        else:
            self.form.current_user = None
        return super(ClientAdmin, self).get_form(request, **kwargs)

    list_display = ['last_name', 'first_name', 'company_name', 'status', 'sales_contact']
    readonly_fields = ['sales_contact_no_link', 'date_created', 'date_updated']

    def has_delete_permission(self, request, obj=None):
        if obj:
            if request.user == obj.sales_contact \
                    or request.user.is_superuser \
                    or request.user.groups.filter(name="Management team").exists():
                return True
            else:
                return False

    def has_change_permission(self, request, obj=None):
        if obj:
            if request.user == obj.sales_contact \
                    or request.user.is_superuser \
                    or request.user.groups.filter(name="Management team").exists():
                return True
            else:
                return False

    @admin.display
    def sales_contact_no_link(self, obj):
        return format_html("{}", obj.sales_contact)
    sales_contact_no_link.short_description = "Sales contact"

    @admin.display
    def status(self, obj):
        if Contract.objects.filter(client=obj).filter(status=True).exists():
            return "existing"
        else:
            return "prospect"


    def get_fields(self, request, obj=None):
        if not obj:
            if request.user.is_superuser or request.user.groups.filter(name="Management team").exists():
                return ['first_name', 'last_name', 'email', 'phone', 'mobile', 'company_name', 'date_created', 'date_updated', 'sales_contact']
            else:
                return ['first_name', 'last_name', 'email', 'phone', 'mobile', 'company_name', 'date_created',
                        'date_updated', 'sales_contact_no_link']
        else:
            if request.user.is_superuser or request.user.groups.filter(name="Management team").exists():
                return ['first_name', 'last_name', 'email', 'phone', 'mobile', 'company_name', 'date_created', 'date_updated', 'sales_contact']
            else:
                return ['first_name', 'last_name', 'email', 'phone', 'mobile', 'company_name', 'date_created', 'date_updated', 'sales_contact_no_link']


class ContractCreationForm(forms.ModelForm):
    def clean(self):
        Validators.check_is_float(self.cleaned_data.get('amount'), "Amount")

    def save(self, commit=True):
        contract = super().save(commit=False)
        contract.date_created = datetime.datetime.now()
        contract.date_updated = datetime.datetime.now()
        contract.save()
        return contract


class ContractChangeForm(forms.ModelForm):
    def clean(self):
        Validators.check_is_float(self.cleaned_data.get('amount'), "Amount")


    def save(self, commit=True):
        contract = super().save(commit=False)
        contract.date_updated = datetime.datetime.now()
        contract.save()
        return contract

class ContractAdmin(admin.ModelAdmin):
    change_form = ContractChangeForm
    add_form = ContractCreationForm

    list_display = ['pk', 'client', 'amount', 'status', 'sales_contact']
    readonly_fields = ['sales_contact', 'date_created', 'date_updated']


    # a user member belonging to 'sales' group can create a contract only for his clients
    # a superuser or a user belonging to 'management' group can create a contract for any client
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if "/add/" in request.path:
            if db_field.name == "client" and request.user.is_superuser:
                kwargs["queryset"] = Client.objects.all()
            elif db_field.name == "client" and request.user.groups.filter(name="Sales team").exists():
                kwargs["queryset"] = Client.objects.filter(sales_contact=request.user)
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
        if "/change/" in request.path:
            if db_field.name == "client" and request.user.is_superuser:
                kwargs["queryset"] = Client.objects.all()
            elif db_field.name == "client" and request.user.groups.filter(name="Sales team").exists():
                kwargs["queryset"] = Client.objects.filter(sales_contact=request.user)
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, change=False, **kwargs):
        if not obj:
            self.form = self.add_form
        else:
            self.form = self.change_form
        if request.user.groups.filter(name="Sales team").exists() and not request.user.is_superuser:
            self.form.current_user = request.user
        else:
            self.form.current_user = None
        return super(ContractAdmin, self).get_form(request, **kwargs)

    def has_delete_permission(self, request, obj=None):
        if obj:
            if request.user == obj.client.sales_contact \
                    or request.user.is_superuser \
                    or request.user.groups.filter(name="Management team").exists():
                return True
            else:
                return False

    def has_change_permission(self, request, obj=None):
        if obj:
            if request.user == obj.client.sales_contact \
                    or request.user.is_superuser \
                    or request.user.groups.filter(name="Management team").exists():
                return True
            else:
                return False


    def get_fields(self, request, obj=None):
        if not obj:
            if request.user.is_superuser or request.user.groups.filter(name="Management team").exists():
                self.readonly_fields = ['sales_contact', 'date_created', 'date_updated']
                self.fields = ['client', 'status', 'amount', 'payment_due', 'sales_contact', 'date_created',
                               'date_updated']
                return self.fields
            else:
                self.readonly_fields = []
                self.fields = ['client', 'amount', 'payment_due']
                return self.fields
        else:
            if request.user.is_superuser or request.user.groups.filter(name="Management team").exists():
                self.readonly_fields = ['sales_contact', 'date_created', 'date_updated']
                self.fields = ['client', 'status', 'amount', 'payment_due', 'sales_contact', 'date_created',
                               'date_updated']
                return self.fields
            else:
                self.readonly_fields = ['sales_contact', 'date_created', 'date_updated']
                self.fields = ['client', 'sales_contact', 'status', 'amount', 'payment_due', 'date_created', 'date_updated']
                return self.fields


    @admin.display
    def sales_contact(self, obj):
        return format_html("{}", obj.client.sales_contact)


class EventCreationForm(forms.ModelForm):
    @staticmethod
    def check_event_status(status, date_event):
        if date_event > datetime.datetime.now() and status in ["2", "3"]:
            raise ValidationError(
                f"Error in field <Event status>: This event can't be in progress or closed since its date is later than the current date")
        elif date_event < datetime.datetime.now() and status == "1":
            raise ValidationError(
                f"Error in field <Event status>: This event can't be incoming since its date is earlier than the current date")


    def clean(self):
        self.check_event_status(self.cleaned_data.get('event_status'), self.cleaned_data.get('event_date'))
        if not Contract.objects.filter(client__sales_contact=self.user).filter(status=True).exclude(Q(event__isnull=False)):
            raise ValidationError('You have no available client with a signed contract.'
                                  'Please ensure that the client associated with this event has signed a contract.'
                                  'Remember that a contract can be associated with only one event')


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
    readonly_fields = ['contract_no_link', 'support_contact_no_link', 'my_notes', 'date_created', 'date_updated']

    def get_form(self, request, obj=None, change=False, **kwargs):
        if not obj:
            self.form = self.add_form
        else:
            self.form = self.change_form
        self.form.user = request.user
        return super(EventAdmin, self).get_form(request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if request.user.is_superuser or request.user.groups.filter(name="Management team").exists():
            if db_field.name == "contract":
                kwargs["queryset"] = Client.objects.all()
                return super(EventAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
            if db_field.name == "support_contact":
                kwargs["queryset"] = User.objects.all()
                return super(EventAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "contract":
            kwargs["queryset"] = Contract.objects.filter(client__sales_contact=request.user).filter(status=True).exclude(Q(event__isnull=False))
            return super(EventAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "support_contact":
            kwargs["queryset"] = User.objects.filter(groups__name="Support team")
            return super(EventAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def has_change_permission(self, request, obj=None):
        if obj:
            if request.user == obj.contract.client.sales_contact or request.user.is_superuser or request.user == obj.support_contact or request.user.groups.filter(name="Management team").exists():
                return True
            else:
                return False

    @admin.display(empty_value='***Nothing***')
    def my_notes(self, obj):
        return obj.notes

    def get_fields(self, request, obj=None):
        if obj:
            if request.user.is_superuser or request.user.groups.filter(name="Management team").exists():
                return ['name', 'contract', 'support_contact', 'event_status', 'event_date',
                        'attendees', 'date_created', 'date_updated',  'notes']
            else:
                if request.user == obj.support_contact:
                    return ['name', 'contract_no_link', 'support_contact_no_link', 'event_status', 'event_date',
                            'attendees', 'date_created', 'date_updated', 'my_notes']
                else:
                    return ['name', 'contract', 'support_contact_no_link', 'event_status', 'event_date',
                        'attendees', 'date_created', 'date_updated',  'my_notes']
        else:
            if request.user.is_superuser or request.user.groups.filter(name="Management team").exists():
                return ['name', 'contract', 'support_contact', 'event_status', 'event_date',
                        'attendees', 'date_created', 'date_updated', 'notes']
            else:
                return ['name', 'contract', 'support_contact_no_link', 'event_status', 'event_date',
                        'attendees', 'date_created', 'date_updated', 'notes']

    @admin.display
    def contract_no_link(self, obj):
        return format_html("{}", obj.contract)
    contract_no_link.short_description = "Contrat"

    @admin.display
    def support_contact_no_link(self, obj):
        return format_html("{}", obj.support_contact)
    support_contact_no_link.short_description = "Support contact"

admin.site.register(User, CustomUserAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Contract, ContractAdmin)
admin.site.register(Event, EventAdmin)