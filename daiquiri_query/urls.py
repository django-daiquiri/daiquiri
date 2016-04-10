from django.conf.urls import url, include

from rest_framework import routers

from .views import query, QueryJobViewSet

router = routers.DefaultRouter()
router.register(r'jobs', QueryJobViewSet)

urlpatterns = [
    url(r'^$', query, name='query1'),

    # rest api
    url(r'^api/', include(router.urls, namespace='query')),
]
