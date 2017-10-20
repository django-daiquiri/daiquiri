from django.conf.urls import url, include

from rest_framework import routers

from .views import CutoutView
from .viewsets import CutoutViewSet

router = routers.DefaultRouter()
router.register(r'cutout', CutoutViewSet, base_name='cutout')

urlpatterns = [
    url(r'^$', CutoutView.as_view(), name='cutout'),

    # rest api
    url(r'^api/', include(router.urls)),
]
