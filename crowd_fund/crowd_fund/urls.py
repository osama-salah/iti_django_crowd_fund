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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from crowd_fund import settings
from crowd_fund.views import render_home
from crowd_fund_app.crowd_fund_app.views import FacebookLogin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dj-rest-auth/facebook/', FacebookLogin.as_view(), name='fb_login'),
    # path('/dj-rest-auth/token/verify/', ),
    path('projects/', include('projects.urls')),
    path('user/', include('crowd_fund_app.urls')),
    path('image/', include('images.urls')),
    path('', render_home, name='home'),
    # path('', TemplateView.as_view(template_name='home.html'), name='home'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
