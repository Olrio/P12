from rest_framework.viewsets import ModelViewSet
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from .models import Client, Contract, Event
from .serializers import ClientSerializer, ContractSerializer, EventSerializer
from .permissions import IsAuthenticated, \
    IsManagementTeam, IsSalesTeam, IsSupportTeam, IsClientSalesContact, IsContractSalesContact, IsEventSupportContact, IsEventContractSalesContact, IsClientEventSupportContact

class MultipleSerializerMixin:
    permission_classes = [IsAuthenticated]

class ClientViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = ClientSerializer

    def get_permissions(self):
        if self.request.method == 'GET' and "pk" not in self.request.parser_context["kwargs"]:
            permission_classes =  [IsManagementTeam|IsSalesTeam|IsSupportTeam]
        elif self.request.method == 'GET' and "pk" in self.request.parser_context["kwargs"]:
            permission_classes =  [IsManagementTeam|(IsSalesTeam & IsClientSalesContact)|(IsSupportTeam & IsClientEventSupportContact)]
        elif self.request.method == 'DELETE' and "pk" in self.request.parser_context["kwargs"]:
            permission_classes =  [IsManagementTeam|(IsSalesTeam & IsClientSalesContact)]
        elif self.request.method == 'PUT' and "pk" in self.request.parser_context["kwargs"]:
            permission_classes =  [IsManagementTeam|(IsSalesTeam & IsClientSalesContact)]
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


class ContractViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = ContractSerializer

    def get_permissions(self):
        if self.request.method == 'GET' and "pk" not in self.request.parser_context["kwargs"]:
            permission_classes =  [IsManagementTeam|IsSalesTeam|IsSupportTeam]
        elif self.request.method == 'GET' and "pk" in self.request.parser_context["kwargs"]:
            permission_classes =  [IsManagementTeam|(IsSalesTeam & IsContractSalesContact)]
        elif self.request.method == 'DELETE' and "pk" in self.request.parser_context["kwargs"]:
            permission_classes =  [IsManagementTeam|(IsSalesTeam & IsContractSalesContact)]
        elif self.request.method == 'PUT' and "pk" in self.request.parser_context["kwargs"]:
            permission_classes =  [IsManagementTeam|(IsSalesTeam & IsContractSalesContact)]
        elif self.request.method == 'POST':
            permission_classes =  [IsManagementTeam|IsSalesTeam]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if "pk" not in self.request.parser_context["kwargs"]:
            return Contract.objects.all()
        else:
            contract_pk = self.request.parser_context["kwargs"]["pk"]
            try:
                Contract.objects.get(id=contract_pk)
            except ObjectDoesNotExist:
                raise NotFound(
                    detail=f"Sorry, contract {contract_pk} doesn't exist"
                )
            queryset = Contract.objects.filter(
                id=contract_pk
            )
            return queryset

class EventViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.request.method == 'GET' and "pk" not in self.request.parser_context["kwargs"]:
            permission_classes =  [IsManagementTeam|IsSalesTeam|IsSupportTeam]
        elif self.request.method == 'GET' and "pk" in self.request.parser_context["kwargs"]:
            permission_classes =  [IsManagementTeam|(IsSalesTeam & IsEventContractSalesContact)|(IsSupportTeam & IsEventSupportContact)]
        elif self.request.method == 'DELETE' and "pk" in self.request.parser_context["kwargs"]:
            permission_classes =  [IsManagementTeam|(IsSalesTeam & IsEventContractSalesContact)|(IsSupportTeam & IsEventSupportContact)]
        elif self.request.method == 'PUT' and "pk" in self.request.parser_context["kwargs"]:
            permission_classes =  [IsManagementTeam|(IsSalesTeam & IsEventContractSalesContact)|(IsSupportTeam & IsEventSupportContact)]
        elif self.request.method == 'POST':
            permission_classes =  [IsManagementTeam|IsSalesTeam]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if "pk" not in self.request.parser_context["kwargs"]:
            return Event.objects.all()
        else:
            event_pk = self.request.parser_context["kwargs"]["pk"]
            try:
                Event.objects.get(id=event_pk)
            except ObjectDoesNotExist:
                raise NotFound(
                    detail=f"Sorry, event {event_pk} doesn't exist"
                )
            queryset = Event.objects.filter(
                id=event_pk
            )
            return queryset