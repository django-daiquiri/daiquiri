from django.conf.urls import url

from .views import ConeSearchView


urlpatterns = [
    url(r'^(?P<resource>.+)/$', ConeSearchView.as_view(), name='search'),
]
