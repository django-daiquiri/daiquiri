from django.urls import include, path, re_path

from rest_framework import routers

from .views import table, reference
from .viewsets import RowViewSet, ColumnViewSet


app_name = 'serve'

router = routers.DefaultRouter()
router.register(r'rows', RowViewSet, base_name='row')
router.register(r'columns', ColumnViewSet, base_name='column')

urlpatterns = [
    re_path('^table/(?P<schema_name>[A-Za-z0-9_]+)/(?P<table_name>[A-Za-z0-9_]+)/$', table, name='table'),
    re_path('^references/(?P<key>[-\w]+)/(?P<value>.+)/$', reference, name='reference'),

    # rest api
    path('api/', include(router.urls)),
]
