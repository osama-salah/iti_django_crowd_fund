"""crowd_fund URL Configuration

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
from allauth.account import views
from allauth.account.views import ConfirmEmailView
from dj_rest_auth.registration.views import VerifyEmailView
from django.contrib import admin
from django.urls import path, include, re_path

from crowd_fund_app.crowd_fund_app.views import FacebookLogin, user_password_reset, CustomPasswordResetView, \
    CustomPasswordResetConfirmView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dj-rest-auth/facebook/', FacebookLogin.as_view(), name='fb_login'),
    # path('/dj-rest-auth/token/verify/', ),
    path('user/', include('crowd_fund_app.urls')),
]
