from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from django.contrib.auth.models import Group
from .models import Client
from .serializers import ClientListSerializer, ClientDetailSerializer
from .permissions import IsAuthenticated
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

    def get_queryset(self):
        return Client.objects.all()

    def perform_create(self, serializer):
        if self.request.user.groups.filter(name="Sales team").exists() and not self.request.user.is_superuser:
            serializer.save(sales_contact=self.request.user,
                            date_created = datetime.datetime.now(),
                            date_updated = datetime.datetime.now())
        else:
            serializer.save(date_created=datetime.datetime.now(),
                            date_updated=datetime.datetime.now())

