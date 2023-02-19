from rest_framework.permissions import BasePermission
from CRM.models import Client, Contract, Event


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsManagementTeam(BasePermission):
    message = "Sorry, only members of the management team" \
              " can perform this action"

    def has_permission(self, request, view):
        return bool(
            request.user.groups.filter(name="Management team").exists())


class IsSalesTeam(BasePermission):
    message = "Sorry, only members of the sales team can perform this action"

    def has_permission(self, request, view):
        return bool(request.user.groups.filter(name="Sales team").exists())


class IsSupportTeam(BasePermission):
    message = "Sorry, only members of the support team can perform this action"

    def has_permission(self, request, view):
        return bool(request.user.groups.filter(name="Support team").exists())


class IsClientSalesContact(BasePermission):
    message = (
        "Sorry, you don't have permission to access "
        "informations related to this client."
        "You're not this client's sales contact."
    )

    def has_object_permission(self, request, view, obj):
        return (
            Client.objects.filter(
                pk=obj.pk,
                sales_contact=request.user).exists()
        )


class IsClientEventSupportContact(BasePermission):
    message = (
        "Sorry, you don't have permission to access "
        "informations related to this client."
        "You're not in charge of an event related to this client."
    )

    def has_object_permission(self, request, view, obj):
        return (
            Client.objects.filter(
                pk=obj.pk,
                contract__event__support_contact=request.user).exists()
        )


class IsContractSalesContact(BasePermission):
    message = (
        "Sorry, you don't have permission to access "
        "informations related to this client."
        "You're not this client's sales contact."
    )

    def has_object_permission(self, request, view, obj):
        return (
            Contract.objects.filter(
                pk=obj.pk,
                client__sales_contact=request.user).exists()
        )


class IsEventSupportContact(BasePermission):
    message = (
        "Sorry, you don't have permission to access "
        "informations related to this event."
        "You're not this event's support contact."
    )

    def has_object_permission(self, request, view, obj):
        return (
            Event.objects.filter(
                pk=obj.pk,
                support_contact=request.user).exists()
        )


class IsEventContractSalesContact(BasePermission):
    message = (
        "Sorry, you don't have permission to access "
        "informations related to this event."
        "You're not this event's client's sales contact."
    )

    def has_object_permission(self, request, view, obj):
        return (
            Event.objects.filter(
                pk=obj.pk,
                contract__client__sales_contact=request.user).exists()
        )
