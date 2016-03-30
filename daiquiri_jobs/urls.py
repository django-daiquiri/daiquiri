from django.conf.urls import url, include

from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register(r'jobs', JobsViewSet)

urlpatterns = [
    url(r'', include(router.urls)),
]
