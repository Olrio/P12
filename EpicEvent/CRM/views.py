from rest_framework.viewsets import ModelViewSet
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from rest_framework import serializers
from django.contrib.auth.models import Group
from .models import Client
from .serializers import ClientListSerializer, ClientDetailSerializer
from .permissions import IsAuthenticated, \
    IsManagementTeam, IsSalesTeam, IsSupportTeam, IsClientSalesContact
import datetime

class MultipleSerializerMixin:
    detail_serializer_class = None
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve" and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()

class ClientViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = ClientListSerializer
    detail_serializer_class = ClientDetailSerializer
    # permission_classes = [IsManagementTeam|IsSalesTeam|IsSupportTeam]


    def get_permissions(self):
        if self.request.method == 'GET' and "pk" not in self.request.parser_context["kwargs"]:
            permission_classes =  [IsManagementTeam|IsSalesTeam|IsSupportTeam]
        elif self.request.method == 'GET' and "pk" in self.request.parser_context["kwargs"]:
            permission_classes =  [IsManagementTeam|IsSalesTeam, IsClientSalesContact]
        elif self.request.method == 'POST':
            permission_classes =  [IsManagementTeam|IsSalesTeam]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if "pk" not in self.request.parser_context["kwargs"]:
            return Client.objects.all()
        else:
            client_pk = self.request.parser_context["kwargs"]["pk"]
            try:
                Client.objects.get(id=client_pk)
            except ObjectDoesNotExist:
                raise NotFound(
                    detail=f"Sorry, client {client_pk} doesn't exist"
                )
            queryset = Client.objects.filter(
                id=client_pk
            )
            return queryset

    def perform_create(self, serializer):
        if self.request.user.groups.filter(name="Sales team").exists() and not self.request.user.is_superuser:
            serializer.save(sales_contact=self.request.user,
                            date_created = datetime.datetime.now(),
                            date_updated = datetime.datetime.now())
        else:
            serializer.save(date_created=datetime.datetime.now(),
                            date_updated=datetime.datetime.now())

