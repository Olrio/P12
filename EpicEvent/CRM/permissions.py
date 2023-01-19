from rest_framework.permissions import BasePermission
from CRM.models import Client


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

class IsManagementTeam(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.groups.filter(name="Management team").exists())

class IsSalesTeam(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.groups.filter(name="Sales team").exists())

class IsSupportTeam(BasePermission):
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