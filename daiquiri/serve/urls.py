from django.urls import include, path, re_path

from rest_framework import routers

from .views import reference, table
from .viewsets import ColumnViewSet, RowViewSet

app_name = 'serve'

router = routers.DefaultRouter()
router.register(r'rows', RowViewSet, basename='row')
router.register(r'columns', ColumnViewSet, basename='column')

urlpatterns = [
    re_path(r'^table/(?P<schema_name>[A-Za-z0-9_]+)/(?P<table_name>[A-Za-z0-9_]+)/$', table, name='table'),
    re_path(r'^references/(?P<key>[-\w]+)/(?P<value>.+)/$', reference, name='reference'),

    # rest api
    path('api/', include(router.urls)),
]
