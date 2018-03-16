from django.conf.urls import url

from .viewsets import CutOutViewSet


urlpatterns = [
    url(r'^api/(?P<resource>.+)/$', CutOutViewSet.as_view(), name='cutout'),
]
