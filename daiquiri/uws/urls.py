from django.conf.urls import url, include

from .routers import UWSRouter
from .viewsets import QueryJobViewSet

router = UWSRouter(trailing_slash=False)
router.register(r'query', QueryJobViewSet, base_name='uwsquery')

urlpatterns = [
    url(r'', include(router.urls)),
]
