from django.conf.urls import url, include

from rest_framework import routers

from .views import table, reference
from .viewsets import RowViewSet, ColumnViewSet

router = routers.DefaultRouter()
router.register(r'rows', RowViewSet, base_name='row')
router.register(r'columns', ColumnViewSet, base_name='column')


urlpatterns = [
    url(r'^table/(?P<schema_name>[A-Za-z0-9_]+)/(?P<table_name>[A-Za-z0-9_]+)/$', table, name='table'),
    url(r'^references/(?P<key>[-\w]+)/(?P<value>.+)/$', reference, name='reference'),

    # rest api
    url(r'^api/', include(router.urls)),
]
