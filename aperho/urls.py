"""aperho URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles import views
import django.contrib.auth.views

from . import home

urlpatterns = [
    url(r'^$', home.index, name='home'),
    url(r'^login/$',django.contrib.auth.views.LoginView.as_view(), name='login'),
    url(r'^logout/$',django.contrib.auth.views.LogoutView.as_view(next_page='/login'), name='logout'),
    url(r'^admin/', admin.site.urls),
    url(r'^votes/', include('votes.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', views.serve),
    ]
