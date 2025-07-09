"""
URL configuration for settings project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib import admin
from django.http import HttpResponse
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import (
    RequestCodeView,
    VerifyCodeView,
    UserProfileView,
    ActivateInviteCodeView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="Referral API",
        default_version='v1',
        description="Simple referral system",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[],
)

urlpatterns = [
     path("", lambda request: HttpResponse("Главная страница  !")),
    path(route="admin/", view=admin.site.urls),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path("auth/request_code/", RequestCodeView.as_view()),
    path("auth/verify_code/", VerifyCodeView.as_view()),
    path("profile/", UserProfileView.as_view()),
    path("activate_invite/", ActivateInviteCodeView.as_view()),
    path(route="auth/token/refresh/",
         view=TokenRefreshView.as_view(), name="token_refresh"
    ),
]