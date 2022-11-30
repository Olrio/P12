from django.urls import include, path
from .views import ClientCreate, ClientList, ClientDelete

urlpatterns = [
    path('create/', ClientCreate.as_view(), name='create-client'),
    path('<int:pk>/delete/', ClientDelete.as_view(), name='delete-client'),
    path('', ClientList.as_view()),
    ]
