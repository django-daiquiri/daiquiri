from django.conf.urls import url, include

from rest_framework import routers

from .views import file
from .viewsets import FileViewSet

router = routers.DefaultRouter()
router.register(r'files', FileViewSet, base_name='file')

urlpatterns = [
    # rest api
    url(r'^api/', include(router.urls)),
    url(r'^(?P<file_path>.+)$', file, name='file'),
]
