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
            queryset = Client.objects.all()
            name = self.request.query_params.get('name')
            email = self.request.query_params.get('email')
            if name is not None:
                queryset = queryset.filter(last_name__icontains=name)
            if email is not None:
                queryset = queryset.filter(email__icontains=email)
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
            queryset = Contract.objects.all()
            client = self.request.query_params.get('client')
            email = self.request.query_params.get('email')
            date = self.request.query_params.get('date')
            after_date = self.request.query_params.get('after_date')
            before_date = self.request.query_params.get('before_date')
            amount = self.request.query_params.get('amount')
            greater_amount = self.request.query_params.get('greater_amount')
            lower_amount = self.request.query_params.get('lower_amount')
            if client is not None:
                queryset = queryset.filter(client__last_name__icontains=client)
            if email is not None:
                queryset = queryset.filter(client__email__icontains=email)
            if date is not None:
                queryset = queryset.filter(payment_due__date=date)
            if after_date is not None:
                queryset = queryset.filter(payment_due__date__gte=after_date)
            if before_date is not None:
                queryset = queryset.filter(payment_due__date__lte=before_date)
            if amount is not None:
                queryset = queryset.filter(amount=amount)
            if greater_amount is not None:
                queryset = queryset.filter(amount__gte=greater_amount)
            if lower_amount is not None:
                queryset = queryset.filter(amount__lte=lower_amount)
            return queryset
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
            permission_classes =  [IsManagementTeam|(IsSalesTeam & IsEventContractSalesContact)]
        elif self.request.method == 'PUT' and "pk" in self.request.parser_context["kwargs"]:
            permission_classes =  [IsManagementTeam|(IsSalesTeam & IsEventContractSalesContact)|(IsSupportTeam & IsEventSupportContact)]
        elif self.request.method == 'POST':
            permission_classes =  [IsManagementTeam|IsSalesTeam]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if "pk" not in self.request.parser_context["kwargs"]:
            queryset = Event.objects.all()
            client = self.request.query_params.get('client')
            email = self.request.query_params.get('email')
            date = self.request.query_params.get('date')
            after_date = self.request.query_params.get('after_date')
            before_date = self.request.query_params.get('before_date')
            if client is not None:
                queryset = queryset.filter(contract__client__last_name__icontains=client)
            if email is not None:
                queryset = queryset.filter(contract__client__email__icontains=email)
            if date is not None:
                queryset = queryset.filter(event_date__date=date)
            if after_date is not None:
                queryset = queryset.filter(event_date__date__gte=after_date)
            if before_date is not None:
                queryset = queryset.filter(event_date__date__lte=before_date)
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