from django.contrib import admin
from django.urls import resolve
from django.db.models import Q
from .models import User
from CRM.models import Client, Contract, Event
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from django.core.exceptions import ValidationError
from .validators import Validators
from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.html import format_html
import datetime
import logging

login_logger = logging.getLogger("login_security")
form_logger = logging.getLogger("form_security")

@receiver(user_logged_out)
def post_logout(sender, request, user, **kwargs):
    login_logger.info("user %s logged out admin site", user)


class MyAuthForm(AuthenticationForm):
    def get_invalid_login_error(self):
        self.error_messages["invalid_login"] = (
            "You must provide both valid username"
            " and password of an active user to access this site"
        )
        login_logger.warning(
            "someone tried to connect to admin site "
            "with username <%s> and password <%s>",
            self.cleaned_data["username"],
            self.cleaned_data["password"],
        )
        return forms.ValidationError(self.error_messages["invalid_login"])

    def confirm_login_allowed(self, user):
        if not user.is_staff:
            login_logger.warning(
                "user %s tried to connect to admin site", user)
            raise ValidationError(
                "Only members of management team are allowed to use this site."
            )
        login_logger.info("user %s connected to admin site", user)


class MyLoginView(LoginView):
    authentication_form = MyAuthForm


class UserForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("username",)

    def clean_first_name(self):
        Validators.check_letters_hyphen(
            self.cleaned_data.get("first_name"), "first_name"
        )
        return self.cleaned_data["first_name"]

    def clean_last_name(self):
        Validators.check_letters_hyphen(
            self.cleaned_data["last_name"], "last_name")
        return self.cleaned_data["last_name"]

    def clean_groups(self):
        if not self.cleaned_data["groups"]:
            raise ValidationError("Please affect this user to a group")
        if len(self.cleaned_data["groups"]) > 1:
            raise ValidationError("A user can belong to only one group")
        return self.cleaned_data["groups"]

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if password1:
            Validators.is_valid_password(password1)
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
        # in add form, username is set automatically
        if "username" not in self.fields:
            user.username = Validators.is_valid_username(
                user.first_name, user.last_name
            )
        if self.cleaned_data["password1"]:
            user.set_password(self.cleaned_data["password1"])
        if self.cleaned_data["groups"].first().name == "Management team":
            user.is_staff = True
        user.save()
        return user


class CustomUserAdmin(BaseUserAdmin):
    form = UserForm
    add_form = UserForm

    list_display = (
        "username",
        "last_name",
        "first_name",
        "number_of_clients",
        "management",
        "sales",
        "support",
    )
    list_filter = ("is_admin",)
    fieldsets = (
        (None, {"fields": ("first_name", "last_name", "username")}),
        (
            "Change password",
            {
                "classes": ("collapse",),
                "fields": ("password1", "password2"),
            },
        ),
        ("Permissions", {"fields": ("groups",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "fields": ("first_name",
                           "last_name",
                           "password1",
                           "password2"),
            },
        ),
        ("Permissions", {"fields": ("groups",)}),
    )
    search_fields = ("username",)
    ordering = ("username",)
    filter_horizontal = ("user_permissions", "groups")

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
            return "N/A"
        else:
            return format_html(
                "<b><i>{}</i></b>",
                Client.objects.filter(sales_contact=obj).count()
            )

    number_of_clients.short_description = "nb of clients"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields["password1"].required = False
            form.base_fields["password2"].required = False
        return form


class ClientForm(forms.ModelForm):
    def clean_first_name(self):
        Validators.check_letters_hyphen(
            self.cleaned_data.get("first_name"), "first_name"
        )
        return self.cleaned_data["first_name"]

    def clean_last_name(self):
        Validators.check_letters_hyphen(
            self.cleaned_data.get("last_name"), "last_name")
        return self.cleaned_data["last_name"]

    def clean_phone(self):
        Validators.check_is_phone_number(
            self.cleaned_data.get("phone"), "phone")
        return self.cleaned_data["phone"]

    def clean_mobile(self):
        Validators.check_is_phone_number(
            self.cleaned_data.get("mobile"), "mobile")
        return self.cleaned_data["mobile"]

    def save(self, commit=True):
        client = super().save(commit=False)
        client.date_updated = datetime.datetime.now()
        if client.pk is None:
            client.date_created = datetime.datetime.now()
        client.save()
        return client


class ClientAdmin(admin.ModelAdmin):
    form = ClientForm
    search_fields = ("last_name", "email")
    list_filter = ("last_name", "email")

    list_display = [
        "last_name",
        "first_name",
        "email",
        "company_name",
        "status",
        "sales_contact",
    ]
    readonly_fields = ["date_created", "date_updated"]

    @admin.display
    def status(self, obj):
        if Contract.objects.filter(client=obj).filter(status=True).exists():
            return "existing"
        else:
            return "prospect"


class ContractForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        try:
            # change form
            self.date_created = kwargs["instance"].date_created
        except (AttributeError, KeyError) as e:
            # add form
            form_logger.info("use of a Contract add form "
                             "according to %s error", type(e))
            self.date_created = datetime.datetime.now()
        super().__init__(*args, **kwargs)
        self.fields["amount"].error_messages = {
            "required": "Amount field is required "
                        "and must be a float or  an integer !"
        }

    def clean_payment_due(self):
        Validators.is_prior_to_created_date(
            self.cleaned_data["payment_due"], self.date_created
        )
        return self.cleaned_data["payment_due"]

    def clean(self):
        try:
            if (
                self.cleaned_data["status"] is False
                and self.initial["status"] is True
                and Event.objects.filter(contract=self.instance).exists()
            ):
                raise ValidationError(
                    "There's already an event "
                    "associated with this signed contract. "
                    "You can't cancel signature !"
                )
        except KeyError as e:
            # it's a create form, with no status field
            form_logger.info("use of a Contract add form "
                             "with no status field according "
                             "to %s error", type(e))

    def save(self, commit=True):
        contract = super().save(commit=False)
        if contract.pk is None:
            contract.date_created = datetime.datetime.now()
        contract.date_updated = datetime.datetime.now()
        contract.save()
        return contract


class ContractAdmin(admin.ModelAdmin):
    form = ContractForm

    list_display = ["pk", "client", "amount", "status", "sales_contact"]
    readonly_fields = ["sales_contact", "date_created", "date_updated"]

    def get_fields(self, request, obj=None):
        if not obj:
            self.readonly_fields = [
                "sales_contact",
                "date_created",
                "date_updated"]
            self.fields = [
                "client",
                "amount",
                "payment_due",
                "sales_contact",
                "date_created",
                "date_updated",
            ]
            return self.fields
        else:
            self.readonly_fields = [
                "sales_contact",
                "date_created",
                "date_updated"]
            self.fields = [
                "client",
                "status",
                "amount",
                "payment_due",
                "sales_contact",
                "date_created",
                "date_updated",
            ]
            return self.fields

    @admin.display
    def sales_contact(self, obj):
        return format_html("{}", obj.client.sales_contact)

    @admin.display
    def pk(self, obj):
        return format_html("Contract N°{}", obj.pk)

    pk.short_description = "Contract"


class EventForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["attendees"].error_messages = {
            "required": "Attendees field is required and must be an integer !"
        }

    @staticmethod
    def check_event_status(status, date_event):
        if date_event \
                and date_event > datetime.datetime.now() \
                and status in ["2", "3"]:
            raise ValidationError(
                "Error in field <Event status>: "
                "This event can't be in progress or closed "
                "since its date is later than the current date"
            )
        elif date_event \
                and date_event < datetime.datetime.now() \
                and status == "1":
            raise ValidationError(
                "Error in field <Event status>: "
                "This event can't be incoming since its date "
                "is earlier than the current date"
            )

    def clean(self):
        self.check_event_status(
            self.cleaned_data.get("event_status"),
            self.cleaned_data.get("event_date")
        )

    def save(self, commit=True):
        event = super().save(commit=False)
        if event.pk is None:
            event.date_created = datetime.datetime.now()
        event.date_updated = datetime.datetime.now()
        event.save()
        return event


class EventAdmin(admin.ModelAdmin):
    form = EventForm

    list_display = ["name", "contract", "support_contact",
                    "event_status", "event_date"]
    readonly_fields = ["date_created", "date_updated"]

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "contract":
            if resolve(request.path)[2]:
                event_id = resolve(request.path)[2]["object_id"]
                kwargs["queryset"] = \
                    Contract.objects.filter(status=True).filter(
                    Q(event__contract__isnull=True) | Q(event__id=event_id)
                )
                return super(EventAdmin, self).formfield_for_foreignkey(
                    db_field, request, **kwargs
                )
            else:
                kwargs["queryset"] = \
                    Contract.objects.filter(status=True).exclude(
                    event__contract__isnull=False
                )
                return super(EventAdmin, self).formfield_for_foreignkey(
                    db_field, request, **kwargs
                )
        if db_field.name == "support_contact":
            kwargs["queryset"] = \
                User.objects.filter(groups__name="Support team")
            return super(EventAdmin, self).formfield_for_foreignkey(
                db_field, request, **kwargs
            )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Contract, ContractAdmin)
admin.site.register(Event, EventAdmin)
