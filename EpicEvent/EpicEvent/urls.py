"""EpicEvent URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_nested import routers
from authentication.admin import MyLoginView
from authentication.views import (
    UserViewset,
    TokenObtainPairView
)
from CRM.views import (
    ClientViewset,
    ContractViewset,
    EventViewset
)

admin.sites.AdminSite.site_header = 'Epic Events CRM'
admin.sites.AdminSite.index_title = 'Items'

router = routers.SimpleRouter()
router.register("clients", ClientViewset, basename="clients")
router.register("contracts", ContractViewset, basename="contracts")
router.register("events", EventViewset, basename="events")
router.register("users", UserViewset, basename="user")

urlpatterns = [
    path("admin/login/", MyLoginView.as_view(),
         {'template_name': 'admin/login.html'}, name="admin_login"),
    path("admin/", admin.site.urls),
    path("crm/token/refresh/", TokenRefreshView.as_view(),
         name="token_refresh"),
    path("crm/", include(router.urls)),
    path("crm/login/", TokenObtainPairView.as_view(), name="login"),
]
