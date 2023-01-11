from rest_framework import generics
from .serializers import UserSerializer

class RegisterUserViewset(generics.CreateAPIView):
    serializer_class = UserSerializer