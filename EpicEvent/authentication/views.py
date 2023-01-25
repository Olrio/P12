from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import NotFound
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from .models import User
from .serializers import UserSerializer, RegisterUserSerializer, UpdateUserSerializer
from CRM.permissions import IsAuthenticated, IsManagementTeam

class UserViewset(ModelViewSet):
    permission_classes = [IsAuthenticated, IsManagementTeam]

    def get_serializer(self, *args, **kwargs):
        if self.request.method == "POST":
            self.serializer_class = RegisterUserSerializer
        elif self.request.method == "PUT":
            self.serializer_class = UpdateUserSerializer
        else:
            self.serializer_class = UserSerializer
        return self.serializer_class(*args, **kwargs)


    def get_queryset(self):
        if not self.request.parser_context["kwargs"]:
            return User.objects.all()

        else:
            user_pk = self.request.parser_context["kwargs"]["pk"]
            try:
                User.objects.get(id=user_pk)
            except ObjectDoesNotExist:
                raise NotFound(
                    detail=f"Sorry, user {user_pk} doesn't exist"
                )
            queryset = User.objects.filter(
                id=user_pk
            )
            return queryset
