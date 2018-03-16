from django.conf.urls import url

from .viewsets import ConeSearchView


urlpatterns = [
    url(r'^api/(?P<resource>.+)/$', ConeSearchView.as_view(), name='search'),
]
