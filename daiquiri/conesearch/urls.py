from django.conf.urls import url, include

from rest_framework import routers

from .viewsets import SearchViewSet

router = routers.DefaultRouter()
router.register(r'search', SearchViewSet, base_name='search')

urlpatterns = [
    # rest api
    url(r'^', include(router.urls)),
]
