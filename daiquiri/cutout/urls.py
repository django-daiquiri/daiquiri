from django.conf.urls import url

from .views import CutOutViewSet


urlpatterns = [
    url(r'^(?P<resource>.+)/$', CutOutViewSet.as_view(), name='cutout'),
]
