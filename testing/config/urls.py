from django.conf.urls import include, url
from django.contrib import admin

from daiquiri_core.views import home

urlpatterns = [
    url(r'^$', home, name='home'),
]
