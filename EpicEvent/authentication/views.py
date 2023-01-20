from rest_framework.viewsets import ModelViewSet
from .models import User
from .serializers import UserSerializer
from CRM.permissions import IsAuthenticated, IsManagementTeam

class UserViewset(ModelViewSet):
    permission_classes = [IsAuthenticated, IsManagementTeam]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()
