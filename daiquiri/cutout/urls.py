from django.conf.urls import url, include

from rest_framework import routers

from .views import DatacubeView
from .viewsets import DatacubeViewSet

router = routers.DefaultRouter()
router.register(r'datacubes', DatacubeViewSet, base_name='datacube')

urlpatterns = [
    url(r'^datacube/$', DatacubeView.as_view(), name='datacube'),

    # rest api
    url(r'^api/', include(router.urls)),
]
