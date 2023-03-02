from rest_framework.viewsets import ModelViewSet
from django.core.exceptions import (
    ObjectDoesNotExist,
    FieldError
)
from rest_framework.exceptions import NotFound
from .models import (
    Client,
    Contract,
    Event
)
from .serializers import (
    ClientDetailSerializer,
    ClientListSerializer,
    ContractDetailSerializer,
    ContractListSerializer,
    EventDetailSerializer,
    EventListSerializer
)
from .permissions import (
    IsAuthenticated,
    IsManagementTeam,
    IsSalesTeam,
    IsSupportTeam,
    IsClientSalesContact,
    IsContractSalesContact,
    IsEventSupportContact,
    IsEventContractSalesContact,
    IsClientEventSupportContact
)


class MultipleSerializerMixin:
    permission_classes = [IsAuthenticated]
    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == "retrieve" and self.get_serializer_class is not None:
            return self.detail_serializer_class
        elif self.action == "update" and self.get_serializer_class is not None:
            return self.detail_serializer_class
        elif self.action == "create":
            return self.detail_serializer_class
        return super().get_serializer_class()


class ClientViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = ClientListSerializer
    detail_serializer_class = ClientDetailSerializer

    def get_permissions(self):
        permission_classes = []
        if (self.request.method == 'GET'
                and "pk" not in self.request.parser_context["kwargs"]):
            permission_classes = [
                IsManagementTeam |
                IsSalesTeam |
                IsSupportTeam
            ]
        elif (self.request.method == 'GET'
              and "pk" in self.request.parser_context["kwargs"]):
            permission_classes = [
                IsManagementTeam |
                (IsSalesTeam & IsClientSalesContact) |
                (IsSupportTeam & IsClientEventSupportContact)
            ]
        elif (self.request.method == 'DELETE'
              and "pk" in self.request.parser_context["kwargs"]):
            permission_classes = [
                IsManagementTeam |
                (IsSalesTeam & IsClientSalesContact)
            ]
        elif (self.request.method == 'PUT'
              and "pk" in self.request.parser_context["kwargs"]):
            permission_classes = [
                IsManagementTeam |
                (IsSalesTeam & IsClientSalesContact)
            ]
        elif self.request.method == 'POST':
            permission_classes = [IsManagementTeam | IsSalesTeam]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if "pk" not in self.request.parser_context["kwargs"]:
            queryset = Client.objects.all()
            try:
                queryset = queryset.filter(
                    **dict(self.request.query_params.items())
                )
                return queryset
            except FieldError:
                raise NotFound(
                    detail=(
                        "Sorry, looks like you search for inexistent fields. "
                        "Please ensure you correctly entered searched fields."
                    )
                )
            return queryset
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
    serializer_class = ContractListSerializer
    detail_serializer_class = ContractDetailSerializer

    def get_permissions(self):
        if (self.request.method == 'GET'
                and "pk" not in self.request.parser_context["kwargs"]):
            permission_classes = [
                IsManagementTeam |
                IsSalesTeam |
                IsSupportTeam
            ]
        elif (self.request.method == 'GET'
              and "pk" in self.request.parser_context["kwargs"]):
            permission_classes = [
                IsManagementTeam |
                (IsSalesTeam & IsContractSalesContact)
            ]
        elif (self.request.method == 'DELETE'
              and "pk" in self.request.parser_context["kwargs"]):
            permission_classes = [
                IsManagementTeam |
                (IsSalesTeam & IsContractSalesContact)
            ]
        elif (self.request.method == 'PUT'
              and "pk" in self.request.parser_context["kwargs"]):
            permission_classes = [
                IsManagementTeam |
                (IsSalesTeam & IsContractSalesContact)
            ]
        elif self.request.method == 'POST':
            permission_classes = [
                IsManagementTeam |
                IsSalesTeam
            ]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if "pk" not in self.request.parser_context["kwargs"]:
            queryset = Contract.objects.all()
            try:
                queryset = queryset.filter(
                    **dict(self.request.query_params.items())
                )
                return queryset
            except FieldError:
                raise NotFound(
                    detail=(
                        "Sorry, looks like you search for inexistent fields. "
                        "Please ensure you correctly entered searched fields."
                    )
                )
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
    serializer_class = EventListSerializer
    detail_serializer_class = EventDetailSerializer

    def get_permissions(self):
        if (self.request.method == 'GET'
                and "pk" not in self.request.parser_context["kwargs"]):
            permission_classes = [
                IsManagementTeam |
                IsSalesTeam |
                IsSupportTeam
            ]
        elif (self.request.method == 'GET'
              and "pk" in self.request.parser_context["kwargs"]):
            permission_classes = [
                IsManagementTeam |
                (IsSalesTeam & IsEventContractSalesContact) |
                (IsSupportTeam & IsEventSupportContact)
            ]
        elif (self.request.method == 'DELETE'
              and "pk" in self.request.parser_context["kwargs"]):
            permission_classes = [
                IsManagementTeam |
                (IsSalesTeam & IsEventContractSalesContact)
            ]
        elif (self.request.method == 'PUT'
              and "pk" in self.request.parser_context["kwargs"]):
            permission_classes = [
                IsManagementTeam |
                (IsSalesTeam & IsEventContractSalesContact) |
                (IsSupportTeam & IsEventSupportContact)
            ]
        elif self.request.method == 'POST':
            permission_classes = [
                IsManagementTeam |
                IsSalesTeam
            ]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if "pk" not in self.request.parser_context["kwargs"]:
            queryset = Event.objects.all()
            try:
                queryset = queryset.filter(
                    **dict(self.request.query_params.items())
                )
                return queryset
            except FieldError:
                raise NotFound(
                    detail=(
                        "Sorry, looks like you search for inexistent fields. "
                        "Please ensure you correctly entered searched fields."
                    )
                )
            return queryset
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
