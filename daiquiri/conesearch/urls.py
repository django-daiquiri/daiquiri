from django.urls import re_path

from .viewsets import ConeSearchView

app_name = 'conesearch'

urlpatterns = [
    re_path(r'^api/(?P<resource>.+)/$', ConeSearchView.as_view(), name='search'),
]
