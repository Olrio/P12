from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase
from django.core.exceptions import ObjectDoesNotExist
from .models import User
from .serializers import (
    UserListSerializer,
    UserDetailSerializer,
    RegisterUserSerializer,
    UpdateUserSerializer,
    LoginUserSerializer
)
from CRM.permissions import (
    IsAuthenticated,
    IsManagementTeam
)


class TokenObtainPairView(TokenViewBase):
    serializer_class = LoginUserSerializer


class UserViewset(ModelViewSet):
    permission_classes = [IsAuthenticated, IsManagementTeam]

    def create(self, request):
        """override create function to custom response so that
            user can check fields not in the request body
            such as 'id' and 'username'
            """
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            data = serializer.data
            data.update({
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
            })
            return Response(data)
        else:
            return Response(serializer.errors)

    def get_serializer(self, *args, **kwargs):
        if self.request.method == "POST":
            self.serializer_class = RegisterUserSerializer
        elif self.request.method == "PUT":
            self.serializer_class = UpdateUserSerializer
        elif self.request.method == "GET" and (
                "pk" in self.request.parser_context["kwargs"]
        ):
            self.serializer_class = UserDetailSerializer
        elif self.request.method == "GET" and (
                "pk" not in self.request.parser_context["kwargs"]
        ):
            self.serializer_class = UserListSerializer
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
