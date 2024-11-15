from django.urls import re_path

from .viewsets import CutOutViewSet

app_name = 'cutout'

urlpatterns = [
    re_path(r'^api/(?P<resource>.+)/$', CutOutViewSet.as_view(), name='cutout'),
]
