from django.conf.urls import url, include

from rest_framework import routers

from .views import ManagementView, DatabaseView, TableView
from .viewsets import (
    DatabaseViewSet,
    TableViewSet,
    ColumnViewSet,
    FunctionViewSet,
    TableTypeViewSet,
    LicenseViewSet,
    AccessLevelViewSet
)

router = routers.DefaultRouter()
router.register(r'databases', DatabaseViewSet, base_name='database')
router.register(r'tables', TableViewSet, base_name='table')
router.register(r'columns', ColumnViewSet, base_name='column')
router.register(r'functions', FunctionViewSet, base_name='function')
router.register(r'tabletypes', TableTypeViewSet, base_name='tabletype')
router.register(r'licenses', LicenseViewSet, base_name='license')
router.register(r'accesslevels', AccessLevelViewSet, base_name='accesslevel')

urlpatterns = [
    url(r'^api/', include(router.urls)),

    url(r'^management/$', ManagementView.as_view(), name='management'),

    url(r'^(?P<database_name>\w+)/$', DatabaseView.as_view(), name='database'),
    url(r'^(?P<database_name>\w+)/(?P<table_name>\w+)/$', TableView.as_view(), name='table'),
]
