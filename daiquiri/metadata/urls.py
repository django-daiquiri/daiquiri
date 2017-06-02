from django.conf.urls import url, include

from rest_framework import routers

from .views import database, table, management
from .viewsets import (
    DatabaseViewSet,
    TableViewSet,
    ColumnViewSet,
    FunctionViewSet,
    TableTypeViewSet
)

router = routers.DefaultRouter()
router.register(r'databases', DatabaseViewSet, base_name='database')
router.register(r'tables', TableViewSet, base_name='table')
router.register(r'columns', ColumnViewSet, base_name='column')
router.register(r'functions', FunctionViewSet, base_name='function')
router.register(r'tabletypes', TableTypeViewSet, base_name='tabletype')

urlpatterns = [
    url(r'^api/', include(router.urls, namespace='metadata')),

    url(r'^management/$', management, name='metadata_management'),

    url(r'^(?P<database_name>\w+)/$', database, name='metadata_database'),
    url(r'^(?P<database_name>\w+)/(?P<table_name>\w+)/$', table, name='metadata_table'),
]
